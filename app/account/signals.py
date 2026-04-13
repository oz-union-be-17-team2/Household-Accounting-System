from django.db.models.signals import post_save
from django.dispatch import receiver

from app.account.models import Account, BalanceAlert
from app.notification.models import Notification
from core.utils import send_email

THRESHOLDS = sorted(
    [
        10_000_000,
        100_000_000,
        1_000_000_000,
    ]
)


@receiver(post_save, sender=Account)
def alert_balance(sender, instance, **kwargs):
    instance = Account.objects.select_related("user").get(pk=instance.pk)
    for threshold in THRESHOLDS:
        if instance.balance < threshold:
            break
        _, is_create = BalanceAlert.objects.get_or_create(account=instance, threshold=threshold)
        if is_create:
            Notification.objects.create(
                user=instance.user,
                message=f"[알림]{instance.user.nickname}님의 {instance.name}의 잔액이 "
                f"{threshold}원이 넘었습니다. 축하합니다.",
            )

            # if settings.DEBUG:
            to_email = "netrunnerr25@gmail.com"  # os.environ.get("EMAIL_HOST_USER")
            # else:
            #     to_email = instance.user.email
            subject = f"[HAS 알림] {instance.user.nickname} 목표 금액 달성 알림"
            message = (
                f"<div><strong>{instance.user.nickname}</strong>님의 <br>"
                f'"{instance.name}"통장의 잔액이 {threshold}원을 돌파하였습니다. 축하합니다.</div>'
            )

            send_email(subject, message, to_email)
