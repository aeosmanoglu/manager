from django.contrib import admin
from unfold.decorators import display

from core.admin import DefaultAdmin
from secretary.enums import EventTypes
from secretary.models import Event


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
    readonly_fields = ("created_at", "updated_at")
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
        (
            "Important dates",
            {"classes": ["tab"], "fields": ("created_at", "updated_at")},
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


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(charter=request.user.charter)
