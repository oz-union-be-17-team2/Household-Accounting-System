from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if access_token is None:
            return None
        validated_token = self.get_validated_token(access_token)
        return self.get_user(validated_token), validated_token


class CookieJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = "app.user.authentication.CookieJWTAuthentication"
    name = "CookieJWTAuthentication"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
        }
