from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from treasury.enums import StatementType

current_year = timezone.now().year

current_month = timezone.now().month


class Period(BaseModel):
    month = models.IntegerField(
        default=current_month,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name=_("Month"),
    )
    year = models.IntegerField(
        default=current_year,
        validators=[
            MinValueValidator(current_year),
            MaxValueValidator(current_year + 1),
        ],
        verbose_name=_("Year"),
    )

    class Meta:
        unique_together = ("month", "year")
        verbose_name = _("Period")
        verbose_name_plural = _("Periods")

    def __str__(self):
        return f"{self.month}/{self.year}"


class Due(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dues",
        verbose_name=_("User"),
    )
    period = models.ForeignKey(
        "Period",
        on_delete=models.CASCADE,
        related_name="dues",
        verbose_name=_("Period"),
    )
    amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Amount"),
    )
    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid"))
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Due")
        verbose_name_plural = _("Dues")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.period} - {self.amount}"


class Statement(BaseModel):
    type = models.CharField(
        max_length=10, choices=StatementType.choices, verbose_name=_("Type")
    )
    description = models.CharField(max_length=100, verbose_name=_("Description"))
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Amount"),
    )
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))

    class Meta:
        verbose_name = _("Statement")
        verbose_name_plural = _("Statements")

    def __str__(self):
        return f"{self.type} - {self.amount} - {self.date}"


class Inventory(BaseModel):
    item = models.ForeignKey(
        "InventoryItem",
        on_delete=models.CASCADE,
        related_name="inventories",
        verbose_name=_("Item"),
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("Quantity")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inventories",
        verbose_name=_("User"),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")

    def __str__(self):
        return self.item.name


class InventoryItem(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Inventory Item")
        verbose_name_plural = _("Inventory Items")

    def __str__(self):
        return self.name
