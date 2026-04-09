from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "account", "transaction_type", "amount", "description", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]
