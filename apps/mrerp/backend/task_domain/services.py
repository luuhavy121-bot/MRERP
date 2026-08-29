import calendar
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from config.file_storage import MAX_FILES_PER_PARENT, delete_stored_file, save_upload
from dashboard_domain.models import Notification
from dashboard_domain.services import notify, notify_many
from people_domain.models import Employee, TeamLeadership
from people_domain.services import audit

from .access import led_team_ids, manages_team
from .models import Goal, Recurrence, Task, TaskAttachment


def validate_goal_task(goal, *, team_id, due_at):
    if goal is None:
        return
    if not goal.is_active:
        raise ValidationError({"goal_uuid": "Mục tiêu không còn hoạt động."})
    if goal.scope == Goal.Scope.TEAM and goal.team_id != team_id:
        raise ValidationError({"goal_uuid": "Task phải cùng Team với mục tiêu."})
    due_date = timezone.localtime(due_at).date()
    if due_date < goal.starts_on or due_date > goal.ends_on:
        raise ValidationError({"goal_uuid": "Deadline Task phải nằm trong timebox của mục tiêu."})


def validate_assignment(actor, assignee: Employee):
    actor_employee = actor.employee_profile
    if actor.has_perm("task_domain.view_company_tasks"):
        if assignee.pk == actor_employee.pk:
            raise ValidationError({"assignee_uuid": "CEO không tạo self-task."})
        return
    led = TeamLeadership.objects.filter(leader=actor_employee, team_id=assignee.team_id).exists() if assignee.team_id else False
    if led:
        return
    if assignee.pk != actor_employee.pk:
        raise PermissionDenied("Bạn chỉ được tự giao hoặc giao cho thành viên Team mình lãnh đạo.")


def create_task(*, actor, title: str, description: str, assignee: Employee, due_at, goal=None, recurrence=None, scheduled_for=None):
    validate_assignment(actor, assignee)
    if not assignee.team_id:
        raise ValidationError({"assignee_uuid": "Người nhận Task phải thuộc một Team."})
    validate_goal_task(goal, team_id=assignee.team_id, due_at=due_at)
    with transaction.atomic():
        task = Task.objects.create(
            title=title.strip(),
            description=description.strip(),
            creator=actor.employee_profile,
            assignee=assignee,
            team_id=assignee.team_id,
            due_at=due_at,
            goal=goal,
            recurrence=recurrence,
            scheduled_for=scheduled_for,
        )
        audit(actor=actor, action="task.created", target=task, changes={"assignee": str(assignee.pk), "team": str(assignee.team_id), "due_at": due_at.isoformat(), "recurring": bool(recurrence)})
    if assignee.pk != actor.employee_profile.pk:
        notify(recipient=assignee, kind=Notification.Kind.TASK, title="Bạn có công việc mới", body=task.title, target_type="task", target_uuid=task.pk, deduplication_key=f"task-assigned:{task.pk}:{assignee.pk}")
    return task


def update_task(*, actor, task: Task, validated_data: dict):
    actor_employee = actor.employee_profile
    with transaction.atomic():
        locked = Task.objects.select_for_update().get(pk=task.pk)
        changed = {}
        if "progress" in validated_data and locked.assignee_id != actor_employee.pk:
            raise PermissionDenied("Chỉ người được giao cập nhật tiến độ.")
        if set(validated_data) == {"progress"}:
            if locked.assignee_id != actor_employee.pk or locked.status not in {Task.Status.IN_PROGRESS, Task.Status.REWORK}:
                raise PermissionDenied("Chỉ người được giao cập nhật tiến độ khi Task đang thực hiện.")
        else:
            if locked.creator_id != actor_employee.pk and not manages_team(actor, locked.team_id):
                raise PermissionDenied("Bạn không có scope sửa nội dung Task.")
            if locked.status == Task.Status.COMPLETED:
                raise ValidationError({"status": "Không sửa Task đã hoàn thành."})
        for field, value in validated_data.items():
            old = getattr(locked, field)
            if old != value:
                setattr(locked, field, value)
                changed[field] = {"from": str(old), "to": str(value)}
        if "due_at" in validated_data or "goal" in validated_data:
            validate_goal_task(locked.goal, team_id=locked.team_id, due_at=locked.due_at)
        if changed:
            locked.version += 1
            locked.save(update_fields=[*validated_data.keys(), "version", "updated_at"])
            audit(actor=actor, action="task.updated", target=locked, changes=changed)
        return locked


