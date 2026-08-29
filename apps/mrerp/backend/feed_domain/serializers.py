from rest_framework import serializers

from .models import Comment, CommentReaction, Post, PostAttachment, PostReaction, ReactionKind


class AttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    def get_download_url(self, attachment) -> str:
        return f"/api/v1/feed/attachments/{attachment.pk}/download/"

    class Meta:
        model = PostAttachment
        fields = ["uuid", "original_name", "content_type", "size", "download_url"]


class ReactionSummaryMixin:
    def get_reaction_summary(self, instance) -> dict:
        summary = {value: 0 for value, _ in ReactionKind.choices}
        actor_id = getattr(getattr(self.context.get("request"), "user", None), "employee_profile", None)
        actor_id = getattr(actor_id, "pk", None)
        my_reaction = None
        for reaction in instance.reactions.all():
            summary[reaction.kind] += 1
            if reaction.actor_id == actor_id:
                my_reaction = reaction.kind
        return {"counts": summary, "mine": my_reaction}


class CommentSerializer(ReactionSummaryMixin, serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    author_code = serializers.CharField(source="author.employee_code", read_only=True)
    reaction_summary = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    def get_content(self, comment) -> str:
        return "Bình luận đã bị xóa" if comment.deleted_at else comment.content

    def get_replies(self, comment) -> list[dict]:
        if comment.parent_id:
            return []
        return CommentSerializer(comment.replies.all(), many=True, context=self.context).data

    def get_can_delete(self, comment) -> bool:
        request = self.context.get("request")
        return bool(request and (comment.author_id == request.user.employee_profile.pk or request.user.has_perm("feed_domain.moderate_post")))

    class Meta:
        model = Comment
        fields = ["uuid", "author_name", "author_code", "parent", "content", "deleted_at", "deletion_mode", "reaction_summary", "replies", "can_delete", "created_at"]


class OriginalPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    available = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_available(self, post) -> bool:
        return post.deleted_at is None

    def get_content(self, post) -> str:
        return post.content if post.deleted_at is None else "Nội dung gốc không còn khả dụng"

    class Meta:
        model = Post
        fields = ["uuid", "author_name", "content", "available", "created_at"]


class PostCompactSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    attachment_count = serializers.IntegerField(source="attachments.count", read_only=True)

    class Meta:
        model = Post
        fields = ["uuid", "author_name", "content", "is_official", "attachment_count", "created_at"]


class PostSerializer(ReactionSummaryMixin, serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.display_name", read_only=True)
    author_code = serializers.CharField(source="author.employee_code", read_only=True)
    audience_employee_names = serializers.SlugRelatedField(source="audience_employees", slug_field="display_name", many=True, read_only=True)
    audience_team_names = serializers.SlugRelatedField(source="audience_teams", slug_field="name", many=True, read_only=True)
    attachments = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    reaction_summary = serializers.SerializerMethodField()
    shared_post = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    def get_attachments(self, post) -> list[dict]:
        if post.deleted_at:
            return []
        return AttachmentSerializer(post.attachments.filter(deleted_at__isnull=True), many=True).data

    def get_comments(self, post) -> list[dict]:
        roots = post.comments.filter(parent__isnull=True).prefetch_related("replies__author", "replies__reactions")
        return CommentSerializer(roots, many=True, context=self.context).data

    def get_shared_post(self, post) -> dict | None:
        return OriginalPostSerializer(post.shared_from).data if post.shared_from_id else None

    def get_can_delete(self, post) -> bool:
        request = self.context.get("request")
        return bool(request and (post.author_id == request.user.employee_profile.pk or request.user.has_perm("feed_domain.moderate_post")))

    class Meta:
        model = Post
        fields = ["uuid", "author", "author_name", "author_code", "content", "company_scope", "audience_employees", "audience_employee_names", "audience_teams", "audience_team_names", "is_official", "shared_post", "attachments", "comments", "reaction_summary", "deleted_at", "deletion_mode", "can_delete", "created_at"]


class PostCreateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True, max_length=12000)
    company_scope = serializers.BooleanField(default=False)
    employee_uuids = serializers.JSONField(binary=True, default=list)
    team_uuids = serializers.JSONField(binary=True, default=list)
    is_official = serializers.BooleanField(default=False)

    def validate_employee_uuids(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Danh sách Employee không hợp lệ.")
        return value

    def validate_team_uuids(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Danh sách Team không hợp lệ.")
        return value


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=4000)
    parent_uuid = serializers.UUIDField(required=False, allow_null=True)


class ReactionSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=ReactionKind.choices)


class ShareSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True, max_length=12000)
    company_scope = serializers.BooleanField(default=False)
    employee_uuids = serializers.ListField(child=serializers.UUIDField(), default=list)
    team_uuids = serializers.ListField(child=serializers.UUIDField(), default=list)
