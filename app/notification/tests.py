from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIClient

from app.account.models import Account
from app.notification.exceptions import NotificationNotFoundError
from app.notification.models import Notification
from app.notification.selectors import get_notification_detail, get_notification_list
from app.notification.services import delete_notification, hard_delete_old_notification, mark_notification_as_read
from app.notification.tasks import hard_delete_old_notification_task
from app.notification.views import NotificationDetailAPIView, NotificationListAPIView
from app.user.models import CustomUser

# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="test@test.com",
        nickname="testuser",
        password="test1234!",
        gender="",
        job="",
    )


@pytest.fixture
def other_user():
    return CustomUser.objects.create_user(
        email="other@test.com",
        nickname="otheruser",
        password="test1234!",
        gender="",
        job="",
    )


@pytest.fixture
def notification(user):
    return Notification.objects.create(user=user, message="테스트 알림")


@pytest.fixture
def other_notification(other_user):
    return Notification.objects.create(user=other_user, message="다른 유저 알림")


@pytest.fixture
def logged_in_client(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def account(user):
    with patch("app.account.signals.send_email"):
        return Account.objects.create(
            user=user,
            name="테스트통장",
            number="1234567890",
            account_type=Account.AccountType.CHECKING,
            bank_code=Account.BankCode.KB,
            balance=0,
        )


# ============================================================
# Services
# ============================================================


@pytest.mark.django_db
class TestMarkNotificationAsRead:
    def test_unread_notification_becomes_read(self, notification):
        assert notification.is_read is False
        mark_notification_as_read(notification)
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_already_read_notification_does_not_call_save(self, notification):
        notification.is_read = True
        notification.save()
        with patch.object(notification, "save") as mock_save:
            mark_notification_as_read(notification)
            mock_save.assert_not_called()


@pytest.mark.django_db
class TestDeleteNotification:
    def test_soft_delete_hides_from_objects(self, notification):
        delete_notification(notification)
        assert Notification.objects.filter(pk=notification.pk).exists() is False

    def test_soft_deleted_still_visible_in_all_objects(self, notification):
        delete_notification(notification)
        assert Notification.all_objects.filter(pk=notification.pk).exists() is True


@pytest.mark.django_db
class TestHardDeleteOldNotification:
    def test_old_soft_deleted_is_permanently_deleted(self, notification):
        notification.deleted_at = timezone.now() - timedelta(days=31)
        notification.save(update_fields=["deleted_at"])
        hard_delete_old_notification(days=30)
        assert Notification.all_objects.filter(pk=notification.pk).exists() is False

    def test_recent_soft_deleted_is_kept(self, notification):
        notification.deleted_at = timezone.now() - timedelta(days=10)
        notification.save(update_fields=["deleted_at"])
        hard_delete_old_notification(days=30)
        assert Notification.all_objects.filter(pk=notification.pk).exists() is True

    def test_not_deleted_notification_is_not_affected(self, notification):
        hard_delete_old_notification(days=30)
        assert Notification.objects.filter(pk=notification.pk).exists() is True


# ============================================================
# Selectors
# ============================================================


@pytest.mark.django_db
class TestGetNotificationList:
    def test_returns_only_own_notifications(self, user, notification, other_notification, settings):
        settings.DEBUG = False
        result = list(get_notification_list(user=user))
        assert notification in result
        assert other_notification not in result

    def test_excludes_soft_deleted_notifications(self, user, notification, settings):
        settings.DEBUG = False
        notification.delete()
        result = list(get_notification_list(user=user))
        assert notification not in result

    def test_empty_list_when_no_notifications(self, user, settings):
        settings.DEBUG = False
        result = list(get_notification_list(user=user))
        assert result == []

    def test_ordered_by_newest_first(self, user, settings):
        settings.DEBUG = False
        n1 = Notification.objects.create(user=user, message="첫번째")
        n2 = Notification.objects.create(user=user, message="두번째")
        # auto_now_add 동일 타임스탬프 방지
        Notification.objects.filter(pk=n1.pk).update(created_at=timezone.now() - timedelta(seconds=1))
        result = list(get_notification_list(user=user))
        assert result[0] == n2
        assert result[1] == n1


@pytest.mark.django_db
class TestGetNotificationDetail:
    def test_success(self, user, notification, settings):
        settings.DEBUG = False
        result = get_notification_detail(user=user, noti_pk=notification.pk)
        assert result == notification

    def test_nonexistent_pk_raises_error(self, user, settings):
        settings.DEBUG = False
        with pytest.raises(NotificationNotFoundError):
            get_notification_detail(user=user, noti_pk=9999)

    def test_other_users_notification_raises_error(self, user, other_notification, settings):
        settings.DEBUG = False
        with pytest.raises(NotificationNotFoundError):
            get_notification_detail(user=user, noti_pk=other_notification.pk)

    def test_soft_deleted_notification_raises_error(self, user, notification, settings):
        settings.DEBUG = False
        notification.delete()
        with pytest.raises(NotificationNotFoundError):
            get_notification_detail(user=user, noti_pk=notification.pk)


# ============================================================
# Views
# ============================================================


@pytest.mark.django_db
class TestNotificationListView:
    def test_authenticated_returns_200_with_own_notifications(self, logged_in_client, notification):
        response = logged_in_client.get(reverse("notification:list"))
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == notification.pk

    def test_unauthenticated_returns_401(self, client, monkeypatch):
        monkeypatch.setattr(NotificationListAPIView, "permission_classes", [IsAuthenticated])
        response = client.get(reverse("notification:list"))
        assert response.status_code == 401


@pytest.mark.django_db
class TestNotificationDetailView:
    def test_get_returns_200_and_marks_as_read(self, logged_in_client, notification):
        assert notification.is_read is False
        response = logged_in_client.get(reverse("notification:detail", kwargs={"noti_pk": notification.pk}))
        assert response.status_code == 200
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_get_nonexistent_returns_404(self, logged_in_client):
        response = logged_in_client.get(reverse("notification:detail", kwargs={"noti_pk": 9999}))
        assert response.status_code == 404

    def test_get_other_users_notification_returns_404(self, logged_in_client, other_notification, settings):
        settings.DEBUG = False
        response = logged_in_client.get(reverse("notification:detail", kwargs={"noti_pk": other_notification.pk}))
        assert response.status_code == 404

    def test_get_unauthenticated_returns_401(self, client, notification, monkeypatch):
        monkeypatch.setattr(NotificationDetailAPIView, "permission_classes", [IsAuthenticated])
        response = client.get(reverse("notification:detail", kwargs={"noti_pk": notification.pk}))
        assert response.status_code == 401

    def test_delete_returns_204_and_soft_deletes(self, logged_in_client, notification):
        response = logged_in_client.delete(reverse("notification:detail", kwargs={"noti_pk": notification.pk}))
        assert response.status_code == 204
        assert Notification.objects.filter(pk=notification.pk).exists() is False
        assert Notification.all_objects.filter(pk=notification.pk).exists() is True

    def test_delete_nonexistent_returns_404(self, logged_in_client):
        response = logged_in_client.delete(reverse("notification:detail", kwargs={"noti_pk": 9999}))
        assert response.status_code == 404

    def test_delete_other_users_notification_returns_404(self, logged_in_client, other_notification, settings):
        settings.DEBUG = False
        response = logged_in_client.delete(reverse("notification:detail", kwargs={"noti_pk": other_notification.pk}))
        assert response.status_code == 404

    def test_delete_unauthenticated_returns_401(self, client, notification, monkeypatch):
        monkeypatch.setattr(NotificationDetailAPIView, "permission_classes", [IsAuthenticated])
        response = client.delete(reverse("notification:detail", kwargs={"noti_pk": notification.pk}))
        assert response.status_code == 401


# ============================================================
# Tasks
# ============================================================


@pytest.mark.django_db
class TestHardDeleteOldNotificationTask:
    def test_task_calls_service_with_30_days(self):
        with patch("app.notification.tasks.hard_delete_old_notification") as mock_service:
            hard_delete_old_notification_task()
            mock_service.assert_called_once_with(days=30)


# ============================================================
# Signals
# ============================================================


@pytest.mark.django_db
class TestAlertBalanceSignal:
    def test_notification_created_when_balance_exceeds_threshold(self, account):
        with patch("app.account.signals.send_email"):
            account.balance = 10_000_000
            account.save()
        assert Notification.objects.filter(user=account.user).exists() is True

    def test_no_notification_when_balance_below_threshold(self, account):
        with patch("app.account.signals.send_email"):
            account.balance = 9_999_999
            account.save()
        assert Notification.objects.filter(user=account.user).exists() is False

    def test_no_duplicate_notification_for_same_threshold(self, account):
        with patch("app.account.signals.send_email"):
            account.balance = 10_000_000
            account.save()
            account.balance = 10_000_001
            account.save()
        assert Notification.objects.filter(user=account.user).count() == 1

    def test_multiple_thresholds_create_multiple_notifications(self, account):
        with patch("app.account.signals.send_email"):
            account.balance = 1_000_000_000
            account.save()
        assert Notification.objects.filter(user=account.user).count() == 3
