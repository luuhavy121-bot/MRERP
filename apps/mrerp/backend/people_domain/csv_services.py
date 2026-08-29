import csv
import io

from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Employee, Team
from .services import audit


CSV_FIELDS = ["employee_code", "display_name", "job_title", "team_code", "employment_status"]


def export_employee_rows():
    yield CSV_FIELDS
    for employee in Employee.objects.select_related("team").order_by("employee_code"):
        yield [
            employee.employee_code,
            employee.display_name,
            employee.job_title,
            employee.team.code if employee.team else "",
            employee.employment_status,
        ]


def import_employee_csv(*, actor, uploaded_file):
    if uploaded_file.size > 2 * 1024 * 1024:
        raise ValidationError({"file": "File CSV vượt giới hạn 2 MB."})
    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValidationError({"file": "CSV phải dùng UTF-8."}) from None
    reader = csv.DictReader(io.StringIO(text))
    required = {"employee_code", "display_name", "job_title", "team_code"}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):
        raise ValidationError({"file": f"CSV cần các cột: {', '.join(sorted(required))}."})

    rows = list(reader)
    if not rows:
        raise ValidationError({"file": "CSV không có dữ liệu."})
    errors = {}
    prepared = []
    seen_codes = set()
    for number, row in enumerate(rows, start=2):
        code = (row.get("employee_code") or "").strip()
        normalized = code.casefold()
        if not code:
            errors[str(number)] = "Thiếu employee_code."
            continue
        if normalized in seen_codes or Employee.objects.filter(employee_code__iexact=code).exists():
            errors[str(number)] = "employee_code bị trùng."
            continue
        team_code = (row.get("team_code") or "").strip()
        team = Team.objects.filter(code__iexact=team_code, is_active=True).first() if team_code else None
        if team_code and not team:
            errors[str(number)] = "team_code không tồn tại hoặc đã archive."
            continue
        seen_codes.add(normalized)
        prepared.append((code, (row.get("display_name") or "").strip(), (row.get("job_title") or "").strip(), team))
    if errors:
        raise ValidationError({"rows": errors})

    with transaction.atomic():
        employees = [
            Employee.objects.create(
                employee_code=code,
                display_name=display_name,
                job_title=job_title,
                team=team,
                employment_status=Employee.EmploymentStatus.PROBATION,
            )
            for code, display_name, job_title, team in prepared
        ]
        for employee in employees:
            audit(actor=actor, action="people.employee.imported", target=employee, changes={"account_created": False, "employment_status": Employee.EmploymentStatus.PROBATION})
    return len(employees)