def transition_task(*, actor, task: Task, action: str, note: str):
    actor_employee = actor.employee_profile
    with transaction.atomic():
        locked = Task.objects.select_for_update().get(pk=task.pk)
        previous = locked.status
        if action == "submit":
            if locked.assignee_id != actor_employee.pk or locked.status not in {Task.Status.IN_PROGRESS, Task.Status.REWORK}:
                raise PermissionDenied("Chỉ người được giao mới có thể gửi xác nhận.")
            locked.status = Task.Status.PENDING_REVIEW
        elif action in {"accept", "rework"}:
            if not actor.has_perm("task_domain.accept_task") or not manages_team(actor, locked.team_id):
                raise PermissionDenied("Bạn không có capability xác nhận Task trong scope này.")
            if locked.assignee_id == actor_employee.pk:
                raise PermissionDenied("Không được tự xác nhận Task của chính mình.")
            if locked.status != Task.Status.PENDING_REVIEW:
                raise ValidationError({"status": "Task chưa ở trạng thái Chờ xác nhận."})
            if action == "rework" and not note.strip():
                raise ValidationError({"note": "Cần ghi rõ lý do làm lại."})
            locked.status = Task.Status.COMPLETED if action == "accept" else Task.Status.REWORK
            locked.progress = 100 if action == "accept" else locked.progress
            locked.review_note = note.strip()
            locked.accepted_by = actor_employee if action == "accept" else None
            locked.accepted_at = timezone.now() if action == "accept" else None
        else:
            raise ValidationError({"action": "Transition không hợp lệ."})
        locked.version += 1
        locked.save(update_fields=["status", "progress", "review_note", "accepted_by", "accepted_at", "version", "updated_at"])
        audit(actor=actor, action=f"task.transition.{action}", target=locked, changes={"from": previous, "to": locked.status, "note": "provided" if note else "empty"})
    if locked.assignee_id != actor_employee.pk:
        notify(recipient=locked.assignee, kind=Notification.Kind.TASK, title="Trạng thái công việc đã thay đổi", body=f"{locked.title} · {locked.get_status_display()}", target_type="task", target_uuid=locked.pk)
    if action == "submit" and locked.creator_id != actor_employee.pk:
        notify(recipient=locked.creator, kind=Notification.Kind.TASK, title="Công việc chờ xác nhận", body=locked.title, target_type="task", target_uuid=locked.pk, deduplication_key=f"task-review:{locked.pk}:{locked.version}")
    return locked


def create_goal(*, actor, title, description, scope, team, period, starts_on, ends_on):
    if scope == Goal.Scope.COMPANY:
        if not actor.has_perm("task_domain.manage_company_goals"):
            raise PermissionDenied("Chỉ CEO quản lý mục tiêu công ty.")
        team = None
    else:
        if team is None:
            raise ValidationError({"team_uuid": "Mục tiêu Team cần chọn Team."})
        if not actor.has_perm("task_domain.manage_goals") or not manages_team(actor, team.pk):
            raise PermissionDenied("Bạn không quản lý mục tiêu của Team này.")
    goal = Goal.objects.create(title=title.strip(), description=description.strip(), scope=scope, team=team, period=period, starts_on=starts_on, ends_on=ends_on, created_by=actor.employee_profile)
    audit(actor=actor, action="goal.created", target=goal, changes={"scope": scope, "team": str(team.pk) if team else None, "period": period})
    recipients = Employee.objects.all() if scope == Goal.Scope.COMPANY else Employee.objects.filter(team=team)
    notify_many(recipients=recipients.exclude(pk=actor.employee_profile.pk), kind=Notification.Kind.GOAL, title="Có mục tiêu mới", body=goal.title, target_type="goal", target_uuid=goal.pk, key_prefix=f"goal-created:{goal.pk}")
    return goal


