from rest_framework import serializers

from app.account.models import Account


class AccountListCreateSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)

    def get_user_name(self, obj):
        return obj.user.name

    class Meta:
        model = Account
        fields = [
            "user_name",
            "name",
            "number",
            "type",
            "bank_code",
            "is_active",
            "balance",
            "updated_at",
            "created_at",
        ]
        read_only_fields = [
            "user_name",
            "updated_at",
            "created_at",
        ]


class AccountDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)

    def get_user_name(self, obj):
        return obj.user.name

    class Meta:
        model = Account
        fields = [
            "user_name",
            "name",
            "number",
            "type",
            "bank_code",
            "is_active",
            "balance",
            "updated_at",
            "created_at",
        ]
        read_only_fields = [
            "user_name",
            "number",
            "type",
            "bank_code",
            "updated_at",
            "created_at",
        ]