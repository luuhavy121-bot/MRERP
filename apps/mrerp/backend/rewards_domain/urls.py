from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeaderboardView, MyStarBalanceView, RecognitionViewSet, RewardAudienceView, StarGrantView

router = DefaultRouter()
router.register("recognitions", RecognitionViewSet, basename="recognition")

urlpatterns = [
    path("", include(router.urls)),
    path("audience-options/", RewardAudienceView.as_view(), name="reward-audience-options"),
    path("stars/grant/", StarGrantView.as_view(), name="star-grant"),
    path("stars/me/", MyStarBalanceView.as_view(), name="my-star-balance"),
    path("leaderboard/", LeaderboardView.as_view(), name="star-leaderboard"),
]
