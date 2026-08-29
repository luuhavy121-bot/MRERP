from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DocumentAudienceOptionsView, DocumentFileDownloadView, DocumentViewSet

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="document")

urlpatterns = [
    path("audience-options/", DocumentAudienceOptionsView.as_view(), name="document-audience-options"),
    path("", include(router.urls)),
    path("files/<uuid:file_uuid>/download/", DocumentFileDownloadView.as_view(), name="document-file-download"),
]
