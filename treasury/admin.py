from django.contrib import admin
from unfold.admin import ModelAdmin

from treasury.models import Expense, Income


@admin.register(Income)
class IncomeAdmin(ModelAdmin):
    compressed_fields = True
    list_filter = ("type", "date")
    list_display = ("type", "user","amount", "date", "description")
    search_fields = ("user__first_name", "user__last_name", "description")

@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    compressed_fields = True
    list_filter = ("type", "date")
    list_display = ("type", "user","amount", "date", "description")
    search_fields = ("user__first_name", "user__last_name", "description")



