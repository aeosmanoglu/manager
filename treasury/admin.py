from django.contrib import admin

from core.admin import DefaultAdmin
from treasury.models import Expense, Income


@admin.register(Income)
class IncomeAdmin(DefaultAdmin):
    list_filter = ("type", "date")
    list_display = ("type", "user", "amount", "date", "description")
    search_fields = ("user__first_name", "user__last_name", "description")


@admin.register(Expense)
class ExpenseAdmin(DefaultAdmin):
    list_filter = ("type", "date")
    list_display = ("type", "user", "amount", "date", "description")
    search_fields = ("user__first_name", "user__last_name", "description")
