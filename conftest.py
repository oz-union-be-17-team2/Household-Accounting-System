import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from app.account.models import Account

User = get_user_model()


# 초기세팅
@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@test.com",
        nickname="test nickname",
    )


@pytest.fixture
def account(user):
    return Account.objects.create(
        user=user,
        number="1234-1234-1234",
        account_type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
        balance=100_000,
    )