def add_task_attachment(*, actor, task: Task, kind: str, uploads):
    active_count = task.attachments.filter(deleted_at__isnull=True).count()
    if active_count + len(uploads) > MAX_FILES_PER_PARENT:
        raise ValidationError({"attachments": "Mỗi Task tối đa 5 file."})
    actor_employee = actor.employee_profile
    if kind == TaskAttachment.Kind.EVIDENCE:
        if task.assignee_id != actor_employee.pk:
            raise PermissionDenied("Chỉ người được giao thêm file kết quả.")
    elif task.creator_id != actor_employee.pk and not manages_team(actor, task.team_id):
        raise PermissionDenied("Chỉ người tạo hoặc quản lý scope thêm file yêu cầu.")
    stored = []
    created = []
    try:
        with transaction.atomic():
            for upload in uploads:
                metadata = save_upload(upload, "tasks")
                stored.append(metadata["storage_key"])
                created.append(TaskAttachment.objects.create(task=task, uploaded_by=actor_employee, kind=kind, **metadata))
            audit(actor=actor, action="task.attachments.added", target=task, changes={"kind": kind, "count": len(created)})
        return created
    except Exception:
        for key in stored:
            delete_stored_file(key)
        raise


def soft_delete_task_attachment(*, actor, attachment: TaskAttachment):
    actor_employee = actor.employee_profile
    if attachment.kind == TaskAttachment.Kind.EVIDENCE:
        allowed = attachment.uploaded_by_id == actor_employee.pk and attachment.task.assignee_id == actor_employee.pk
    else:
        allowed = attachment.uploaded_by_id == actor_employee.pk or manages_team(actor, attachment.task.team_id)
    if not allowed:
        raise PermissionDenied("Bạn không được xóa file này.")
    attachment.deleted_at = timezone.now()
    attachment.save(update_fields=["deleted_at", "updated_at"])
    audit(actor=actor, action="task.attachment.deleted", target=attachment.task, changes={"attachment": str(attachment.pk), "kind": attachment.kind})


def next_schedule(series: Recurrence, current):
    if series.frequency == Recurrence.Frequency.DAILY:
        return current + timedelta(days=series.interval)
    if series.frequency == Recurrence.Frequency.WEEKLY:
        return current + timedelta(weeks=series.interval)
    month_index = current.year * 12 + current.month - 1 + series.interval
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    day = min(series.anchor_day or current.day, calendar.monthrange(year, month)[1])
    return current.replace(year=year, month=month, day=day)


def generate_due_occurrences(series: Recurrence, now=None):
    now = now or timezone.now()
    generated = 0
    with transaction.atomic():
        # Goal is nullable; including it in SELECT ... FOR UPDATE creates an
        # outer join that PostgreSQL cannot lock. Optional relations load lazily.
        locked = Recurrence.objects.select_for_update().select_related("creator", "assignee").get(pk=series.pk)
        while locked.status == Recurrence.Status.ACTIVE and locked.next_occurrence_at <= now:
            scheduled = locked.next_occurrence_at
            if locked.end_date and timezone.localtime(scheduled).date() > locked.end_date:
                locked.status = Recurrence.Status.STOPPED
                break
            due_at = scheduled + timedelta(minutes=locked.deadline_offset_minutes)
            if locked.goal_id and timezone.localtime(due_at).date() > locked.goal.ends_on:
                locked.status = Recurrence.Status.STOPPED
                break
            try:
                create_task(actor=locked.creator.identity_user, title=locked.title, description=locked.description, assignee=locked.assignee, due_at=due_at, goal=locked.goal, recurrence=locked, scheduled_for=scheduled)
                generated += 1
            except IntegrityError:
                pass
            locked.next_occurrence_at = next_schedule(locked, scheduled)
        locked.save(update_fields=["next_occurrence_at", "status", "updated_at"])
    return generated
