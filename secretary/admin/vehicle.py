from django.contrib import admin
from unfold.contrib.filters.admin import (
    BooleanRadioFilter,
    RangeDateFilter,
    RangeNumericFilter,
)
from unfold.decorators import display

from core.admin import DefaultAdmin
from secretary.models import Vehicle


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
        "is_active",
    )
    list_filter = [
        ("year", RangeNumericFilter),
        ("engine_capacity", RangeNumericFilter),
        ("last_maintenance_date", RangeDateFilter),
        ("inspection_expiry_date", RangeDateFilter),
        ("insurance_expiry_date", RangeDateFilter),
        ("is_active", BooleanRadioFilter),
    ]
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("user__first_name", "user__last_name", "plate", "brand", "model")

    @display(description="Engine Capacity")
    def display_engine_capacity(self, obj):
        return f"{obj.engine_capacity} cc"

    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(user__charter=request.user.charter)
        if request.user.is_superuser or request.user.has_perm("secretary.view_vehicle"):
            return qs
        return qs.filter(user=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm("secretary.view_vehicle"):
            return True
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm(
            "secretary.change_vehicle"
        ):
            return True
        if obj is not None and obj.pk != request.user.pk:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm(
            "secretary.delete_vehicle"
        ):
            return True
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_add_permission(self, request):
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if not (
                request.user.is_superuser
                or request.user.has_perm("secretary.add_contact")
                or request.user.has_perm("secretary.change_contact")
            ):
                kwargs["queryset"] = kwargs.get(
                    "queryset", self.model._meta.get_field("user").related_model.objects
                ).filter(pk=request.user.pk)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
