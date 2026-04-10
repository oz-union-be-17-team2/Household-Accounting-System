from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from app.account.exceptions import AccountNotFoundError
from app.account.models import Account

User = get_user_model()


def get_account_list(*, user: User) -> QuerySet[Account]:
    if settings.DEBUG:
        return Account.objects.all().select_related("user")
    return Account.objects.filter(user=user).select_related("user")


def get_account_detail(*, user: User, account_pk: int) -> Account:
    try:
        if settings.DEBUG:
            return Account.objects.get(pk=account_pk)
        return Account.objects.select_related("user").get(user=user, pk=account_pk)
    except Account.DoesNotExist:
        raise AccountNotFoundError("계좌를 찾을 수 없습니다.") from None
