from django.contrib import admin

from .models import AuditEvent, Department, Employee, EmploymentTransition, Team, TeamLeadership

admin.site.register([Department, Team, Employee, TeamLeadership, EmploymentTransition, AuditEvent])
