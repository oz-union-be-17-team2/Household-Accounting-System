from celery import shared_task

from app.notification.services import hard_delete_old_notification


@shared_task
def hard_delete_old_notification_task():
    hard_delete_old_notification(days=30)
