from django.db import models
from django.utils.translation import gettext_lazy as _

from core.callbacks.utils import one_year_ago
from secretary.enums import EventTypes
from treasury.enums import StatementType
from treasury.models import Due, Statement


def get_ride_count(user):
    count = user.attended_events.filter(type=EventTypes.RIDE).count()
    return count if count else _("No Ride")


def get_debt_count(user):
    unpaid_dues = user.dues.filter(is_paid=False)
    total_debt = unpaid_dues.aggregate(total=models.Sum("amount"))["total"]
    debt_count = unpaid_dues.count()
    total_debt_str = f"{total_debt} TL" if total_debt else _("No Debt")
    debt_count_str = (
        _("%(count)s time") % {"count": debt_count} if debt_count else _("All Clear")
    )
    return total_debt_str, debt_count_str


def get_penalty_count(user):
    count = user.disciplines.filter(date__gte=one_year_ago(), is_guilty=True).count()
    return count if count else _("All Clear")


def get_balance():
    incomes = (
        Statement.objects.filter(type=StatementType.INCOME).aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )
    paid_dues = (
        Due.objects.filter(is_paid=True).aggregate(total=models.Sum("amount"))["total"]
        or 0
    )
    expenses = (
        Statement.objects.filter(type=StatementType.EXPENSE).aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )
    return f"{incomes + paid_dues - expenses} TL"


def _get_absence_table(users, user_attendance, all_ids, user_id_to_name, min_streak=2):
    absence_data = []

    for u in users:
        user_id = u["id"]
        full_name = user_id_to_name[user_id]
        attended_ids = user_attendance.get(user_id, set())
        # Kullanıcının üyelik tarihinden sonraki etkinlik/sürüş ID'lerini filtrele
        joined_date = u.get("date_joined")
        filtered_ids = (
            [
                eid
                for eid in all_ids
                if hasattr(eid, "date_time") and eid.date_time >= joined_date
            ]
            if joined_date
            else all_ids
        )
        # Eğer all_ids sadece id ise, etkinliklerin tarihine ulaşmak için ek bilgi gerekebilir. Ancak dashboard.py'de all_ids sadece id listesi olarak geliyor.
        # Bu yüzden, all_ids'nin Event objesi değil, id listesi olduğunu varsayarsak, all_ids'nin sırası tarih sırası ile aynı.
        # O yüzden, Event objelerinin tarihleriyle eşleştirmek için ek bir yapı gerekebilir. Ancak mevcut kodda, all_ids zaten bir yıl öncesinden başlıyor.
        # Yine de, date_joined'dan önceki etkinlikleri atlamak için, all_ids'nin indeksini bulup oradan başlatabiliriz.
        # Bunun için, Event'lerin tarih sırasına göre id listesi olduğunu varsayarsak:
        if joined_date:
            # all_ids'nin sırası tarih sırası ile aynı olduğu için, kullanıcının üyelik tarihinden sonraki ilk etkinliği bul
            from secretary.models import Event

            event_dates = list(
                Event.objects.filter(id__in=all_ids)
                .order_by("date_time")
                .values_list("id", "date_time")
            )
            filtered_ids = [eid for eid, dt in event_dates if dt.date() >= joined_date]
        else:
            filtered_ids = all_ids
        current_streak = max_streak = 0
        for eid in filtered_ids:
            if eid not in attended_ids:
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
            else:
                current_streak = 0
        if max_streak >= min_streak:
            absence_data.append([full_name, max_streak])
    absence_data.sort(key=lambda x: x[1], reverse=True)
    return absence_data


def get_event_absence_table(users, user_attendance, all_events, user_id_to_name):
    rows = _get_absence_table(
        users, user_attendance, all_events, user_id_to_name, min_streak=4
    )
    return {"headers": [_("User"), _("Streak")], "rows": rows}


def get_ride_absence_table(users, user_attendance, all_rides, user_id_to_name):
    rows = _get_absence_table(users, user_attendance, all_rides, user_id_to_name)
    return {"headers": [_("User"), _("Streak")], "rows": rows}


def get_due_table(users, user_id_to_dues, user_id_to_name):
    due_data = [
        [
            user_id_to_name[u["id"]],
            sum(1 for d in user_id_to_dues.get(u["id"], []) if not d.is_paid),
        ]
        for u in users
        if sum(1 for d in user_id_to_dues.get(u["id"], []) if not d.is_paid) > 0
    ]
    due_data.sort(key=lambda x: x[1], reverse=True)
    return {"headers": [_("User"), _("Total")], "rows": due_data}


def get_contact_table(users, contact_count, emergency_contact_count, user_id_to_name):
    contact_data = [
        [
            user_id_to_name[u["id"]],
            contact_count.get(u["id"], 0),
            emergency_contact_count.get(u["id"], 0),
        ]
        for u in users
        if contact_count.get(u["id"], 0) < 1
        or emergency_contact_count.get(u["id"], 0) < 2
    ]
    contact_data.sort(key=lambda x: (x[1], x[2]))
    return {
        "headers": [_("User"), _("Contacts"), _("Emergency Contacts")],
        "rows": contact_data,
    }


def get_motorcycle_table(all_vehicles, user_id_to_name, user_id_to_license):
    motorcycle_data = [
        [
            user_id_to_name[v.user_id],
            user_id_to_license[v.user_id],
            v.engine_capacity,
            v.is_active,
        ]
        for v in all_vehicles
        if v.user_id in user_id_to_name
    ]
    motorcycle_data.sort(key=lambda x: (not x[3], -x[2]))
    return {
        "headers": [_("User"), _("License"), "CC", _("Active")],
        "rows": motorcycle_data,
    }
