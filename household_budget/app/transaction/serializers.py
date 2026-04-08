from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['user', 'to_account', 'from_account', 'amount', 'balance_after',
                  'description', 'transaction_type', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'balance_after', 'status', 'created_at', 'updated_at']

