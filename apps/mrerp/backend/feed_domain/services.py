from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from config.file_storage import MAX_FILES_PER_PARENT, delete_stored_file, save_upload
from dashboard_domain.models import Notification
from dashboard_domain.services import notify, notify_many
from people_domain.models import Employee, Team
from people_domain.services import audit

from .access import can_moderate
from .models import Comment, CommentReaction, Post, PostAttachment, PostReaction


def _audience_recipients(post):
    if post.company_scope:
        return Employee.objects.none()
    return Employee.objects.filter(
        models_q_direct_or_team(post)
    ).exclude(pk=post.author_id).distinct()


def models_q_direct_or_team(post):
    from django.db.models import Q

    query = Q(direct_feed_posts=post)
    team_ids = list(post.audience_teams.values_list("pk", flat=True))
    if team_ids:
        query |= Q(team_id__in=team_ids)
    return query


def create_post(*, actor, content: str, company_scope: bool, employee_uuids: list, team_uuids: list, is_official: bool, uploads=(), shared_from=None):
    actor_employee = actor.employee_profile
    if company_scope and (employee_uuids or team_uuids):
        raise ValidationError({"audience": "Phạm vi toàn công ty không kết hợp với người hoặc Team."})
    if not company_scope and not employee_uuids and not team_uuids:
        raise ValidationError({"audience": "Hãy chọn ít nhất một người, Team hoặc toàn công ty."})
    if is_official and (not company_scope or not actor.has_perm("feed_domain.publish_official_post")):
        raise PermissionDenied("Chỉ HR/CEO được đăng thông báo chính thức toàn công ty.")
    if not content.strip() and not uploads and shared_from is None:
        raise ValidationError({"content": "Bài viết cần có nội dung hoặc file đính kèm."})
    if len(uploads) > MAX_FILES_PER_PARENT:
        raise ValidationError({"attachments": "Mỗi bài viết tối đa 5 file."})
    employees = list(Employee.objects.filter(pk__in=employee_uuids))
    teams = list(Team.objects.filter(pk__in=team_uuids, is_active=True))
    if len(employees) != len(set(employee_uuids)) or len(teams) != len(set(team_uuids)):
        raise ValidationError({"audience": "Audience chứa Employee hoặc Team không hợp lệ."})
    stored = []
    try:
        with transaction.atomic():
            post = Post.objects.create(
                author=actor_employee,
                content=content.strip(),
                company_scope=company_scope,
                is_official=is_official,
                shared_from=shared_from,
            )
            post.audience_employees.set(employees)
            post.audience_teams.set(teams)
            for uploaded_file in uploads:
                metadata = save_upload(uploaded_file, "feed")
                stored.append(metadata["storage_key"])
                PostAttachment.objects.create(post=post, **metadata)
            audit(actor=actor, action="feed.post.created", target=post, changes={"company_scope": company_scope, "employee_count": len(employees), "team_count": len(teams), "official": is_official, "attachment_count": len(uploads), "shared": bool(shared_from)})
        if not company_scope:
            notify_many(
                recipients=_audience_recipients(post),
                kind=Notification.Kind.FEED,
                title=f"{actor_employee.display_name or actor_employee.employee_code} đã chia sẻ với bạn",
                body=post.content[:180] or "Bài viết có file đính kèm",
                target_type="post",
                target_uuid=post.pk,
                key_prefix=f"feed-post:{post.pk}",
            )
        return post
    except Exception:
        for storage_key in stored:
            delete_stored_file(storage_key)
        raise


