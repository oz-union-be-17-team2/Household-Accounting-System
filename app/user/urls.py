from django.urls import path

from app.user import views

app_name = "user"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
]
