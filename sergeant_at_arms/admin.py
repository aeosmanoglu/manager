from django.contrib import admin
from unfold.contrib.filters.admin import BooleanRadioFilter
from unfold.decorators import display

from core.admin import DefaultAdmin
from sergeant_at_arms.models import Discipline


@admin.register(Discipline)
class DisciplineAdmin(DefaultAdmin):
    filter_horizontal = ("attendance",)
    list_display = ("user", "offense", "penalty", "display_is_guilty", "date")
    list_filter = [("is_guilty", BooleanRadioFilter)]

    @display(
        description="Is Guilty",
        label={
            "Yes": "danger",
            "No": "success",
        },
    )
    def display_is_guilty(self, obj):
        return "Yes" if obj.is_guilty else "No"
