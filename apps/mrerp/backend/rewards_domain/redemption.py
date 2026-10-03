from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema
from people_domain.access import get_actor_employee
from people_domain.models import Employee, Team, TeamLeadership
from people_domain.services import audit
from people_domain.views import require_capability
from .models import RewardGift, RewardRedemption, StarLedgerEntry, TeamStarAllowance
from .services import star_balance
from .capabilities import VIEW_REWARDS, GRANT_STARS_COMPANY


def actor(request, management=False):
    employee = get_actor_employee(request.user)
    require_capability(request.user, GRANT_STARS_COMPANY if management else VIEW_REWARDS)
    return employee


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardGift
        fields = ['uuid', 'title', 'description', 'category', 'cost', 'stock', 'active', 'updated_at']
        read_only_fields = ['updated_at']
    cost = serializers.IntegerField(min_value=1, max_value=1000000)
    stock = serializers.IntegerField(min_value=0, max_value=1000000)
    description = serializers.CharField(max_length=3000, allow_blank=True, required=False)


class RedemptionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.display_name', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = RewardRedemption
        fields = ['uuid', 'employee', 'employee_name', 'gift', 'gift_title', 'cost', 'status', 'status_label', 'note', 'created_at', 'updated_at']
        read_only_fields = fields


class GiftPatchSerializer(GiftSerializer):
    updated_at = serializers.CharField(required=True)
    class Meta(GiftSerializer.Meta):
        read_only_fields = ['uuid']


class RedemptionPageSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = RedemptionSerializer(many=True)


class RedeemInput(serializers.Serializer):
    gift_uuid = serializers.UUIDField()
    request_key = serializers.UUIDField()
    expected_cost = serializers.IntegerField(min_value=1)


class DecisionInput(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'cancel', 'fulfill'])
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AllowanceInput(serializers.Serializer):
    team_uuid = serializers.UUIDField()
    month = serializers.DateField()
    limit = serializers.IntegerField(min_value=0, max_value=1000000)
    def validate_month(self, value):
        if value.day != 1:
            raise serializers.ValidationError('Tháng phải là ngày đầu tháng.')
        return value


class GiftsView(APIView):
    @extend_schema(responses=GiftSerializer(many=True))
    def get(self, request):
        actor(request)
        rows = RewardGift.objects.all()
        if not request.user.has_perm(GRANT_STARS_COMPANY):
            rows = rows.filter(active=True)
        return Response(GiftSerializer(rows, many=True).data)

    @extend_schema(request=GiftSerializer, responses={201:GiftSerializer})
    def post(self, request):
        actor(request, True)
        data = GiftSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        with transaction.atomic():
            gift = data.save()
            audit(actor=request.user, action='rewards.gift.created', target=gift, changes={'title':gift.title})
        return Response(GiftSerializer(gift).data, status=201)


class GiftDetailView(APIView):
    @extend_schema(request=GiftPatchSerializer, responses=GiftSerializer)
    def patch(self, request, uuid):
        actor(request, True)
        with transaction.atomic():
            gift = get_object_or_404(RewardGift.objects.select_for_update(), pk=uuid)
            if request.data.get('updated_at') != GiftSerializer(gift).data['updated_at']:
                raise ValidationError('Quà đã thay đổi. Tải lại trước khi chỉnh sửa.')
            data = GiftPatchSerializer(gift, data=request.data, partial=True)
            data.is_valid(raise_exception=True)
            data.validated_data.pop('updated_at', None)
            data.save()
            audit(actor=request.user, action='rewards.gift.updated', target=gift, changes={'fields':list(data.validated_data)})
        return Response(data.data)


class RedemptionsView(APIView):
    def handle_exception(self, exc):
        if isinstance(exc, IntegrityError):
            exc = ValidationError('Mã yêu cầu đã được sử dụng. Tải lại yêu cầu đổi thưởng.')
        return super().handle_exception(exc)

    @extend_schema(responses=RedemptionPageSerializer)
    def get(self, request):
        employee = actor(request)
        rows = RewardRedemption.objects.select_related('employee')
        if not request.user.has_perm(GRANT_STARS_COMPANY):
            rows = rows.filter(employee=employee)
        pagination = PageNumberPagination()
        page = pagination.paginate_queryset(rows, request)
        return pagination.get_paginated_response(RedemptionSerializer(page, many=True).data)

    @extend_schema(request=RedeemInput, responses={201:RedemptionSerializer})
    def post(self, request):
        employee = actor(request)
        data = RedeemInput(data=request.data)
        data.is_valid(raise_exception=True)
        d = data.validated_data
        with transaction.atomic():
            Employee.objects.select_for_update().get(pk=employee.pk)
            old = RewardRedemption.objects.filter(request_key=d['request_key']).first()
            if old:
                if old.employee_id != employee.pk or old.gift_id != d['gift_uuid'] or old.cost != d['expected_cost']:
                    raise ValidationError('Mã yêu cầu đã được sử dụng.')
                return Response(RedemptionSerializer(old).data)
            gift = get_object_or_404(RewardGift.objects.select_for_update(), pk=d['gift_uuid'], active=True)
            if gift.cost != d['expected_cost']:
                raise ValidationError('Mức sao đã thay đổi. Tải lại danh mục trước khi đổi.')
            if gift.stock < 1 or star_balance(employee) < gift.cost:
                raise ValidationError('Quà hết số lượng hoặc bạn chưa đủ sao khả dụng.')
            redemption = RewardRedemption.objects.create(employee=employee, gift=gift, gift_title=gift.title, cost=gift.cost, request_key=d['request_key'])
            gift.stock -= 1
            gift.save(update_fields=['stock','updated_at'])
            StarLedgerEntry.objects.create(employee=employee, amount=-gift.cost, entry_type='hold', actor=request.user, reason=f'Giữ sao: {gift.title}', idempotency_key=f'redeem:{redemption.pk}')
            audit(actor=request.user, action='rewards.redemption.requested', target=redemption, changes={'cost':gift.cost})
        return Response(RedemptionSerializer(redemption).data, status=201)


