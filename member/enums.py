from django.db import models


class BloodType(models.TextChoices):
    A_POSITIVE = "A+", "A+"
    A_NEGATIVE = "A-", "A-"
    B_POSITIVE = "B+", "B+"
    B_NEGATIVE = "B-", "B-"
    AB_POSITIVE = "AB+", "AB+"
    AB_NEGATIVE = "AB-", "AB-"
    O_POSITIVE = "O+", "O+"
    O_NEGATIVE = "O-", "O-"


class AddressType(models.TextChoices):
    HOME = "home", "HOME"
    WORK = "work", "WORK"
    OTHER = "other", "OTHER"


class DrivingLicenseType(models.TextChoices):
    NONE = "none", "NONE"
    B = "B", "B"
    A = "A", "A"
    A2 = "A2", "A2"
    A1 = "A1", "A1"
    M = "M", "M"
