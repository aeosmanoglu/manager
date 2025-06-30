from django.db import models
from django.utils.translation import gettext_lazy as _


class StatementType(models.TextChoices):
    INCOME = "income", _("Income")
    EXPENSE = "expense", _("Expense")
