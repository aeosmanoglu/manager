from django.contrib import admin

from core.admin import DefaultAdmin
from secretary.models import EmergencyContact


@admin.register(EmergencyContact)
class EmergencyContactAdmin(DefaultAdmin):
    list_display = ("user", "name", "phone", "relationship")
    ordering = ("user",)
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("user__first_name", "user__last_name", "name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm(
            "secretary.view_emergencycontact"
        ):
            return qs
        return qs.filter(user=request.user)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm(
            "secretary.view_emergencycontact"
        ):
            return True
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm(
            "secretary.change_emergencycontact"
        ):
            return True
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.has_perm(
            "secretary.delete_emergencycontact"
        ):
            return True
        if obj is not None and obj.user != request.user:
            return False
        return True

    def has_add_permission(self, request):
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            UserModel = self.model._meta.get_field("user").related_model
            if (
                request.user.is_superuser
                or request.user.has_perm("secretary.add_emergencycontact")
                or request.user.has_perm("secretary.change_emergencycontact")
            ):
                kwargs["queryset"] = UserModel.objects.all()
            else:
                kwargs["queryset"] = UserModel.objects.filter(pk=request.user.pk)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
