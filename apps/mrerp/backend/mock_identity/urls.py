from django.urls import path

from .views import DebugSwitchView, LoginView, LogoutView, SessionView

urlpatterns = [
    path("session/", SessionView.as_view(), name="session"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("debug/switch/", DebugSwitchView.as_view(), name="debug-switch"),
]
