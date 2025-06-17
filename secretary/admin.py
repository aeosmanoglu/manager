from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from secretary.models import Contact, EmergencyContact, User, Vehicle

admin.site.unregister(Group)


class ContactInline(TabularInline):
    model = Contact
    extra = 0


class EmergencyContactInline(TabularInline):
    model = EmergencyContact
    extra = 0


class VehicleInline(StackedInline):
    model = Vehicle
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    compressed_fields = True
    form = UserChangeForm
    list_display = ("first_name", "last_name", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    ordering = ("first_name",)
    readonly_fields = ("last_login", "created_at", "updated_at")
    search_fields = ("email", "first_name", "last_name")
    inlines = [ContactInline, EmergencyContactInline, VehicleInline]
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


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    compressed_fields = True
    list_display = ("user", "type", "phone", "address", "what3words")
    ordering = ("user", "type")
    search_fields = ("user__first_name", "user__last_name")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(ModelAdmin):
    compressed_fields = True
    list_display = ("user", "name", "phone", "relationship")
    ordering = ("user",)
    search_fields = ("user__first_name", "user__last_name", "name")


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    compressed_fields = True
