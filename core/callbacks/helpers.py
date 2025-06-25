from django.db import models

from core.callbacks.utils import one_year_ago
from secretary.enums import EventTypes
from treasury.enums import StatementType
from treasury.models import Dues, Statement


def get_ride_count(user):
    """Kullanıcının katıldığı sürüş sayısını döndürür."""
    count = user.attended_events.filter(type=EventTypes.RIDE).count()
    return count if count else "No Ride"


def get_debt_count(user) -> tuple:
    """Kullanıcının toplam borcunu ve borç adedini döndürür."""
    unpaid_dues = user.dues.filter(is_paid=False)
    total_debt = unpaid_dues.aggregate(total=models.Sum("amount"))["total"]
    debt_count = unpaid_dues.count()
    total_debt_str = f"{total_debt} TL" if total_debt else "No Debt"
    debt_count_str = f"{debt_count} Time" if debt_count else "All Clear"
    return total_debt_str, debt_count_str


def get_penalty_count(user):
    """Kullanıcının son bir yıldaki ceza sayısını döndürür."""
    count = user.disciplines.filter(date__gte=one_year_ago(), is_guilty=True).count()
    return count if count else "All Clear"


def get_balance():
    """Kasadaki toplam bakiyeyi döndürür."""
    incomes = (
        Statement.objects.filter(type=StatementType.INCOME).aggregate(
            total=models.Sum("amount")
        )["total"]
        or 0
    )
    paid_dues = (
        Dues.objects.filter(is_paid=True).aggregate(total=models.Sum("amount"))["total"]
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
    """Kullanıcıların ardışık katılmadığı etkinlik/sürüş serilerini hesaplar."""
    absence_data = []

    for u in users:
        user_id = u["id"]
        full_name = user_id_to_name[user_id]
        attended_ids = user_attendance.get(user_id, set())
        current_streak = max_streak = 0
        for eid in all_ids:
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
    """Etkinlik yoklama tablosu döndürür."""
    rows = _get_absence_table(users, user_attendance, all_events, user_id_to_name, min_streak=4)
    return {"headers": ["User", "Streak"], "rows": rows}


def get_ride_absence_table(users, user_attendance, all_rides, user_id_to_name):
    """Sürüş yoklama tablosu döndürür."""
    rows = _get_absence_table(users, user_attendance, all_rides, user_id_to_name)
    return {"headers": ["User", "Streak"], "rows": rows}


def get_due_table(users, user_id_to_dues, user_id_to_name):
    """Kullanıcıların ödenmemiş aidat sayılarını döndürür."""
    due_data = [
        [
            user_id_to_name[u["id"]],
            sum(1 for d in user_id_to_dues.get(u["id"], []) if not d.is_paid),
        ]
        for u in users
        if sum(1 for d in user_id_to_dues.get(u["id"], []) if not d.is_paid) > 0
    ]
    due_data.sort(key=lambda x: x[1], reverse=True)
    return {"headers": ["User", "Total"], "rows": due_data}


def get_contact_table(users, contact_count, emergency_contact_count, user_id_to_name):
    """Kullanıcıların iletişim ve acil iletişim eksiklerini döndürür."""
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
    return {"headers": ["User", "Contacts", "Emergency Contacts"], "rows": contact_data}


def get_motorcycle_table(all_vehicles, user_id_to_name, user_id_to_license):
    """Kullanıcıların motosiklet bilgilerini döndürür."""
    motorcycle_data = [
        [user_id_to_name[v.user_id], user_id_to_license[v.user_id], v.engine_capacity]
        for v in all_vehicles
        if v.user_id in user_id_to_name
    ]
    motorcycle_data.sort(key=lambda x: x[2], reverse=True)
    return {"headers": ["User", "License", "CC"], "rows": motorcycle_data}
