import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.user.models import CustomUser


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "test@test.com",
        "nickname": "testuser",
        "password": "test1234!",
        "password2": "test1234!",
    }


@pytest.fixture
def registered_user(client, user_data):
    client.post(reverse("user:register"), user_data, format="json")
    return CustomUser.objects.get(email="test@test.com")


@pytest.fixture
def logged_in_client(client, registered_user):
    response = client.post(
        reverse("user:login"),
        {"email": "test@test.com", "password": "test1234!"},
        format="json",
    )
    client.cookies["access_token"] = response.cookies["access_token"]
    client.cookies["refresh_token"] = response.cookies["refresh_token"]
    return client


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, client, user_data):
        response = client.post(reverse("user:register"), user_data, format="json")
        assert response.status_code == 201
        assert CustomUser.objects.filter(email="test@test.com").exists()

    def test_register_duplicate_email(self, client, user_data):
        client.post(reverse("user:register"), user_data, format="json")
        response = client.post(reverse("user:register"), user_data, format="json")
        assert response.status_code == 400

    def test_register_password_mismatch(self, client, user_data):
        user_data["password2"] = "wrongpassword"
        response = client.post(reverse("user:register"), user_data, format="json")
        assert response.status_code == 400

    def test_register_missing_field(self, client):
        response = client.post(reverse("user:register"), {"email": "test@test.com"}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, client, user_data):
        client.post(reverse("user:register"), user_data, format="json")
        response = client.post(
            reverse("user:login"),
            {"email": "test@test.com", "password": "test1234!"},
            format="json",
        )
        assert response.status_code == 200
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_wrong_password(self, client, user_data):
        client.post(reverse("user:register"), user_data, format="json")
        response = client.post(
            reverse("user:login"),
            {"email": "test@test.com", "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_wrong_email(self, client):
        response = client.post(
            reverse("user:login"),
            {"email": "notexist@test.com", "password": "test1234!"},
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestLogout:
    def test_logout_success(self, logged_in_client):
        response = logged_in_client.post(reverse("user:logout"))
        assert response.status_code == 200

    def test_logout_without_login(self, client):
        response = client.post(reverse("user:logout"))
        assert response.status_code == 401


@pytest.mark.django_db
class TestProfile:
    def test_get_profile_success(self, logged_in_client):
        response = logged_in_client.get(reverse("user:profile"))
        assert response.status_code == 200

    def test_get_profile_without_login(self, client):
        response = client.get(reverse("user:profile"))
        assert response.status_code == 401

    def test_patch_profile_success(self, logged_in_client):
        response = logged_in_client.patch(
            reverse("user:profile"),
            {"nickname": "newnickname"},
            format="json",
        )
        assert response.status_code == 200

    def test_delete_profile_success(self, logged_in_client, registered_user):
        response = logged_in_client.delete(reverse("user:profile"))
        assert response.status_code == 204
        registered_user.refresh_from_db()
        assert registered_user.is_delete is True


@pytest.mark.django_db
class TestTokenRefresh:
    def test_token_refresh_success(self, logged_in_client):
        response = logged_in_client.post(reverse("user:token_refresh"))
        assert response.status_code == 200
        assert "access_token" in response.cookies
