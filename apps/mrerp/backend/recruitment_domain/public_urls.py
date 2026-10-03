from rest_framework.routers import DefaultRouter
from .public import PublicOpeningViewSet
router = DefaultRouter()
router.register("openings", PublicOpeningViewSet, basename="public-opening")
urlpatterns = router.urls
