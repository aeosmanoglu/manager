from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from unfold.admin import StackedInline, TabularInline
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    ChoicesCheckboxFilter,
    ChoicesDropdownFilter,
    RangeDateFilter,
)
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from core import settings
from core.admin import DefaultAdmin
from secretary.enums import DrivingLicenseType, Titles
from secretary.models import Contact, EmergencyContact, User, Vehicle
from treasury.models import Dues, Period


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
    actions = ["add_dues"]
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
                    # "user_permissions",
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

    @action(
        description="Add dues to selected users",
        icon="paid",
        permissions=["add_dues"],
    )
    def add_dues(self, request, queryset):
        last_period = Period.objects.order_by("-year", "-month").first()
        if not last_period:
            self.message_user(request, "No period found!", level=messages.ERROR)
            return
        for user in queryset:
            if user.title == Titles.HANGROUND:
                amount = settings.HANGROUND_DUE_AMOUNT
            elif user.title == Titles.PROSPECT:
                amount = settings.PROSPECT_DUE_AMOUNT
            elif user.title >= 40 and user.title < 50:
                amount = settings.MEMBER_DUE_AMOUNT
            else:
                continue
            Dues.objects.create(
                user=user,
                period=last_period,
                amount=amount,
                date=timezone.now(),
                description="Toplu eklenen aidat",
            )
        self.message_user(
            request,
            f"{queryset.count()} user(s) added dues for {last_period} period.",
            level=messages.SUCCESS,
        )

    def has_add_dues_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.has_perm("treasury.add_dues")

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
