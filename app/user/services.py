from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


def login(email, password):
    user = authenticate(email=email, password=password)
    if user is None:
        return None
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }


def logout(refresh_token):
    if refresh_token is None:
        return False
    token = RefreshToken(refresh_token)
    token.blacklist()
    return True


def token_refresh(refresh_token):
    if refresh_token is None:
        return None
    token = RefreshToken(refresh_token)
    return {
        "access_token": str(token.access_token),
    }
