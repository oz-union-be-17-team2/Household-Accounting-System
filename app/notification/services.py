from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from app.notification.models import Notification

User = get_user_model()


def mark_notification_as_read(notification: Notification) -> Notification:
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])
    return notification


def delete_notification(notification: Notification):
    notification.delete()
    return None


def hard_delete_old_notification(*, days: int = 30):
    Notification.all_objects.filter(deleted_at__lt=timezone.now() - timedelta(days=days)).delete()
