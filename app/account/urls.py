from django.urls import path

from app.account.views import AccountListCreateAPIView

app_name = "account"

urlpatterns = [
    path("", AccountListCreateAPIView.as_view(), name="account_list_create"),
]
