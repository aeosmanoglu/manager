from treasury.models import Due


def dues_callback(_):
    return Due.objects.filter(is_paid=False).count()
