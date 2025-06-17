from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel
from member.enums import AddressType, BloodType, DrivingLicenseType

current_year = timezone.now().year

turkish_plate_validator = RegexValidator(
    regex=r'^[0-9]{2}[A-Z]{1,3}[0-9]{2,4}$',
    message="Please enter a valid Turkish license plate. (Ex: 06ABC123)"
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

    def __str__(self):
        return self.get_full_name()


class Contact(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="contacts")
    type = models.CharField(
        max_length=5, choices=AddressType.choices, default=AddressType.HOME
    )
    phone = PhoneNumberField(blank=True)
    address = models.CharField(max_length=20, blank=True)
    what3words = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.type


class EmergencyContact(BaseModel):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="emergency_contacts"
    )
    name = models.CharField(max_length=20)
    phone = PhoneNumberField(blank=True)
    relationship = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Vehicle(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="vehicles")
    brand = models.CharField(max_length=20)
    model = models.CharField(max_length=20)
    year = models.IntegerField(
        validators=(MinValueValidator(1900), MaxValueValidator(current_year + 1))
    )
    plate = models.CharField(max_length=10, validators=(turkish_plate_validator,))
    engine_capacity = models.IntegerField()
    last_maintenance_date = models.DateField()
    inspection_expiry_date = models.DateField()
    insurance_expiry_date = models.DateField()

    def __str__(self):
        return self.plate
