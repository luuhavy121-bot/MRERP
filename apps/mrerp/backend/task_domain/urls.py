from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GoalViewSet, RecurrenceViewSet, TaskAttachmentDetailView, TaskAttachmentDownloadView, TaskViewSet


router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")
router.register("goals", GoalViewSet, basename="goal")
router.register("recurrences", RecurrenceViewSet, basename="recurrence")

urlpatterns = [
    *router.urls,
    path("attachments/<uuid:attachment_uuid>/", TaskAttachmentDetailView.as_view(), name="task-attachment-detail"),
    path("attachments/<uuid:attachment_uuid>/download/", TaskAttachmentDownloadView.as_view(), name="task-attachment-download"),
]
