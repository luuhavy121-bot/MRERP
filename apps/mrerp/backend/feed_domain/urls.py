from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AttachmentDownloadView, AudienceOptionsView, CommentDetailView, CommentReactionView, PostViewSet


router = DefaultRouter()
router.register("posts", PostViewSet, basename="feed-post")

urlpatterns = [
    *router.urls,
    path("comments/<uuid:comment_uuid>/", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/<uuid:comment_uuid>/reaction/", CommentReactionView.as_view(), name="comment-reaction"),
    path("attachments/<uuid:attachment_uuid>/download/", AttachmentDownloadView.as_view(), name="feed-attachment-download"),
    path("audience-options/", AudienceOptionsView.as_view(), name="feed-audience-options"),
]
