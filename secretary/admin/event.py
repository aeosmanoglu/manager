from django.contrib import admin
from django.utils.translation import gettext_lazy as _
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
        "display_attendance",
        "display_attendance_rate",
        "display_has_training",
        "has_ride",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            _("Event Info"),
            {
                "classes": ["tab"],
                "fields": (
                    "type",
                    "name",
                    "date_time",
                    "location",
                    "agenda",
                ),
            },
        ),
        (
            _("Attendance"),
            {
                "classes": ["tab"],
                "fields": ("attendance",),
            },
        ),
        (
            _("Decisions"),
            {
                "classes": ["tab"],
                "fields": ("decisions", "training_note"),
            },
        ),
        (
            _("Ride"),
            {
                "classes": ["tab"],
                "fields": ("has_ride", "destination", "ride_note"),
            },
        ),
        (
            _("Important dates"),
            {"classes": ["tab"], "fields": ("created_at", "updated_at")},
        ),
    )

    @display(description=_("Attendance"))
    def display_attendance(self, obj):
        return obj.attendance.count()

    @display(description=_("Attendance Rate"))
    def display_attendance_rate(self, obj):
        total_active_users = obj.attendance.model.objects.filter(is_active=True).count()
        if total_active_users > 0:
            return f"{obj.attendance.count() / total_active_users * 100:.0f}%"
        return "0%"

    @display(description=_("Has Training"), boolean=True)
    def display_has_training(self, obj):
        return obj.training_note != ""

    @display(
        description=_("Type"),
        label={
            EventTypes.MEETING.label: "info",
            EventTypes.RIDE.label: "success",
            EventTypes.OTHER.label: "secondary",
        },
    )
    def display_type(self, obj):
        return obj.get_type_display()
