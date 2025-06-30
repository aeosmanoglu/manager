from django.db import models
from django.utils.translation import gettext_lazy as _


class Titles(models.IntegerChoices):
    SUPPORTER = 10, "Supporter"
    HANGROUND = 20, "Hanground"
    PROSPECT = 30, "Prospect"

    MEMBER = 40, "Member"
    PRESIDENT = 41, "President"
    VICE_PRESIDENT = 42, "Vice President"
    SERGENT_AT_ARMS = 43, "Sergent at Arms"
    SECRETARY = 44, "Secretary"
    TREASURER = 45, "Treasurer"
    ROAD_CAPTAIN = 46, "Road Captain"
    TAILGUNNER = 47, "Tailgunner"
    SECURITY = 48, "Security"
    MECHANIC = 49, "Mechanic"

    FROZEN = 50, "Frozen"

    LEFT = 60, "Left"
    OUT = 61, "Out"
    NO_CONTACT = 62, "No Contact"
    OUT_BAD = 63, "Out Bad"

    DECEASED = 70, _("Deceased")
    LIFE_TIME_MEMBER = 71, "Life Time Member"


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
    HOME = "home", _("Home")
    WORK = "work", _("Work")
    OTHER = "other", _("Other")


class DrivingLicenseType(models.TextChoices):
    NONE = "none", _("None")
    B = "B", "B"
    A = "A", "A"
    A2 = "A2", "A2"
    A1 = "A1", "A1"
    M = "M", "M"


class EventTypes(models.TextChoices):
    MEETING = "meeting", _("Meeting")
    RIDE = "ride", _("Ride")
    PARTY = "party", _("Party")
    OTHER = "other", _("Other")
