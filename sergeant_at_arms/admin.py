from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import display

from core.admin import DefaultAdmin
from sergeant_at_arms.models import Discipline


@admin.register(Discipline)
class DisciplineAdmin(DefaultAdmin):
    filter_horizontal = ("attendance",)
    list_display = ("user", "offense", "penalty", "display_is_guilty", "date")
    list_filter = [("is_guilty", BooleanRadioFilter)]
    readonly_fields = ("created_at", "updated_at")

    @display(
        description=_("Is Guilty"),
        label={
            _("Yes"): "danger",
            _("No"): "success",
        },
    )
    def display_is_guilty(self, obj):
        return _("Yes") if obj.is_guilty else _("No")
