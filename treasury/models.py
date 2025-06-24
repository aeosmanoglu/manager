from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from treasury.enums import StatementType

current_year = timezone.now().year

current_month = timezone.now().month


class Period(BaseModel):
    month = models.IntegerField(
        default=current_month, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.IntegerField(
        default=current_year,
        validators=[
            MinValueValidator(current_year),
            MaxValueValidator(current_year + 1),
        ],
    )

    class Meta:
        unique_together = ("month", "year")

    def __str__(self):
        return f"{self.month}/{self.year}"


class Dues(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dues",
    )
    period = models.ForeignKey(
        "Period",
        on_delete=models.CASCADE,
        related_name="dues",
    )
    amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    is_paid = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.period} - {self.amount}"


class Statement(BaseModel):
    type = models.CharField(max_length=10, choices=StatementType.choices)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.type} - {self.amount} - {self.date}"


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
