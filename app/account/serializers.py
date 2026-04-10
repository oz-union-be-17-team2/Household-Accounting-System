from rest_framework import serializers

from app.account.models import Account


class AccountListCreateSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField(read_only=True)

    def get_user_nickname(self, obj):
        return obj.user.nickname

    class Meta:
        model = Account
        fields = [
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code",
            "is_active",
            "balance",
            "updated_at",
            "created_at",
        ]
        read_only_fields = [
            "user_nickname",
            "updated_at",
            "created_at",
        ]


class AccountDetailSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField(read_only=True)

    def get_user_nickname(self, obj):
        return obj.user.nickname

    class Meta:
        model = Account
        fields = [
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code",
            "is_active",
            "balance",
            "updated_at",
            "created_at",
        ]
        read_only_fields = [
            "user_nickname",
            "number",
            "account_type",
            "bank_code",
            "balance",
            "updated_at",
            "created_at",
        ]
