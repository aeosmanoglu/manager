from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SecretaryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "secretary"

    verbose_name = _("Secretary")
