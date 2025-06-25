from treasury.models import Dues


def dues_callback(_):
    return Dues.objects.filter(is_paid=False).count()