def _validate_share_subset(original: Post, *, company_scope: bool, employee_uuids: list, team_uuids: list):
    if original.company_scope:
        return
    if company_scope:
        raise ValidationError({"audience": "Không thể share ra phạm vi toàn công ty."})
    original_team_ids = set(str(value) for value in original.audience_teams.values_list("pk", flat=True))
    requested_team_ids = set(str(value) for value in team_uuids)
    if not requested_team_ids.issubset(original_team_ids):
        raise ValidationError({"audience": "Team nhận share phải nằm trong audience gốc."})
    direct_ids = set(str(value) for value in original.audience_employees.values_list("pk", flat=True))
    team_member_ids = set(str(value) for value in Employee.objects.filter(team_id__in=original_team_ids).values_list("pk", flat=True))
    if not set(str(value) for value in employee_uuids).issubset(direct_ids | team_member_ids):
        raise ValidationError({"audience": "Người nhận share phải nằm trong audience gốc."})


def share_post(*, actor, original: Post, content: str, company_scope: bool, employee_uuids: list, team_uuids: list):
    canonical = original.shared_from or original
    if canonical.deleted_at:
        raise ValidationError({"post": "Nội dung gốc không còn khả dụng."})
    _validate_share_subset(canonical, company_scope=company_scope, employee_uuids=employee_uuids, team_uuids=team_uuids)
    post = create_post(actor=actor, content=content, company_scope=company_scope, employee_uuids=employee_uuids, team_uuids=team_uuids, is_official=False, shared_from=canonical)
    if canonical.author_id != actor.employee_profile.pk:
        notify(recipient=canonical.author, kind=Notification.Kind.FEED, title="Bài viết của bạn vừa được chia sẻ", body=content[:180], target_type="post", target_uuid=post.pk, deduplication_key=f"feed-share:{post.pk}:{canonical.author_id}")
    return post


def add_comment(*, actor, post: Post, content: str, parent=None):
    if post.deleted_at:
        raise ValidationError({"post": "Bài viết đã bị xóa."})
    if parent and (parent.post_id != post.pk or parent.parent_id):
        raise ValidationError({"parent_uuid": "Bình luận chỉ hỗ trợ một cấp trả lời."})
    comment = Comment.objects.create(post=post, author=actor.employee_profile, parent=parent, content=content.strip())
    audit(actor=actor, action="feed.comment.created", target=comment, changes={"post": str(post.pk), "reply": bool(parent)})
    recipient = parent.author if parent else post.author
    if recipient.pk != actor.employee_profile.pk:
        notify(recipient=recipient, kind=Notification.Kind.FEED, title="Có phản hồi mới trên Bảng tin", body=comment.content[:180], target_type="post", target_uuid=post.pk, deduplication_key=f"feed-comment:{comment.pk}:{recipient.pk}")
    return comment


def soft_delete(*, actor, instance):
    own_content = instance.author_id == actor.employee_profile.pk
    if not own_content and not can_moderate(actor):
        raise PermissionDenied("Bạn chỉ được xóa nội dung của mình.")
    if instance.deleted_at:
        return instance
    instance.deleted_at = timezone.now()
    instance.deleted_by = actor
    instance.deletion_mode = "author" if own_content else "moderation"
    instance.save(update_fields=["deleted_at", "deleted_by", "deletion_mode", "updated_at"])
    if isinstance(instance, Post):
        instance.attachments.filter(deleted_at__isnull=True).update(deleted_at=instance.deleted_at)
    audit(actor=actor, action=f"feed.{instance.__class__.__name__.lower()}.deleted", target=instance, changes={"mode": instance.deletion_mode})
    return instance


def set_reaction(*, actor, target, kind: str):
    model = PostReaction if isinstance(target, Post) else CommentReaction
    lookup = {"post": target} if isinstance(target, Post) else {"comment": target}
    reaction, _ = model.objects.update_or_create(actor=actor.employee_profile, **lookup, defaults={"kind": kind})
    if target.author_id != actor.employee_profile.pk:
        post = target if isinstance(target, Post) else target.post
        notify(recipient=target.author, kind=Notification.Kind.FEED, title="Có cảm xúc mới trên nội dung của bạn", body=kind, target_type="post", target_uuid=post.pk, deduplication_key=f"feed-reaction:{target.__class__.__name__}:{target.pk}:{actor.employee_profile.pk}")
    return reaction
