from django.apps import AppConfig


class MockIdentityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mock_identity"
    verbose_name = "Mock Identity (dev/test only)"
