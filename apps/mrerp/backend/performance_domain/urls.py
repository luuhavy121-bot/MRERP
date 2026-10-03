from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, ReviewOptionsView, ReviewContextView
router = DefaultRouter()
router.register("reviews", ReviewViewSet, basename="performance-review")
urlpatterns = [path("options/", ReviewOptionsView.as_view()), path("context/", ReviewContextView.as_view())] + router.urls
