from datetime import timedelta

from django.utils import timezone


def has_permission(user):
    return (
        user.is_superuser
        or user.has_perm("treasury.view_dues")
        or user.has_perm("treasury.view_statements")
        or user.has_perm("secretary.view_events")
        or user.has_perm("sergeant_at_arms.view_disciplines")
    )


def one_year_ago():
    return timezone.now() - timedelta(days=365)
