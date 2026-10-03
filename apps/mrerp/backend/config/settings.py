import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
APP_ENV = os.getenv("MRERP_ENV", "development")
DEBUG = APP_ENV != "production"
# Company-confirmed workweek, 03/10/2026; imported HR attendance is never recalculated.
MRERP_WORK_WEEKDAYS = (0, 1, 2, 3, 4, 5)
MOCK_IDENTITY_ENABLED = os.getenv("MRERP_MOCK_IDENTITY", "true").lower() == "true"

if APP_ENV == "production" and MOCK_IDENTITY_ENABLED:
    raise ImproperlyConfigured("Mock Identity must be disabled in production.")

SECRET_KEY = os.getenv("MRERP_SECRET_KEY", "unsafe-development-key-change-me")
if APP_ENV == "production" and SECRET_KEY == "unsafe-development-key-change-me":
    raise ImproperlyConfigured("MRERP_SECRET_KEY is required in production.")

ALLOWED_HOSTS = [host for host in os.getenv("MRERP_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host]
CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in os.getenv(
        "MRERP_CSRF_TRUSTED_ORIGINS",
        "http://localhost:4173,http://127.0.0.1:4173",
    ).split(",")
    if origin
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "people_domain.apps.PeopleDomainConfig",
    "leave_domain.apps.LeaveDomainConfig",
    "dashboard_domain.apps.DashboardDomainConfig",
    "feed_domain.apps.FeedDomainConfig",
    "task_domain.apps.TaskDomainConfig",
    "preferences_domain.apps.PreferencesDomainConfig",
    "recruitment_domain.apps.RecruitmentDomainConfig",
    "performance_domain.apps.PerformanceDomainConfig",
    "documents_domain.apps.DocumentsDomainConfig",
    "rewards_domain.apps.RewardsDomainConfig",
    "mock_identity.apps.MockIdentityConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.CorrelationIdMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

if os.getenv("MRERP_DB_ENGINE", "sqlite") == "postgres":
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "mrerp"),
        "USER": os.getenv("POSTGRES_USER", "mrerp"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }}
else:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("MRERP_SQLITE_PATH", BASE_DIR / "db.sqlite3"),
    }}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_ROOT = Path(os.getenv("MRERP_MEDIA_ROOT", BASE_DIR / "media"))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_BROKER_URL = os.getenv("MRERP_REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = None
CELERY_TASK_IGNORE_RESULT = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULE = {
    "task-recurrence-every-minute": {
        "task": "task_domain.process_recurrences",
        "schedule": 60.0,
    },
    "dashboard-deadline-notifications": {
        "task": "dashboard_domain.emit_deadline_notifications",
        "schedule": 900.0,
    },
    "retention-purge-daily": {
        "task": "dashboard_domain.purge_expired_data",
        "schedule": 86400.0,
    },
    "phase-3-retention-daily": {
        "task": "recruitment_domain.anonymize_expired_candidates",
        "schedule": 86400.0,
    },
    "documents-retention-daily": {
        "task": "documents_domain.purge_expired_documents",
        "schedule": 86400.0,
    },
}

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = APP_ENV == "production"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = APP_ENV == "production"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "config.exceptions.api_exception_handler",
}
SPECTACULAR_SETTINGS = {
    "TITLE": "MRERP API",
    "DESCRIPTION": "MRERP modular-monolith API contract",
    "VERSION": "1.0.0",
    "ENUM_NAME_OVERRIDES": {
        "EmploymentStatusEnum": "people_domain.choices.EMPLOYMENT_STATUS_CHOICES",
        "NotificationKindEnum": "dashboard_domain.models.NOTIFICATION_KIND_CHOICES",
        "FeedReactionKindEnum": "feed_domain.models.ReactionKind.choices",
        "TaskAttachmentKindEnum": "task_domain.models.TASK_ATTACHMENT_KIND_CHOICES",
        "GoalScopeEnum": "task_domain.models.GOAL_SCOPE_CHOICES",
        "DocumentScopeEnum": "documents_domain.models.DOCUMENT_SCOPE_CHOICES",
    },
}

# Shared public-form throttling across workers when Redis is configured.
if os.getenv("MRERP_REDIS_URL"):
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache", "LOCATION": os.environ["MRERP_REDIS_URL"], "KEY_PREFIX": "mrerp-throttle"}}
