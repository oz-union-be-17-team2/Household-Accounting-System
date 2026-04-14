from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from app.notification.exceptions import NotificationNotFoundError
from app.notification.models import Notification

User = get_user_model()


def get_notification_list(*, user: User) -> QuerySet[Notification]:
    return Notification.objects.select_related("user").filter(user=user).order_by("-created_at")


def get_notification_detail(*, user: User, noti_pk: int) -> Notification:
    try:
        return Notification.objects.select_related("user").get(user=user, pk=noti_pk)
    except Notification.DoesNotExist:
        raise NotificationNotFoundError("알림을 찾을 수 없습니다.") from None
