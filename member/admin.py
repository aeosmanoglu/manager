from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from member.models import Contact, EmergencyContact, User, Vehicle

admin.site.unregister(Group)


class ContactInline(TabularInline):
    model = Contact
    extra = 1


class EmergencyContactInline(TabularInline):
    model = EmergencyContact
    extra = 2


class VehicleInline(StackedInline):
    model = Vehicle
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    compressed_fields = True
    form = UserChangeForm
    inlines = [ContactInline, EmergencyContactInline, VehicleInline]
    list_display = ("first_name", "last_name", "status", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "status")
    ordering = ("first_name",)
    readonly_fields = ("last_login", "created_at", "updated_at")
    search_fields = ("email", "first_name", "last_name")

    fieldsets = (
        (
            "Personal Info",
            {
                "fields": ("first_name", "last_name", "email", "password"),
            },
        ),
        (
            "Membership Info",
            {
                "fields": (
                    "date_joined",
                    "driving_license_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (
            "Health Info",
            {
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


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    pass
