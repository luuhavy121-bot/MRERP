from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register("requests", LeaveRequestViewSet, basename="leave-request")
router.register("attendance", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls
