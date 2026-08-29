from rest_framework.routers import DefaultRouter

from .views import AccessViewSet, AuditViewSet, EmployeeViewSet, TeamViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("teams", TeamViewSet, basename="team")
router.register("access", AccessViewSet, basename="access")
router.register("audit", AuditViewSet, basename="audit")

urlpatterns = router.urls
