from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Discipline(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="disciplines",
        verbose_name=_("User"),
    )
    offense = models.CharField(max_length=100, verbose_name=_("Offense"))
    defense = models.TextField(blank=True, verbose_name=_("Defense"))
    decision = models.TextField(verbose_name=_("Decision"))
    penalty = models.CharField(max_length=100, blank=True, verbose_name=_("Penalty"))
    is_guilty = models.BooleanField(default=True, verbose_name=_("Is Guilty"))
    date = models.DateField(default=timezone.now, verbose_name=_("Date"))
    attendance = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="attended_disciplines",
        verbose_name=_("Attendance"),
    )

    class Meta:
        verbose_name = _("Discipline")
        verbose_name_plural = _("Disciplines")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.offense} - {self.date}"
