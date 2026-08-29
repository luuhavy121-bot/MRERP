from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet, CandidateAttachmentDownloadView, HiringRequestViewSet, OpeningViewSet, RecruitmentOptionsView

router = DefaultRouter()
router.register("requests", HiringRequestViewSet, basename="recruitment-request")
router.register("openings", OpeningViewSet, basename="recruitment-opening")
router.register("applications", ApplicationViewSet, basename="recruitment-application")

urlpatterns = [
    path("options/", RecruitmentOptionsView.as_view(), name="recruitment-options"),
    path("", include(router.urls)),
    path("attachments/<uuid:attachment_uuid>/download/", CandidateAttachmentDownloadView.as_view(), name="candidate-attachment-download"),
]
