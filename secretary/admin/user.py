from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import StackedInline, TabularInline
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    ChoicesCheckboxFilter,
    ChoicesDropdownFilter,
    RangeDateFilter,
)
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from core.admin import DefaultAdmin
from secretary.enums import DrivingLicenseType
from secretary.models import Contact, EmergencyContact, User, Vehicle


class ContactInline(TabularInline):
    model = Contact
    extra = 0
    tab = True


class EmergencyContactInline(TabularInline):
    model = EmergencyContact
    extra = 0
    tab = True


class VehicleInline(StackedInline):
    model = Vehicle
    extra = 0
    tab = True


@admin.register(User)
class UserAdmin(BaseUserAdmin, DefaultAdmin):
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    form = UserChangeForm
    inlines = [ContactInline, EmergencyContactInline, VehicleInline]
    list_display = (
        "first_name",
        "last_name",
        "title",
        "charter",
        "blood_type",
        "date_joined",
        "display_contact",
        "display_emergency_contact",
        "display_driving_license_type",
        "display_vehicle",
        "sponsor",
        "is_active",
    )
    list_filter = [
        ("charter", ChoicesCheckboxFilter),
        ("blood_type", ChoicesDropdownFilter),
        ("driving_license_type", ChoicesDropdownFilter),
        ("sponsor", ChoicesDropdownFilter),
        ("is_active", BooleanRadioFilter),
        ("is_superuser", BooleanRadioFilter),
        ("date_joined", RangeDateFilter),
    ]
    ordering = ("created_at", "-is_active")
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "title",
        "sponsor__first_name",
        "sponsor__last_name",
    )
    fieldsets = (
        (
            "Personal Info",
            {
                "classes": ["tab"],
                "fields": ("first_name", "last_name", "email", "password"),
            },
        ),
        (
            "Membership Info",
            {
                "classes": ["tab"],
                "fields": (
                    "date_joined",
                    "charter",
                    "title",
                    "driving_license_type",
                    "sponsor",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Health Info",
            {
                "classes": ["tab"],
                "fields": (
                    "birth_date",
                    "blood_type",
                    "allergies",
                    "medical_conditions",
                    "medications",
                ),
            },
        ),
        (
            "Permissions",
            {
                "classes": ["tab"],
                "fields": (
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Important dates",
            {"classes": ["tab"], "fields": ("last_login", "created_at", "updated_at")},
        ),
    )
    add_fieldsets = ((None, {"fields": ("email", "password1", "password2")}),)

    @display(description="Contact", boolean=True)
    def display_contact(self, obj):
        return obj.contacts.exists()

    @display(description="Emergency Contact", boolean=True)
    def display_emergency_contact(self, obj):
        return obj.emergency_contacts.count() > 1

    @display(description="Vehicle", boolean=True)
    def display_vehicle(self, obj):
        return obj.vehicles.exists()

    @display(
        description="License",
        label={
            DrivingLicenseType.NONE: "danger",
            DrivingLicenseType.B: "warning",
            DrivingLicenseType.A: "success",
            DrivingLicenseType.A2: "secondary",
            DrivingLicenseType.A1: "secondary",
            DrivingLicenseType.M: "secondary",
        },
    )
    def display_driving_license_type(self, obj):
        return obj.driving_license_type

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(charter=request.user.charter)
        if request.user.is_superuser or request.user.has_perm("secretary.view_user"):
            return qs
        return qs.filter(pk=request.user.pk)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm("secretary.change_user"):
            return ("last_login", "created_at", "updated_at")
        return (
            "date_joined",
            "charter",
            "title",
            "sponsor",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
            "created_at",
            "updated_at",
        )

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm("secretary.view_user"):
            return True
        if obj is not None and obj.pk != request.user.pk:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm("secretary.change_user"):
            return True
        if obj is not None and obj.pk != request.user.pk:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.has_perm("secretary.add_user"):
            return True
        return False
