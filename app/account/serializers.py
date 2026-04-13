import re

from rest_framework import serializers

from app.account.models import Account


class AccountSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField(read_only=True)

    def get_user_nickname(self, obj):
        return obj.user.nickname


class AccountListSerializer(AccountSerializer):
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
        ]
        read_only_fields = [
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code",
            "is_active",
            "balance",
        ]


class AccountCreateSerializer(AccountSerializer):
    def validate_number(self, value):
        if not re.match(r"^[\d-]+$", value):
            raise serializers.ValidationError("계좌번호는 숫자와 -만 입력 가능합니다.")
        return value

    class Meta:
        model = Account
        fields = [
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code",
            "balance",
        ]
        read_only_fields = [
            "user_nickname",
        ]


class AccountDetailSerializer(AccountSerializer):
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
