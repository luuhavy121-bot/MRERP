import uuid
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from people_domain.models import Employee
from .models import RewardGift, RewardRedemption, StarLedgerEntry, TeamStarAllowance
from .services import star_balance

class RedemptionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo',password='Test-only-1234!')
    def setUp(self):
        self.client=APIClient()
        self.staff=Employee.objects.get(employee_code='STF01')
        self.other=Employee.objects.get(employee_code='OTH01')
        self.hr=get_user_model().objects.get(username='hr.demo')
        self.gift=RewardGift.objects.create(title='Sách',category='Học tập',cost=40,stock=2,active=True)
        StarLedgerEntry.objects.create(employee=self.staff,amount=100,entry_type='grant',reason='test',actor=self.hr)
        self.login('staff.demo')
    def login(self,name):
        self.client.force_authenticate(get_user_model().objects.get(username=name))
    def redeem(self,key=None):
        return self.client.post('/api/v1/rewards/redemptions/',{'gift_uuid':str(self.gift.pk),'expected_cost':40,'request_key':str(key or uuid.uuid4())},format='json')
    def decide(self,pk,action):
        return self.client.post(f'/api/v1/rewards/redemptions/{pk}/decision/',{'action':action,'note':'Kiểm thử'},format='json')
    def test_hold_cancel_refund_once_and_ranking_unchanged(self):
        key=uuid.uuid4();r=self.redeem(key);self.assertEqual(r.status_code,201,r.data)
        self.assertEqual(self.redeem(key).status_code,200)
        self.assertEqual(star_balance(self.staff),60)
        self.assertEqual(self.client.get('/api/v1/rewards/stars/me/').data['held'],40)
        self.assertEqual(self.client.get('/api/v1/rewards/leaderboard/').data[0]['stars'],100)
        self.assertEqual(self.decide(r.data['uuid'],'cancel').status_code,200)
        self.assertEqual(self.decide(r.data['uuid'],'cancel').status_code,200)
        self.assertEqual(star_balance(self.staff),100)
        self.gift.refresh_from_db();self.assertEqual(self.gift.stock,2)
        self.assertEqual(StarLedgerEntry.objects.filter(entry_type='refund').count(),1)
    def test_approval_fulfillment_cannot_cancel_or_self_approve(self):
        r=self.redeem();pk=r.data['uuid']
        self.assertEqual(self.decide(pk,'approve').status_code,403)
        self.login('hr.demo');self.assertEqual(self.decide(pk,'fulfill').status_code,400)
        self.assertEqual(self.decide(pk,'approve').status_code,200)
        self.assertEqual(self.decide(pk,'fulfill').status_code,200)
        self.assertEqual(self.decide(pk,'cancel').status_code,400)
        self.assertEqual(star_balance(self.staff),60)
    def test_scope_and_field_redaction(self):
        r=self.redeem();self.login('other.demo')
        self.assertEqual(self.client.get('/api/v1/rewards/redemptions/').data['results'],[])
        self.assertEqual(self.decide(r.data['uuid'],'cancel').status_code,404)
        self.assertEqual(self.client.post('/api/v1/rewards/gifts/',{},format='json').status_code,403)
        self.assertEqual(self.client.get('/api/v1/rewards/allowances/').data['allowances'],[])
        hidden=RewardGift.objects.create(title='Ẩn',category='test',cost=1,stock=1)
        self.assertNotIn(str(hidden.pk),str(self.client.get('/api/v1/rewards/gifts/').data))
        self.assertNotIn('request_key',r.data)
    def test_insufficient_stock_cost_and_invalid_account(self):
        self.assertEqual(self.redeem().status_code,201)
        self.assertEqual(self.redeem().status_code,201)
        self.assertEqual(self.redeem().status_code,400)
        self.gift.cost=45;self.gift.save()
        self.assertEqual(self.redeem().status_code,400)
        self.staff.employment_status='terminated';self.staff.save()
        self.login('staff.demo');self.assertEqual(self.client.get('/api/v1/rewards/gifts/').status_code,403)
        self.staff.employment_status='official';self.staff.save()
        u=self.staff.identity_user;u.is_active=False;u.save();self.client.force_authenticate(u)
        self.assertEqual(self.client.get('/api/v1/rewards/gifts/').status_code,403)
    def test_team_quota_and_negative_guard(self):
        self.login('leader.demo');payload={'employee_uuid':str(self.staff.pk),'amount':4,'reason':'test'}
        url='/api/v1/rewards/stars/grant/'
        self.assertEqual(self.client.post(url,payload,format='json').status_code,400)
        a=TeamStarAllowance.objects.create(team=self.staff.team,month=timezone.localdate().replace(day=1),limit=5)
        self.assertEqual(self.client.post(url,payload,format='json').status_code,201)
        self.assertEqual(self.client.post(url,payload,format='json').status_code,400)
        self.assertEqual(self.client.post(url,{**payload,'amount':-1},format='json').status_code,403)
        self.login('hr.demo');r=self.client.post('/api/v1/rewards/allowances/',{'team_uuid':str(a.team_id),'month':str(a.month),'limit':3},format='json')
        self.assertEqual(r.status_code,400)

    def test_gift_update_rejects_stale_inventory_and_recognition_filter(self):
        self.login('hr.demo')
        snapshot=self.client.get('/api/v1/rewards/gifts/').data[0]
        self.login('staff.demo');self.redeem()
        self.login('hr.demo')
        result=self.client.patch(f'/api/v1/rewards/gifts/{self.gift.pk}/',{'stock':10,'updated_at':snapshot['updated_at']},format='json')
        self.assertEqual(result.status_code,400)
        self.login('leader.demo')
        self.assertEqual(self.client.get(f'/api/v1/rewards/recognitions/?employee_uuid={self.other.pk}').status_code,403)

    def test_manager_reject_refunds_and_catalog_patch(self):
        r=self.redeem();self.login('hr.demo')
        self.assertEqual(self.decide(r.data['uuid'],'reject').status_code,200)
        self.assertEqual(star_balance(self.staff),100)
        snapshot=self.client.get('/api/v1/rewards/gifts/').data[0]
        result=self.client.patch(f'/api/v1/rewards/gifts/{self.gift.pk}/',{'description':'Updated','updated_at':snapshot['updated_at']},format='json')
        self.assertEqual(result.status_code,200,result.data)
        self.assertEqual(result.data['description'],'Updated')


