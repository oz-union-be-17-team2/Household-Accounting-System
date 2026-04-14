from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from app.account.exceptions import AccountNotFoundError
from app.account.models import Account

User = get_user_model()


def get_account_list(*, user: User, account_type: str | None = None, bank_code: str | None = None) -> QuerySet[Account]:
    account_list = Account.objects.filter(user=user).select_related("user")
    # filter
    if account_type:
        account_list = account_list.filter(account_type=account_type)
    if bank_code:
        account_list = account_list.filter(bank_code=bank_code)
    return account_list


def get_account_detail(*, user: User, account_pk: int) -> Account:
    try:
        return Account.objects.select_related("user").get(user=user, pk=account_pk)
    except Account.DoesNotExist:
        raise AccountNotFoundError("계좌를 찾을 수 없습니다.") from None
