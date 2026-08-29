from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/auth/", include("mock_identity.urls")),
    path("api/v1/people/", include("people_domain.urls")),
    path("api/v1/leave/", include("leave_domain.urls")),
    path("api/v1/dashboard/", include("dashboard_domain.urls")),
    path("api/v1/feed/", include("feed_domain.urls")),
    path("api/v1/tasks/", include("task_domain.urls")),
    path("api/v1/settings/", include("preferences_domain.urls")),
    path("api/v1/recruitment/", include("recruitment_domain.urls")),
    path("api/v1/documents/", include("documents_domain.urls")),
    path("api/v1/rewards/", include("rewards_domain.urls")),
]
