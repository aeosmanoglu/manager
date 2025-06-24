from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel
from secretary.enums import (
    AddressType,
    BloodType,
    Charters,
    DrivingLicenseType,
    EventTypes,
    Titles,
)

current_year = timezone.now().year

turkish_plate_validator = RegexValidator(
    regex=r"^[0-9]{2}[A-Z]{1,3}[0-9]{2,4}$",
    message="Please enter a valid Turkish license plate. (Ex: 06ABC123)",
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email adresi zorunludur")
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

    date_joined = models.DateField(default=timezone.now)
    charter = models.IntegerField(choices=Charters.choices, default=Charters.ANKARA)
    title = models.IntegerField(choices=Titles.choices, default=Titles.HANGROUND)

    birth_date = models.DateField(null=True, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    blood_type = models.CharField(
        max_length=20, choices=BloodType.choices, default=BloodType.A_POSITIVE
    )
    driving_license_type = models.CharField(
        max_length=5,
        choices=DrivingLicenseType.choices,
        default=DrivingLicenseType.NONE,
    )
    sponsor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sponsors",
    )

    def __str__(self):
        return self.get_full_name()


class Contact(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="contacts")
    type = models.CharField(
        max_length=5, choices=AddressType.choices, default=AddressType.HOME
    )
    phone = PhoneNumberField(blank=True, help_text="Format: +905555555555")
    address = models.CharField(max_length=100, blank=True)
    what3words = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} address"


class EmergencyContact(BaseModel):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="emergency_contacts"
    )
    name = models.CharField(max_length=20)
    phone = PhoneNumberField(help_text="Format: +905555555555")
    relationship = models.CharField(max_length=20)

    # TODO: ayni telefon numarasi girememeli

    def __str__(self):
        return self.relationship


class Vehicle(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="vehicles")
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    year = models.IntegerField(
        validators=(MinValueValidator(1950), MaxValueValidator(current_year + 1))
    )
    plate = models.CharField(
        max_length=10,
        validators=(turkish_plate_validator,),
        help_text="Format: 06ABC123",
    )
    engine_capacity = models.IntegerField()
    last_maintenance_date = models.DateField()
    inspection_expiry_date = models.DateField()
    insurance_expiry_date = models.DateField()

    def __str__(self):
        return self.plate


class Event(BaseModel):
    type = models.CharField(max_length=10, choices=EventTypes.choices)
    name = models.CharField(max_length=50, default="Weekly Meeting")
    date_time = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=50, default="Club House")
    charter = models.IntegerField(choices=Charters.choices, default=Charters.ANKARA)
    agenda = models.TextField(blank=True)

    decisions = models.TextField(blank=True)
    training_note = models.TextField(blank=True)

    has_ride = models.BooleanField(default=False)
    destination = models.CharField(max_length=50, blank=True)
    ride_note = models.TextField(blank=True)

    attendance = models.ManyToManyField(
        "User",
        blank=True,
        related_name="attended_events",
    )

    def __str__(self):
        return self.name
