import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from app.account.models import Account
from app.transaction.models import Transaction
from app.transaction.views import get_transaction_list
from app.user.models import CustomUser

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(email="test@test.com", nickname="testuser", password="testpassword")


@pytest.fixture
def account(user):
    return Account.objects.create(
        user=user,
        name="테스트 통장",
        number="010-0000-0000",
        account_type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
    )


@pytest.fixture
def transaction(user, account):
    return Transaction.objects.create(
        user=user,
        account=account,
        amount=10000,
        description="테스트 거래",
        transaction_type=Transaction.TransactionType.DEPOSIT,
    )


# 거래내역 모델이 정상적으로 생성되는지 확인
@pytest.mark.django_db
def test_transaction_create(user, account):
    result = Transaction.objects.create(
        user=user,
        account=account,
        amount=10000,
        description="테스트 거래",
        transaction_type=Transaction.TransactionType.DEPOSIT,
    )

    assert result.user == user
    assert result.account == account
    assert result.amount == 10000
    assert result.transaction_type == Transaction.TransactionType.DEPOSIT


# get_transaction_list() 셀렉터가 본인 거래내역 목록을 정상적으로 반환하는지 확인
@pytest.mark.django_db
def test_selectors_get_transaction_list(user, account, transaction):
    result = get_transaction_list(user=user)

    assert result.count() == 1
    assert result[0] == transaction


# 거래 유형(입금/출금)으로 필터링이 정상적으로 작동하는지 확인
@pytest.mark.django_db
def test_selectors_get_transaction_list_filter_type(user, account, transaction):
    result = get_transaction_list(user=user, transaction_type="DEPOSIT")

    assert result.count() == 1
    assert result[0].transaction_type == Transaction.TransactionType.DEPOSIT


# 금액 범위(최소/최대)로 필터링이 정상적으로 작동하는지 확인
@pytest.mark.django_db
def test_selectors_get_transaction_list_filter_amount(user, account, transaction):
    result = get_transaction_list(user=user, amount_min=5000, amount_max=20000)

    assert result.count() == 1
    assert result[0].amount == 10000


# 인증된 유저가 거래내역 목록 조회 API 호출 시 200과 결과를 정상적으로 반환하는지 확인
@pytest.mark.django_db
def test_views_get_transaction_list(client, user, account, transaction):
    client.force_authenticate(user=user)
    response = client.get("/transaction/transaction/")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1


# 인증된 유저가 거래내역 생성 API 호출 시 201과 DB에 정상적으로 생성되는지 확인
@pytest.mark.django_db
def test_views_post_transaction_create(client, user, account):
    client.force_authenticate(user=user)
    data = {
        "account": account.pk,
        "amount": 20000,
        "description": "생성 테스트",
        "transaction_type": "DEPOSIT",
    }
    response = client.post("/transaction/transaction/", data=data, format="json")

    assert response.status_code == 201
    assert Transaction.objects.count() == 1


# 인증된 유저가 특정 거래내역 단건 조회 API 호출 시 200과 올바른 데이터를 반환하는지 확인
@pytest.mark.django_db
def test_views_get_transaction_detail(client, user, account, transaction):
    client.force_authenticate(user=user)
    response = client.get(f"/transaction/transaction/{transaction.pk}/")

    assert response.status_code == 200
    assert response.data["amount"] == "10000.00"


# 인증된 유저가 거래내역 수정 API 호출 시 200과 DB에 정상적으로 수정되는지 확인
@pytest.mark.django_db
def test_views_put_transaction_update(client, user, account, transaction):
    client.force_authenticate(user=user)
    data = {
        "account": account.pk,
        "amount": 50000,
        "description": "수정된 거래",
        "transaction_type": "WITHDRAWAL",
    }
    response = client.put(f"/transaction/transaction/{transaction.pk}/", data=data, format="json")

    assert response.status_code == 200
    transaction.refresh_from_db()
    assert transaction.description == "수정된 거래"
    assert transaction.amount == 50000


# 인증된 유저가 거래내역 삭제 API 호출 시 204와 DB에서 정상적으로 삭제되는지 확인
@pytest.mark.django_db
def test_views_delete_transaction(client, user, account, transaction):
    client.force_authenticate(user=user)
    response = client.delete(f"/transaction/transaction/{transaction.pk}/")

    assert response.status_code == 204
    assert Transaction.objects.count() == 0


# 비로그인 유저가 거래내역 API 접근 시 401을 반환하는지 확인
@pytest.mark.django_db
def test_views_unauthenticated_access(client):
    response = client.get("/transaction/transaction/")

    assert response.status_code == 401


# 다른 유저가 타인의 거래내역에 접근 시 404를 반환하는지 확인
@pytest.mark.django_db
def test_views_other_user_cannot_access(client, user, account, transaction):
    other_user = CustomUser.objects.create_user(
        email="other@test.com",
        nickname="otheruser",
        password="otherpass123",
    )
    client.force_authenticate(user=other_user)
    response = client.get(f"/transaction/transaction/{transaction.pk}/")

    assert response.status_code == 404
