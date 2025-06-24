import tomllib
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone

from secretary.enums import EventTypes


def _get_project_version():
    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def environment_callback(_):
    version = _get_project_version()
    return [version, "success" if not settings.DEBUG else "warning"]


def dashboard_callback(request, context):
    user = request.user

    # Katıldığı ride tipi event sayısı
    ride_count = user.attended_events.filter(type=EventTypes.RIDE).count() or "No Ride"

    # Ödenmemiş borçların toplamı ve adedi
    unpaid_dues = user.dues.filter(is_paid=False)
    total_debt = unpaid_dues.aggregate(total=models.Sum("amount"))["total"]
    debt_count = unpaid_dues.count()
    total_debt_label = f"{debt_count} Time" if debt_count > 0 else None
    total_debt_display = "No Debt" if total_debt is None else f"{total_debt} TL"

    # Son 1 yıl içinde suçlu bulunduğu disiplin cezası sayısı
    one_year_ago = timezone.now().date().replace(year=timezone.now().year - 1)
    discipline_count = user.disciplines.filter(
        date__gte=one_year_ago, is_guilty=True
    ).count()
    discipline_count = discipline_count if discipline_count > 0 else "All Clear"

    context.update(
        {
            "user": user,
            "ride_count": ride_count,
            "total_debt_display": total_debt_display,
            "total_debt_label": total_debt_label,
            "discipline_count": discipline_count,
        }
    )
    return context
