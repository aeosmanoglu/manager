from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    ChoicesCheckboxFilter,
    RangeDateFilter,
    RangeNumericFilter,
    RelatedDropdownFilter,
)
from unfold.decorators import display

from core.admin import DefaultAdmin
from treasury.enums import StatementType
from treasury.models import Due, Inventory, InventoryItem, Period, Statement


@admin.register(Period)
class PeriodAdmin(DefaultAdmin):
    list_display = ("month", "year")
    search_fields = ("month", "year")


@admin.register(Due)
class DueAdmin(DefaultAdmin):
    list_display = ("user", "period", "amount", "is_paid", "date", "description")
    list_filter = [
        ("period", RelatedDropdownFilter),
        ("is_paid", BooleanRadioFilter),
        ("date", RangeDateFilter),
        ("amount", RangeNumericFilter),
    ]
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("user__first_name", "user__last_name", "description")
    list_editable = ("is_paid",)


@admin.register(Statement)
class StatementAdmin(DefaultAdmin):
    list_display = ("display_type", "amount", "date", "description")
    list_filter = [
        ("type", ChoicesCheckboxFilter),
        ("date", RangeDateFilter),
        ("amount", RangeNumericFilter),
    ]
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("description",)

    @display(
        description=_("Type"),
        label={
            StatementType.INCOME.label: "success",
            StatementType.EXPENSE.label: "danger",
        },
    )
    def display_type(self, obj):
        return obj.get_type_display()


@admin.register(Inventory)
class InventoryAdmin(DefaultAdmin):
    list_display = ("item", "user", "quantity", "description")
    list_filter = [("quantity", RangeNumericFilter)]
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("item__name", "user__first_name", "user__last_name", "description")


@admin.register(InventoryItem)
class InventoryItemAdmin(DefaultAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")
