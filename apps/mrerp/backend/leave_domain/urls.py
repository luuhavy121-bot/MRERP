from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, LeaveRequestViewSet
from .actual_attendance import ActualAttendanceViewSet, AttendanceImportViewSet

router = DefaultRouter()
router.register("requests", LeaveRequestViewSet, basename="leave-request")
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("actual-attendance", ActualAttendanceViewSet, basename="actual-attendance")
router.register("attendance-imports", AttendanceImportViewSet, basename="attendance-import")

urlpatterns = router.urls
