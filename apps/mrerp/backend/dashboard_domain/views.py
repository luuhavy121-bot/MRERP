from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from people_domain.access import get_actor_employee
from people_domain.serializers import ApiErrorSerializer

from .models import Notification
from .serializers import DashboardSerializer, NotificationSerializer


GUIDES = [
    {"id": "profile", "title": "Hoàn thiện hồ sơ cá nhân", "body": "Kiểm tra họ tên, ngày sinh và địa chỉ trong Hồ sơ của tôi.", "target": "profile"},
    {"id": "security", "title": "Bảo vệ tài khoản", "body": "Không chia sẻ mật khẩu tạm thời và đổi mật khẩu ngay khi được yêu cầu.", "target": "profile"},
    {"id": "scope", "title": "Chọn đúng phạm vi chia sẻ", "body": "Kiểm tra người hoặc Team nhận trước khi đăng nội dung nội bộ.", "target": "feed"},
]


class DashboardView(APIView):
    @extend_schema(responses={200: DashboardSerializer, 403: ApiErrorSerializer})
    def get(self, request):
        actor = get_actor_employee(request.user)
        from feed_domain.models import Post
        from feed_domain.serializers import PostCompactSerializer

        company_posts = Post.objects.filter(company_scope=True, deleted_at__isnull=True).select_related("author").prefetch_related("attachments")[:8]
        notifications = Notification.objects.filter(recipient=actor)[:30]
        unread_count = Notification.objects.filter(recipient=actor, read_at__isnull=True).count()
        warnings = []
        account_state = getattr(actor, "account_state", None)
        if account_state and account_state.must_change_password:
            warnings.append({"id": "change-password", "title": "Bạn cần đổi mật khẩu", "body": "Mật khẩu hiện tại là mật khẩu tạm thời.", "target": "profile"})
        return Response({
            "general": {"guides": GUIDES, "company_posts": PostCompactSerializer(company_posts, many=True, context={"request": request}).data},
            "private": {"notifications": NotificationSerializer(notifications, many=True).data, "unread_count": unread_count, "warnings": warnings},
        })


class NotificationReadView(APIView):
    @extend_schema(request=None, responses={204: None, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def post(self, request, notification_uuid):
        actor = get_actor_employee(request.user)
        notification = Notification.objects.filter(pk=notification_uuid, recipient=actor).first()
        if notification is None:
            return Response({"detail": "Không tìm thấy thông báo trong scope."}, status=status.HTTP_404_NOT_FOUND)
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationReadAllView(APIView):
    @extend_schema(request=None, responses={204: None, 403: ApiErrorSerializer})
    def post(self, request):
        actor = get_actor_employee(request.user)
        Notification.objects.filter(recipient=actor, read_at__isnull=True).update(read_at=timezone.now())
        return Response(status=status.HTTP_204_NO_CONTENT)
