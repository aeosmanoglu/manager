from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel


class Discipline(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="disciplines",
    )
    offense = models.CharField(max_length=100)
    defense = models.TextField(blank=True)
    decision = models.TextField()
    penalty = models.CharField(max_length=100, blank=True)
    is_guilty = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)
    attendance = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="attended_disciplines",
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.offense} - {self.date}"
