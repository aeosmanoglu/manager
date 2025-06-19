from django.contrib import admin
from unfold.contrib.filters.admin import (
    ChoicesCheckboxFilter,
    RangeDateFilter,
    RangeNumericFilter,
)

from core.admin import DefaultAdmin
from treasury.models import Expense, Income, Inventory, InventoryItem


@admin.register(Income)
class IncomeAdmin(DefaultAdmin):
    list_filter = [
        ("type", ChoicesCheckboxFilter),
        ("date", RangeDateFilter),
        ("amount", RangeNumericFilter),
    ]
    list_display = ("type", "user", "amount", "date", "description")
    search_fields = ("user__first_name", "user__last_name", "description")


@admin.register(Expense)
class ExpenseAdmin(DefaultAdmin):
    list_filter = [
        ("type", ChoicesCheckboxFilter),
        ("date", RangeDateFilter),
        ("amount", RangeNumericFilter),
    ]
    list_display = ("type", "user", "amount", "date", "description")
    search_fields = ("user__first_name", "user__last_name", "description")


@admin.register(Inventory)
class InventoryAdmin(DefaultAdmin):
    list_filter = [("quantity", RangeNumericFilter)]
    list_display = ("item", "user", "quantity", "description")
    search_fields = ("item__name", "user__first_name", "user__last_name", "description")


@admin.register(InventoryItem)
class InventoryItemAdmin(DefaultAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


## TODO: Add label display
## TODO: Add sgtarms module
