from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        transaction = Transaction.objects.filter(user=self.request.user)

        transaction_type = self.request.query_params.get('type')
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')

        if transaction_type:
            transaction = transaction.filter(transaction_type=transaction_type)
        if amount_min:
            transaction = transaction.filter(amount__gte=amount_min)
        if amount_max:
            transaction = transaction.filter(amount__lte=amount_max)

        return transaction

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)