from concurrent.futures import ThreadPoolExecutor
from django.db import connections
from django.test import TransactionTestCase, skipUnlessDBFeature

@skipUnlessDBFeature('has_select_for_update')
class RedemptionConcurrencyTests(TransactionTestCase):
    def setUp(self):
        call_command('seed_demo',password='Test-only-1234!')
        self.staff=Employee.objects.get(employee_code='STF01')
        self.other=Employee.objects.get(employee_code='OTH01')
        self.hr=get_user_model().objects.get(username='hr.demo')
        self.gift=RewardGift.objects.create(title='Last item',category='test',cost=40,stock=1,active=True)
        for person in [self.staff,self.other]:
            StarLedgerEntry.objects.create(employee=person,amount=100,entry_type='grant',reason='test',actor=self.hr)

    def call(self,name,url,data):
        try:
            client=APIClient();client.force_authenticate(get_user_model().objects.get(username=name))
            return client.post(url,data,format='json').status_code
        finally:
            connections.close_all()

    def test_last_gift_not_double_reserved(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda name:self.call(name,'/api/v1/rewards/redemptions/',{'gift_uuid':str(self.gift.pk),'expected_cost':40,'request_key':str(uuid.uuid4())}),['staff.demo','other.demo']))
        self.assertEqual(sorted(results),[201,400])
        self.assertEqual(RewardRedemption.objects.count(),1)
        self.gift.refresh_from_db();self.assertEqual(self.gift.stock,0)

    def test_team_allowance_not_overspent(self):
        self.other.team=self.staff.team;self.other.save()
        TeamStarAllowance.objects.create(team=self.staff.team,month=timezone.localdate().replace(day=1),limit=5)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda person:self.call('leader.demo','/api/v1/rewards/stars/grant/',{'employee_uuid':str(person.pk),'amount':4,'reason':'concurrent'}),[self.staff,self.other]))
        self.assertEqual(sorted(results),[201,400])
