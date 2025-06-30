from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel
from secretary.enums import (
    AddressType,
    BloodType,
    DrivingLicenseType,
    EventTypes,
    Titles,
)

current_year = timezone.now().year

turkish_plate_validator = RegexValidator(
    regex=r"^[0-9]{2}[A-Z]{1,3}[0-9]{2,4}$",
    message=_("Please enter a valid Turkish license plate. (Ex: 06ABC123)"),
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email address is required"))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    date_joined = models.DateField(default=timezone.now, verbose_name=_("Date Joined"))
    title = models.IntegerField(
        choices=Titles.choices, default=Titles.HANGROUND, verbose_name=_("Title")
    )

    birth_date = models.DateField(null=True, blank=True, verbose_name=_("Birth Date"))
    allergies = models.TextField(blank=True, verbose_name=_("Allergies"))
    medical_conditions = models.TextField(
        blank=True, verbose_name=_("Medical Conditions")
    )
    medications = models.TextField(blank=True, verbose_name=_("Medications"))
    blood_type = models.CharField(
        max_length=20,
        choices=BloodType.choices,
        default=BloodType.A_POSITIVE,
        verbose_name=_("Blood Type"),
    )
    driving_license_type = models.CharField(
        max_length=5,
        choices=DrivingLicenseType.choices,
        default=DrivingLicenseType.NONE,
        verbose_name=_("License"),
    )
    sponsor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sponsors",
        verbose_name=_("Sponsor"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.get_full_name()


class Contact(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="contacts", verbose_name=_("User"))
    type = models.CharField(
        max_length=5,
        choices=AddressType.choices,
        default=AddressType.HOME,
        verbose_name=_("Type"),
    )
    phone = PhoneNumberField(
        blank=True, help_text="Format: +905555555555", verbose_name=_("Phone")
    )
    address = models.CharField(max_length=100, blank=True, verbose_name=_("Address"))
    what3words = models.CharField(
        max_length=30, blank=True, verbose_name=_("What3Words")
    )

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

    def __str__(self):
        return _("%(type_display)s address") % {"type_display": self.get_type_display()}


class EmergencyContact(BaseModel):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="emergency_contacts", verbose_name=_("User")
    )
    name = models.CharField(max_length=20, verbose_name=_("Name"))
    phone = PhoneNumberField(help_text="Format: +905555555555", verbose_name=_("Phone"))
    relationship = models.CharField(max_length=20, verbose_name=_("Relationship"))

    class Meta:
        unique_together = ("user", "phone")
        verbose_name = _("Emergency Contact")
        verbose_name_plural = _("Emergency Contacts")

    def __str__(self):
        return self.relationship


class Vehicle(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="vehicles", verbose_name=_("User"))
    brand = models.CharField(max_length=20, verbose_name=_("Brand"))
    model = models.CharField(max_length=20, verbose_name=_("Model"))
    year = models.IntegerField(
        validators=(MinValueValidator(1950), MaxValueValidator(current_year + 1)),
        verbose_name=_("Year"),
    )
    plate = models.CharField(
        max_length=10,
        validators=(turkish_plate_validator,),
        help_text="Format: 06ABC123",
        unique=True,
        verbose_name=_("Plate"),
    )
    engine_capacity = models.IntegerField(verbose_name=_("Engine Capacity"))
    last_maintenance_date = models.DateField(verbose_name=_("Last Maintenance Date"))
    inspection_expiry_date = models.DateField(verbose_name=_("Inspection Expiry Date"))
    insurance_expiry_date = models.DateField(verbose_name=_("Insurance Expiry Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")

    def __str__(self):
        return self.plate


class Event(BaseModel):
    type = models.CharField(
        max_length=10, choices=EventTypes.choices, verbose_name=_("Type")
    )
    name = models.CharField(
        max_length=50, default=_("Weekly Meeting"), verbose_name=_("Name")
    )
    date_time = models.DateTimeField(default=timezone.now, verbose_name=_("Date Time"))
    location = models.CharField(
        max_length=50, default=_("Club House"), verbose_name=_("Location")
    )
    agenda = models.TextField(blank=True, verbose_name=_("Agenda"))

    decisions = models.TextField(blank=True, verbose_name=_("Decisions"))
    training_note = models.TextField(blank=True, verbose_name=_("Training Note"))

    has_ride = models.BooleanField(default=False, verbose_name=_("Has Ride"))
    destination = models.CharField(
        max_length=50, blank=True, verbose_name=_("Destination")
    )
    ride_note = models.TextField(blank=True, verbose_name=_("Ride Note"))

    attendance = models.ManyToManyField(
        "User",
        blank=True,
        related_name="attended_events",
        verbose_name=_("Attendance"),
    )

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.name
