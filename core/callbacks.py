import tomllib
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils import timezone

from secretary.enums import EventTypes
from secretary.models import Contact, EmergencyContact, Event, User, Vehicle
from treasury.enums import StatementType
from treasury.models import Dues, Statement


def _get_project_version():
    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def environment_callback(_):
    version = _get_project_version()
    return [version, "success" if not settings.DEBUG else "warning"]


def dues_badge_callback(_):
    return Dues.objects.filter(is_paid=False).count()


def dashboard_callback(request, context):
    user = request.user
    one_year_ago = timezone.now().date().replace(year=timezone.now().year - 1)

    # Katıldığı ride tipi event sayısı
    ride_count_title = (
        user.attended_events.filter(type=EventTypes.RIDE).count() or "No Ride"
    )

    # Ödenmemiş borçların toplamı ve adedi
    unpaid_dues = user.dues.filter(is_paid=False)
    total_debt = unpaid_dues.aggregate(total=models.Sum("amount"))["total"]
    debt_count = unpaid_dues.count()
    total_debt_label = f"{debt_count} Time" if debt_count > 0 else None
    total_debt_title = "No Debt" if total_debt is None else f"{total_debt} TL"

    # Son 1 yıl içinde suçlu bulunduğu disiplin cezası sayısı
    discipline_count = user.disciplines.filter(
        date__gte=one_year_ago, is_guilty=True
    ).count()
    discipline_count_title = discipline_count if discipline_count > 0 else "All Clear"

    # Member
    is_member = (
        user.has_perm("treasury.view_dues")
        or user.has_perm("treasury.view_statements")
        or user.has_perm("secretary.view_events")
        or user.has_perm("sergeant_at_arms.view_disciplines")
    )

    # Balance
    balance = None
    if is_member:
        paid_dues = Dues.objects.filter(is_paid=True).aggregate(
            total=models.Sum("amount")
        )["total"]
        expenses = Statement.objects.filter(type=StatementType.EXPENSE).aggregate(
            total=models.Sum("amount")
        )["total"]
        incomes = Statement.objects.filter(type=StatementType.INCOME).aggregate(
            total=models.Sum("amount")
        )["total"]
        balance = paid_dues + incomes - expenses
    balance_title = f"{balance} TL"

    # Tables
    event_table = None
    ride_table = None
    due_table = None
    contact_table = None
    motorcycle_table = None
    if is_member:
        all_events = list(
            Event.objects.filter(date_time__gte=one_year_ago)
            .order_by("date_time")
            .values_list("id", flat=True)
        )
        all_rides = list(
            Event.objects.filter(type=EventTypes.RIDE, date_time__gte=one_year_ago)
            .order_by("date_time")
            .values_list("id", flat=True)
        )
        users = list(
            User.objects.filter(is_active=True).values(
                "id", "first_name", "last_name", "driving_license_type"
            )
        )
        user_id_to_name = {
            u["id"]: f"{u['first_name']} {u['last_name']}" for u in users
        }
        user_id_to_license = {u["id"]: u["driving_license_type"] for u in users}

        # All events for all users
        user_attendance = defaultdict(set)
        for user_id, event_id in User.attended_events.through.objects.values_list(
            "user_id", "event_id"
        ):
            user_attendance[user_id].add(event_id)

        # All dues for all users
        all_dues = Dues.objects.filter(date__gte=one_year_ago)
        user_id_to_dues = defaultdict(list)
        for d in all_dues:
            user_id_to_dues[d.user_id].append(d)

        # All contacts and emergency contacts for all users
        all_contacts = Contact.objects.values("user_id")
        all_emergency_contacts = EmergencyContact.objects.values("user_id")
        contact_count = defaultdict(int)
        emergency_contact_count = defaultdict(int)
        for c in all_contacts:
            contact_count[c["user_id"]] += 1
        for ec in all_emergency_contacts:
            emergency_contact_count[ec["user_id"]] += 1

        # All vehicles for all users
        all_vehicles = Vehicle.objects.select_related("user").all()
        motorcycle_data = []
        for v in all_vehicles:
            if v.user_id in user_id_to_name:
                motorcycle_data.append(
                    [
                        user_id_to_name[v.user_id],
                        user_id_to_license[v.user_id],
                        v.engine_capacity,
                    ]
                )
        motorcycle_data.sort(key=lambda x: x[2], reverse=True)

        event_absence_data = []
        ride_absence_data = []
        due_data = []
        contact_data = []

        for u in users:
            user_id = u["id"]
            full_name = user_id_to_name[user_id]
            attended_ids = user_attendance.get(user_id, set())
            dues = user_id_to_dues.get(user_id, [])
            c_count = contact_count.get(user_id, 0)
            ec_count = emergency_contact_count.get(user_id, 0)

            # Total unpaid dues
            unpaid_dues_count = sum(1 for d in dues if not d.is_paid)
            if unpaid_dues_count > 0:
                due_data.append([full_name, unpaid_dues_count])

            # Event streak
            current_streak = max_streak = 0
            for event_id in all_events:
                if event_id not in attended_ids:
                    current_streak += 1
                    if current_streak > max_streak:
                        max_streak = current_streak
                else:
                    current_streak = 0
            if max_streak > 1:
                event_absence_data.append([full_name, max_streak])

            # Ride streak
            current_streak = max_streak = 0
            for ride_id in all_rides:
                if ride_id not in attended_ids:
                    current_streak += 1
                    if current_streak > max_streak:
                        max_streak = current_streak
                else:
                    current_streak = 0
            if max_streak > 1:
                ride_absence_data.append([full_name, max_streak])

            # Eksik contact/emergency contact
            if c_count < 1 or ec_count < 2:
                contact_data.append([full_name, c_count, ec_count])

        event_absence_data.sort(key=lambda x: x[1], reverse=True)
        ride_absence_data.sort(key=lambda x: x[1], reverse=True)
        due_data.sort(key=lambda x: x[1], reverse=True)
        contact_data.sort(key=lambda x: (x[1], x[2]))

        event_table = {
            "headers": ["User", "Streak"],
            "rows": event_absence_data,
        }
        ride_table = {
            "headers": ["User", "Streak"],
            "rows": ride_absence_data,
        }
        due_table = {
            "headers": ["User", "Total"],
            "rows": due_data,
        }
        contact_table = {
            "headers": ["User", "Contacts", "Emergency Contacts"],
            "rows": contact_data,
        }
        motorcycle_table = {
            "headers": ["User", "License", "CC"],
            "rows": motorcycle_data,
        }

    context.update(
        {
            "user": user,
            "ride_count_title": ride_count_title,
            "total_debt_title": total_debt_title,
            "total_debt_label": total_debt_label,
            "discipline_count_title": discipline_count_title,
            "is_member": is_member,
            "balance_title": balance_title,
            "event_table": event_table,
            "ride_table": ride_table,
            "due_table": due_table,
            "contact_table": contact_table,
            "contact_table_footer": f"Total {len(contact_data)}",
            "motorcycle_table": motorcycle_table,
            "motorcycle_table_footer": f"Total {len(motorcycle_data)}",
        }
    )
    return context
