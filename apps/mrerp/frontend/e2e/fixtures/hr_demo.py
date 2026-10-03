"""Synthetic fixture for hr-demo-upgrade.spec.ts, only in a scratch SQLite DB.

Run after migrate and seed_demo on a fresh database under the repository tmp/.
Never run against the Docker/pilot database.
"""
from pathlib import Path

import django

django.setup()
from django.conf import settings
from people_domain.models import Employee
from performance_domain.models import PerformanceReview, PerformanceKPI
from recruitment_domain.models import HiringRequest, JobOpening, Candidate, Application

scratch_root = Path(__file__).resolve().parents[5] / "tmp"
database = settings.DATABASES["default"]
if database["ENGINE"] != "django.db.backends.sqlite3" or not Path(database["NAME"]).resolve().is_relative_to(scratch_root.resolve()):
    raise SystemExit("HR E2E fixture requires an isolated SQLite database under repository tmp/.")
if PerformanceReview.objects.filter(month="2026-10-01").exists():
    raise SystemExit("Use a fresh scratch database before running the HR demo E2E suite.")

staff = Employee.objects.get(employee_code="STF01")
leader = Employee.objects.get(employee_code="LDR01")
review, _ = PerformanceReview.objects.get_or_create(employee=staff, month="2026-09-01", defaults={"team": staff.team, "leader": leader, "leader_comment": "Nhận xét tháng cũ"})
PerformanceKPI.objects.get_or_create(review=review, position=0, defaults={"title": "Hiệu quả chiến dịch", "description": "Theo mục tiêu Leader giao", "weight": 100, "completion": 80, "comment": "Nhận xét cũ"})
if not Application.objects.filter(candidate__email="candidate@example.test").exists():
    hiring = HiringRequest.objects.create(team=staff.team, requester=leader, title="Ads Demo 06/10", description="Quản lý chiến dịch quảng cáo.", location="Hà Nội", employment_type="Toàn thời gian", requirements="Có kinh nghiệm Ads.", benefits="Trao đổi khi phỏng vấn.", deadline="2030-12-31", justification="Nội bộ")
    opening = JobOpening.objects.create(team=staff.team, hiring_request=hiring, title=hiring.title)
    Application.objects.create(opening=opening, candidate=Candidate.objects.create(full_name="Ứng viên demo Ads", email="candidate@example.test", phone="0900000000"))
print("Synthetic HR E2E fixture ready in scratch SQLite database.")
