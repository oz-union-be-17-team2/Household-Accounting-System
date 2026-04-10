from django.conf import settings
from django.contrib.auth import get_user_model

from app.account.selectors import get_account_detail
from app.account.serializers import AccountDetailSerializer, AccountListCreateSerializer

User = get_user_model()


def create_account(*, user: User, data):
    serializer = AccountListCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    if settings.DEBUG:
        serializer.save(user=User.objects.first())
    else:
        serializer.save(user=user)
    return serializer.data


def retrieve_account(*, user: User, account_pk: int):
    account = get_account_detail(user=user, account_pk=account_pk)
    serializer = AccountDetailSerializer(account, many=False)
    return serializer.data


def update_account(*, user: User, data, account_pk: int):
    account = get_account_detail(user=user, account_pk=account_pk)
    serializer = AccountDetailSerializer(account, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data


def delete_account(*, user: User, account_pk: int) -> None:
    account = get_account_detail(user=user, account_pk=account_pk)
    account.delete()
    return None
