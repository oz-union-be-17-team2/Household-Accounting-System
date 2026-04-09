from django.urls import path

from .views import TransactionDetailView, TransactionListView

urlpatterns = [
    path("transaction/", TransactionListView.as_view(), name="transaction_list"),
    path("transaction/<int:pk>/", TransactionDetailView.as_view(), name="transaction_detail"),
    # RetrieveUpdateDestroyAPIView가 GET, PUT, PATCH, DELETE를 전부 처리(generic view에서 알아서 분기)
]
