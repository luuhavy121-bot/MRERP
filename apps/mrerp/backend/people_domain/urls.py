from rest_framework.routers import DefaultRouter

from .views import EmployeeViewSet, TeamViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("teams", TeamViewSet, basename="team")

urlpatterns = router.urls