class RedemptionDecisionView(APIView):
    @extend_schema(request=DecisionInput, responses=RedemptionSerializer)
    def post(self, request, uuid):
        employee = actor(request)
        data = DecisionInput(data=request.data)
        data.is_valid(raise_exception=True)
        action = data.validated_data['action']
        manager = request.user.has_perm(GRANT_STARS_COMPANY)
        query = RewardRedemption.objects.all() if manager else RewardRedemption.objects.filter(employee=employee)
        reference = get_object_or_404(query, pk=uuid)
        if action != 'cancel' and (not manager or reference.employee_id == employee.pk):
            raise PermissionDenied('Cần HR/CEO khác duyệt và xác nhận trao quà.')
        with transaction.atomic():
            Employee.objects.select_for_update().get(pk=reference.employee_id)
            row = RewardRedemption.objects.select_for_update().get(pk=uuid)
            transitions = {'approve':('pending','approved'), 'fulfill':('approved','fulfilled'), 'reject':('pending','rejected')}
            note = data.validated_data.get('note','').strip()
            target = 'cancelled' if action == 'cancel' else transitions[action][1]
            if row.status == target:
                return Response(RedemptionSerializer(row).data)
            if action == 'cancel':
                if row.status not in ['pending','approved']:
                    raise ValidationError('Chỉ hủy trước khi trao quà.')
            elif row.status != transitions[action][0]:
                raise ValidationError('Trạng thái đã thay đổi. Tải lại yêu cầu.')
            if action in ['reject','cancel']:
                if not note:
                    raise ValidationError('Cần lý do hủy hoặc từ chối.')
                gift = RewardGift.objects.select_for_update().get(pk=row.gift_id)
                gift.stock += 1
                gift.save(update_fields=['stock','updated_at'])
                StarLedgerEntry.objects.create(employee_id=row.employee_id, amount=row.cost, entry_type='refund', actor=request.user, reason=f'Hoàn sao: {row.gift_title}', idempotency_key=f'refund:{row.pk}')
            row.status, row.note, row.processed_by = target, note, request.user
            row.save(update_fields=['status','note','processed_by','updated_at'])
            audit(actor=request.user, action=f'rewards.redemption.{target}', target=row, changes={'note':note})
        return Response(RedemptionSerializer(row).data)


class AllowancesView(APIView):
    @extend_schema(responses=dict)
    def get(self, request):
        employee = actor(request)
        teams = Team.objects.all() if request.user.has_perm(GRANT_STARS_COMPANY) else Team.objects.filter(pk__in=TeamLeadership.objects.filter(leader=employee).values('team_id'))
        rows = TeamStarAllowance.objects.filter(team__in=teams).select_related('team').annotate(used=Sum('starledgerentry__amount'))
        return Response({'teams':[{'uuid':str(t.pk),'name':t.name} for t in teams], 'allowances':[{'team_uuid':str(a.team_id),'team_name':a.team.name,'month':a.month.isoformat(),'limit':a.limit,'used':a.used or 0} for a in rows]})

    @extend_schema(request=AllowanceInput, responses=dict)
    def post(self, request):
        actor(request, True)
        data = AllowanceInput(data=request.data)
        data.is_valid(raise_exception=True)
        d = data.validated_data
        with transaction.atomic():
            team = get_object_or_404(Team.objects.select_for_update(), pk=d['team_uuid'])
            row, _ = TeamStarAllowance.objects.get_or_create(team=team, month=d['month'])
            row = TeamStarAllowance.objects.select_for_update().get(pk=row.pk)
            used = row.starledgerentry_set.aggregate(value=Sum('amount'))['value'] or 0
            if d['limit'] < used:
                raise ValidationError('Hạn mức không được thấp hơn số đã cấp.')
            row.limit = d['limit']; row.save(update_fields=['limit'])
            audit(actor=request.user, action='rewards.allowance.updated', target=team, changes={'month':str(d['month']),'limit':row.limit})
        return Response({'limit':row.limit,'used':used})
