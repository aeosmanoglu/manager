from django.db import models


class StatementType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"
