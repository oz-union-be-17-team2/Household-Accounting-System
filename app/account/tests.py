# Create your tests here.
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from app.account.exceptions import AccountNotFoundError
from app.account.models import Account
from app.account.selectors import get_account_detail, get_account_list

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


# selectors test
@pytest.mark.django_db
def test_selectors_get_account_list(user, account):
    result = get_account_list(user=user)

    assert result.count() == 1
    assert result[0] == account
    assert result[0].balance == 100_000


@pytest.mark.django_db
def test_selectors_get_account_detail_success(user, account):
    result = get_account_detail(user=user, account_pk=account.pk)

    assert result == account
    assert result.number == "1234-1234-1234"


@pytest.mark.django_db
def test_selectors_get_account_detail_fail(user):
    with pytest.raises(AccountNotFoundError) as error:
        get_account_detail(user=user, account_pk=None)

    assert str(error.value) == "계좌를 찾을 수 없습니다."


# views test
@pytest.mark.django_db
def test_views_get_account_list_create(client, user, account):
    client.force_authenticate(user=user)
    response = client.get("/account/")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_views_get_account_list_create_fail(client, user):
    client.force_authenticate(user=user)
    response = client.get("/account/")

    assert response.status_code == 404
    assert response.data["message"] == "계좌가 없습니다."


@pytest.mark.django_db
def test_views_post_account_list_create(client, user, account):
    client.force_authenticate(user=user)
    url = reverse("account:list_create")
    data = {
        "name": "test account",
        "number": "1234-1234-1111-1111",
        "type": Account.AccountType.CHECKING,
        "bank_code": Account.BankCode.KB,
        "balance": 100_000,
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == 201
    assert response.data["user_nickname"] == user.nickname


@pytest.mark.django_db
def test_views_post_account_list_create_fail(client, user, account):
    client.force_authenticate(user=user)
    url = reverse("account:list_create")
    data = {
        "name": "test account",
        "number": "1234-1234-1111-1111",
        "type": Account.AccountType.CHECKING,
        "bank_code": "test bank",
        "balance": -100,
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == 400
