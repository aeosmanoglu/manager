from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import StackedInline, TabularInline
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    ChoicesCheckboxFilter,
    ChoicesDropdownFilter,
    RangeDateFilter,
    RangeNumericFilter,
)
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from core.admin import DefaultAdmin
from secretary.enums import DrivingLicenseType, EventTypes
from secretary.models import Contact, EmergencyContact, Event, User, Vehicle

admin.site.unregister(Group)


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
    readonly_fields = ("last_login", "created_at", "updated_at")
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
        return obj.get_driving_license_type_display()


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, DefaultAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(DefaultAdmin):
    list_display = ("user", "type", "phone", "address", "what3words")
    ordering = ("user", "type")
    search_fields = ("user__first_name", "user__last_name")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(DefaultAdmin):
    list_display = ("user", "name", "phone", "relationship")
    ordering = ("user",)
    search_fields = ("user__first_name", "user__last_name", "name")


@admin.register(Vehicle)
class VehicleAdmin(DefaultAdmin):
    list_display = (
        "user",
        "plate",
        "brand",
        "model",
        "year",
        "display_engine_capacity",
        "last_maintenance_date",
        "inspection_expiry_date",
        "insurance_expiry_date",
    )
    list_filter = [
        ("year", RangeNumericFilter),
        ("engine_capacity", RangeNumericFilter),
        ("last_maintenance_date", RangeDateFilter),
        ("inspection_expiry_date", RangeDateFilter),
        ("insurance_expiry_date", RangeDateFilter),
    ]
    search_fields = ("user__first_name", "user__last_name", "plate", "brand", "model")

    @display(description="Engine Capacity")
    def display_engine_capacity(self, obj):
        return f"{obj.engine_capacity} cc"


@admin.register(Event)
class EventAdmin(DefaultAdmin):
    filter_horizontal = ("attendance",)
    list_display = (
        "display_type",
        "name",
        "date_time",
        "location",
        "charter",
        "display_attendance",
        "display_attendance_rate",
        "display_has_training",
        "has_ride",
    )
    fieldsets = (
        (
            "Event Info",
            {
                "classes": ["tab"],
                "fields": (
                    "type",
                    "name",
                    "date_time",
                    "location",
                    "charter",
                    "agenda",
                ),
            },
        ),
        (
            "Attendance",
            {
                "classes": ["tab"],
                "fields": ("attendance",),
            },
        ),
        (
            "Decisions",
            {
                "classes": ["tab"],
                "fields": ("decisions", "training_note"),
            },
        ),
        (
            "Ride",
            {
                "classes": ["tab"],
                "fields": ("has_ride", "destination", "ride_note"),
            },
        ),
    )

    @display(description="Attendance")
    def display_attendance(self, obj):
        return obj.attendance.count()

    @display(description="Attendance Rate")
    def display_attendance_rate(self, obj):
        total_active_users = obj.attendance.model.objects.filter(
            charter=obj.charter, is_active=True
        ).count()
        if total_active_users > 0:
            return f"{obj.attendance.count() / total_active_users * 100:.0f}%"
        return "0%"

    @display(description="Has Training", boolean=True)
    def display_has_training(self, obj):
        return obj.training_note != ""

    @display(
        description="Type",
        label={
            EventTypes.MEETING: "info",
            EventTypes.RIDE: "success",
            EventTypes.OTHER: "secondary",
        },
    )
    def display_type(self, obj):
        return obj.type
