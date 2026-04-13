import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse

from app.account.exceptions import AccountNotFoundError
from app.account.models import Account, BalanceAlert
from app.account.selectors import get_account_detail, get_account_list

User = get_user_model()


# model test
@pytest.mark.django_db
def test_account_create_success(user):
    result = Account.objects.create(
        user=user,
        number="1111-1111-1111",
        account_type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
        balance=100_000,
    )
    assert result.user == user
    assert result.number == "1111-1111-1111"
    assert result.account_type == Account.AccountType.CHECKING
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
        get_account_detail(user=user, account_pk=100)

    assert str(error.value) == "계좌를 찾을 수 없습니다."


@pytest.mark.django_db
class TestSelectorFilter:
    def test_selectors_filter_account_type(self, user, account):
        result = get_account_list(user=user, account_type=account.account_type)

        assert result.count() == 1
        assert result.first().account_type == Account.AccountType.CHECKING

    def test_selectors_filter_bank_code(self, user, account):
        result = get_account_list(user=user, bank_code=account.bank_code)

        assert result.count() == 1
        assert result.first().bank_code == Account.BankCode.KB


@pytest.mark.django_db
class TestSignals:
    # 생성 검증
    def test_balance_alert_created(self, user, account):
        account.balance = 10_000_000
        account.save()

        assert BalanceAlert.objects.filter(account=account, threshold=10_000_000).exists()

    # 1개만 생성되는지 검증
    def test_balance_alert_not_duplicated(self, user, account):
        account.balance = 10_000_000
        account.save()
        account.save()
        account.save()

        assert BalanceAlert.objects.filter(account=account, threshold=10_000_000).count() == 1

    def test_no_alert_below_threshold(self, user, account):
        account.balance = 5_000_000
        account.save()

        assert BalanceAlert.objects.filter(account=account, threshold=10_000_000).count() == 0


# views test
@pytest.mark.django_db
def test_views_get_account_list_create(client, user, account):
    client.force_authenticate(user=user)
    response = client.get("/account/")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_views_post_account_list_create(client, user, account):
    client.force_authenticate(user=user)
    url = reverse("account:list_create")
    data = {
        "name": "test account",
        "number": "1234-1234-1111-1111",
        "account_type": Account.AccountType.CHECKING,
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
        "account_type": Account.AccountType.CHECKING,
        "bank_code": "test bank",
        "balance": -100,
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == 400


# ================================================================
# Claude가 작성한 테스트
# ================================================================


# Model
@pytest.mark.django_db
def test_account_create_without_number(user):
    """필수 필드(number) 없이 생성 시도"""
    account = Account(
        user=user,
        account_type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
    )
    with pytest.raises(ValidationError):
        account.full_clean()


# Selectors
@pytest.mark.django_db
def test_selectors_get_account_list_empty(user):
    """계좌가 없을 때 빈 QuerySet 반환"""
    result = get_account_list(user=user)

    assert result.count() == 0


# Services


# Views - GET /account/ 목록 조회
@pytest.mark.django_db
def test_views_get_account_list_empty(client, user):
    """계좌가 없을 때 빈 목록 반환"""
    client.force_authenticate(user=user)
    url = reverse("account:list_create")
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_views_get_account_list_unauthenticated(client):
    """미로그인 상태에서 목록 조회 시도"""
    url = reverse("account:list_create")
    response = client.get(url)

    assert response.status_code == 401


# Views - POST /account/ 계좌 생성
@pytest.mark.django_db
def test_views_post_account_fail_duplicate_number(client, user, account):
    """중복된 계좌번호로 생성 시도"""
    client.force_authenticate(user=user)
    url = reverse("account:list_create")
    data = {
        "name": "중복 통장",
        "number": account.number,
        "account_type": Account.AccountType.CHECKING,
        "bank_code": Account.BankCode.KB,
        "balance": 10_000,
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_views_post_account_unauthenticated(client):
    """미로그인 상태에서 계좌 생성 시도"""
    url = reverse("account:list_create")
    data = {
        "name": "test account",
        "number": "1234-1234-1111-1111",
        "account_type": Account.AccountType.CHECKING,
        "bank_code": Account.BankCode.KB,
        "balance": 100_000,
    }
    response = client.post(url, data=data, format="json")

    assert response.status_code == 401


# Views - GET /account/<account_pk>/ 단건 조회
@pytest.mark.django_db
def test_views_get_account_detail_success(client, user, account):
    """계좌 단건 조회 성공"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["number"] == account.number
    assert response.data["user_nickname"] == user.nickname


@pytest.mark.django_db
def test_views_get_account_detail_not_found(client, user):
    """존재하지 않는 계좌 단건 조회"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": 99999})
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_views_get_account_detail_unauthenticated(client, account):
    """미로그인 상태에서 단건 조회 시도"""
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_views_get_account_detail_other_user(client, account):
    """다른 유저의 계좌 단건 조회 시도"""
    other_user = User.objects.create_user(email="other@test.com", nickname="other", gender="", job="")
    client.force_authenticate(user=other_user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.get(url)

    assert response.status_code == 404


# Views - PATCH /account/<account_pk>/ 수정
@pytest.mark.django_db
def test_views_patch_account_success(client, user, account):
    """계좌 이름 수정 성공"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.patch(url, data={"name": "수정된 통장"}, format="json")

    assert response.status_code == 200
    assert response.data["name"] == "수정된 통장"


@pytest.mark.django_db
def test_views_patch_account_readonly_fields(client, user, account):
    """read_only 필드 수정 시도 시 무시됨"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.patch(url, data={"balance": 999_999_999}, format="json")

    assert response.status_code == 200
    assert response.data["balance"] == str(account.balance)


@pytest.mark.django_db
def test_views_patch_account_not_found(client, user):
    """존재하지 않는 계좌 수정 시도"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": 99999})
    response = client.patch(url, data={"name": "수정된 통장"}, format="json")

    assert response.status_code == 404


@pytest.mark.django_db
def test_views_patch_account_unauthenticated(client, account):
    """미로그인 상태에서 수정 시도"""
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.patch(url, data={"name": "수정된 통장"}, format="json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_views_patch_account_other_user(client, account):
    """다른 유저의 계좌 수정 시도"""
    other_user = User.objects.create_user(email="other@test.com", nickname="other", gender="", job="")
    client.force_authenticate(user=other_user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.patch(url, data={"name": "수정된 통장"}, format="json")

    assert response.status_code == 404


# Views - DELETE /account/<account_pk>/ 삭제
@pytest.mark.django_db
def test_views_delete_account_success(client, user, account):
    """계좌 삭제 성공 및 DB에서 실제 삭제 확인"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.delete(url)

    assert response.status_code == 204
    assert Account.objects.filter(pk=account.pk).exists() is False


@pytest.mark.django_db
def test_views_delete_account_not_found(client, user):
    """존재하지 않는 계좌 삭제 시도"""
    client.force_authenticate(user=user)
    url = reverse("account:detail", kwargs={"account_pk": 99999})
    response = client.delete(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_views_delete_account_unauthenticated(client, account):
    """미로그인 상태에서 삭제 시도"""
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.delete(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_views_delete_account_other_user(client, account):
    """다른 유저의 계좌 삭제 시도"""
    other_user = User.objects.create_user(email="other@test.com", nickname="other", gender="", job="")
    client.force_authenticate(user=other_user)
    url = reverse("account:detail", kwargs={"account_pk": account.pk})
    response = client.delete(url)

    assert response.status_code == 404
