from django.urls import path

from app.account.views import AccountDetailAPIView, AccountListCreateAPIView

app_name = "account"

urlpatterns = [
    path("", AccountListCreateAPIView.as_view(), name="list_create"),
    path("<int:account_pk>/", AccountDetailAPIView.as_view(), name="detail"),
]
