# Create your tests here.
import pytest
from django.contrib.auth import get_user_model

from app.account.models import Account

User = get_user_model()


# 초기세팅
@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@test.com", nickname="test nickname", gender=User.Gender.MALE, age=20, job=User.Job.EMPLOYEE
    )


@pytest.fixture
def account(user):
    return Account.objects.create(
        user=user,
        number="1234-1234-1234",
        type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
        balance=100_000,
    )


# model test
@pytest.mark.django_db
def test_account_create_success(user):
    result = Account.objects.create(
        user=user,
        number="1111-1111-1111",
        type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
        balance=100_000,
    )
    assert result.user == user
    assert result.number == "1111-1111-1111"
    assert result.type == Account.AccountType.CHECKING
    assert result.bank_code == Account.BankCode.KB
    assert result.balance == 100_000
