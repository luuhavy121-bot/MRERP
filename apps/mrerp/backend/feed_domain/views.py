from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from config.file_storage import protected_file_response
from people_domain.access import get_actor_employee
from people_domain.models import Employee, Team
from people_domain.serializers import ApiErrorSerializer
from people_domain.views import require_capability

from .access import visible_posts
from .capabilities import COMMENT, CREATE_POST, REACT, SHARE
from .models import Comment, CommentReaction, Post, PostAttachment, PostReaction
from .serializers import CommentCreateSerializer, CommentSerializer, PostCreateSerializer, PostSerializer, ReactionSerializer, ShareSerializer
from .services import add_comment, create_post, set_reaction, share_post, soft_delete


class PostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Post.objects.none()
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return visible_posts(self.request.user)

    @extend_schema(request=PostCreateSerializer, responses={201: PostSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    def create(self, request):
        require_capability(request.user, CREATE_POST)
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = create_post(actor=request.user, uploads=request.FILES.getlist("attachments"), **serializer.validated_data)
        return Response(PostSerializer(post, context={"request": request}).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        post = self.get_object()
        soft_delete(actor=request.user, instance=post)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=CommentCreateSerializer, responses={201: CommentSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def comments(self, request, pk=None):
        require_capability(request.user, COMMENT)
        post = self.get_object()
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parent_uuid = serializer.validated_data.pop("parent_uuid", None)
        parent = Comment.objects.filter(pk=parent_uuid).first() if parent_uuid else None
        if parent_uuid and parent is None:
            raise Http404
        comment = add_comment(actor=request.user, post=post, parent=parent, **serializer.validated_data)
        return Response(CommentSerializer(comment, context={"request": request}).data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ReactionSerializer, responses={200: ReactionSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["put", "delete"])
    def reaction(self, request, pk=None):
        require_capability(request.user, REACT)
        post = self.get_object()
        if request.method == "DELETE":
            PostReaction.objects.filter(post=post, actor=request.user.employee_profile).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction = set_reaction(actor=request.user, target=post, **serializer.validated_data)
        return Response({"kind": reaction.kind})

    @extend_schema(request=ShareSerializer, responses={201: PostSerializer, 400: ApiErrorSerializer, 403: ApiErrorSerializer})
    @action(detail=True, methods=["post"])
    def share(self, request, pk=None):
        require_capability(request.user, SHARE)
        original = self.get_object()
        serializer = ShareSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = share_post(actor=request.user, original=original, **serializer.validated_data)
        return Response(PostSerializer(post, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    def _comment(self, request, comment_uuid):
        comment = Comment.objects.select_related("post", "author").filter(pk=comment_uuid, post__in=visible_posts(request.user)).first()
        if comment is None:
            raise Http404
        return comment

    @extend_schema(request=None, responses={204: None, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def delete(self, request, comment_uuid):
        soft_delete(actor=request.user, instance=self._comment(request, comment_uuid))
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentReactionView(CommentDetailView):
    @extend_schema(request=ReactionSerializer, responses={200: ReactionSerializer, 403: ApiErrorSerializer})
    def put(self, request, comment_uuid):
        require_capability(request.user, REACT)
        comment = self._comment(request, comment_uuid)
        if comment.deleted_at:
            raise PermissionDenied("Không thể reaction bình luận đã xóa.")
        serializer = ReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reaction = set_reaction(actor=request.user, target=comment, **serializer.validated_data)
        return Response({"kind": reaction.kind})

    @extend_schema(request=None, responses={204: None, 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def delete(self, request, comment_uuid):
        comment = self._comment(request, comment_uuid)
        CommentReaction.objects.filter(comment=comment, actor=request.user.employee_profile).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttachmentDownloadView(APIView):
    @extend_schema(responses={(200, "application/octet-stream"): OpenApiResponse(description="Protected attachment"), 403: ApiErrorSerializer, 404: ApiErrorSerializer})
    def get(self, request, attachment_uuid):
        get_actor_employee(request.user)
        attachment = PostAttachment.objects.select_related("post").filter(pk=attachment_uuid, deleted_at__isnull=True, post__in=visible_posts(request.user), post__deleted_at__isnull=True).first()
        if attachment is None:
            raise Http404
        try:
            return protected_file_response(attachment.storage_key, attachment.original_name, attachment.content_type)
        except FileNotFoundError as exc:
            raise Http404 from exc


class AudienceOptionsView(APIView):
    @extend_schema(responses={200: dict, 403: ApiErrorSerializer})
    def get(self, request):
        get_actor_employee(request.user)
        employees = Employee.objects.filter(
            employment_status__in=[Employee.EmploymentStatus.PROBATION, Employee.EmploymentStatus.OFFICIAL]
        ).select_related("team").order_by("display_name", "employee_code")
        teams = Team.objects.filter(is_active=True).order_by("name")
        return Response({
            "employees": [{"uuid": item.pk, "employee_code": item.employee_code, "display_name": item.display_name or item.employee_code, "team_uuid": item.team_id, "team_name": item.team.name if item.team else None} for item in employees],
            "teams": [{"uuid": item.pk, "code": item.code, "name": item.name} for item in teams],
        })
