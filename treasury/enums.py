from django.db import models


class IncomeType(models.TextChoices):
    DUES = "dues", "Dues"
    SPONSORSHIP = "sponsorship", "Sponsorship"
    OTHER = "other", "Other"

class ExpenseType(models.TextChoices):
    DEPT = "dept", "Dept"
    UTILITY = "utility", "Utility"
    OTHER = "other", "Other"