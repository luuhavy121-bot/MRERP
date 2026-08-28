from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, EmployeeViewSet, TeamViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("departments", DepartmentViewSet, basename="department")
router.register("teams", TeamViewSet, basename="team")

urlpatterns = router.urls
