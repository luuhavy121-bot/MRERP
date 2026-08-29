from django.urls import path

from .views import DashboardView, NotificationReadAllView, NotificationReadView


urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("notifications/<uuid:notification_uuid>/read/", NotificationReadView.as_view(), name="notification-read"),
    path("notifications/read-all/", NotificationReadAllView.as_view(), name="notification-read-all"),
]
