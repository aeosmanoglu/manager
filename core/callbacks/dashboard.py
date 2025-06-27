from collections import defaultdict

from core.callbacks.helpers import (
    get_balance,
    get_contact_table,
    get_debt_count,
    get_due_table,
    get_event_absence_table,
    get_motorcycle_table,
    get_penalty_count,
    get_ride_absence_table,
    get_ride_count,
)
from core.callbacks.utils import has_permission, one_year_ago
from secretary.enums import EventTypes
from secretary.models import Contact, EmergencyContact, Event, User, Vehicle
from treasury.models import Dues


def get_all_users():
    return list(
        User.objects.filter(is_active=True).values(
            "id", "first_name", "last_name", "driving_license_type", "date_joined"
        )
    )


def get_user_id_maps(users):
    user_id_to_name = {u["id"]: f"{u['first_name']} {u['last_name']}" for u in users}
    user_id_to_license = {u["id"]: u["driving_license_type"] for u in users}
    return user_id_to_name, user_id_to_license


def get_user_attendance():
    user_attendance = defaultdict(set)
    for user_id, event_id in User.attended_events.through.objects.values_list(
        "user_id", "event_id"
    ):
        user_attendance[user_id].add(event_id)
    return user_attendance


def get_user_dues():
    all_dues = Dues.objects.filter(date__gte=one_year_ago())
    user_id_to_dues = defaultdict(list)
    for d in all_dues:
        user_id_to_dues[d.user_id].append(d)
    return user_id_to_dues


def get_contact_counts():
    all_contacts = Contact.objects.values("user_id")
    all_emergency_contacts = EmergencyContact.objects.values("user_id")
    contact_count = defaultdict(int)
    emergency_contact_count = defaultdict(int)
    for c in all_contacts:
        contact_count[c["user_id"]] += 1
    for ec in all_emergency_contacts:
        emergency_contact_count[ec["user_id"]] += 1
    return contact_count, emergency_contact_count


def get_all_vehicles():
    return Vehicle.objects.select_related("user").all()


def get_event_and_ride_ids():
    all_events = list(
        Event.objects.filter(date_time__gte=one_year_ago())
        .order_by("date_time")
        .values_list("id", flat=True)
    )
    all_rides = list(
        Event.objects.filter(type=EventTypes.RIDE, date_time__gte=one_year_ago())
        .order_by("date_time")
        .values_list("id", flat=True)
    )
    return all_events, all_rides


def build_dashboard_context():
    """Yönetici paneli için gerekli tüm tablo ve özet verileri hazırlar."""
    users = get_all_users()
    user_id_to_name, user_id_to_license = get_user_id_maps(users)
    user_attendance = get_user_attendance()
    user_id_to_dues = get_user_dues()
    contact_count, emergency_contact_count = get_contact_counts()
    all_vehicles = get_all_vehicles()
    all_events, all_rides = get_event_and_ride_ids()

    event_table = get_event_absence_table(
        users, user_attendance, all_events, user_id_to_name
    )
    ride_table = get_ride_absence_table(
        users, user_attendance, all_rides, user_id_to_name
    )
    due_table = get_due_table(users, user_id_to_dues, user_id_to_name)
    contact_table = get_contact_table(
        users, contact_count, emergency_contact_count, user_id_to_name
    )
    motorcycle_table = get_motorcycle_table(
        all_vehicles, user_id_to_name, user_id_to_license
    )

    return {
        "balance_title": get_balance(),
        "event_table": event_table,
        "ride_table": ride_table,
        "due_table": due_table,
        "contact_table": contact_table,
        "contact_table_footer": f"Total {len(contact_table['rows']) if contact_table else 0}",
        "motorcycle_table": motorcycle_table,
        "motorcycle_table_footer": f"Total {len(motorcycle_table['rows']) if motorcycle_table else 0}",
    }


def callback(request, context):
    user = request.user
    is_member = has_permission(user)

    if is_member:
        dashboard_data = build_dashboard_context()
        context.update(dashboard_data)

    else:
        context["balance_title"] = None
        context["event_table"] = None
        context["ride_table"] = None
        context["due_table"] = None
        context["contact_table"] = None
        context["contact_table_footer"] = "Total 0"
        context["motorcycle_table"] = None
        context["motorcycle_table_footer"] = "Total 0"

    context.update(
        {
            "user": user,
            "ride_count_title": get_ride_count(user),
            "total_debt_title": get_debt_count(user)[0],
            "total_debt_label": get_debt_count(user)[1],
            "penalty_count_title": get_penalty_count(user),
            "is_member": is_member,
        }
    )
    return context
