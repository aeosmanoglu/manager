from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from treasury.enums import ExpenseType, IncomeType


class Income(BaseModel):
    type = models.CharField(
        max_length=20, choices=IncomeType.choices, default=IncomeType.DUES
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="incomes",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.type


class Expense(BaseModel):
    type = models.CharField(
        max_length=20, choices=ExpenseType.choices, default=ExpenseType.UTILITY
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField()

    def __str__(self):
        return self.type


class Inventory(BaseModel):
    item = models.ForeignKey(
        "InventoryItem",
        on_delete=models.CASCADE,
        related_name="inventories",
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inventories",
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.item.name


class InventoryItem(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
