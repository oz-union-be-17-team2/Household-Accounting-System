import re

from rest_framework import serializers

from app.account.models import Account


class AccountSerializer(serializers.ModelSerializer):
    user_nickname = serializers.SerializerMethodField(read_only=True)
    bank_code_display = serializers.SerializerMethodField()

    def get_user_nickname(self, obj):
        return obj.user.nickname

    def get_bank_code_display(self, obj):
        return obj.get_bank_code_display()


class AccountListSerializer(AccountSerializer):
    class Meta:
        model = Account
        fields = [
            "id",  # test 및 시연을 위해 생성
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code_display",
            "is_active",
            "balance",
        ]
        read_only_fields = [
            "id",  # test 및 시연을 위해 생성
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code_display",
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
            "id",  # test 및 시연을 위해 생성
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code",
            "bank_code_display",
            "balance",
        ]
        read_only_fields = [
            "id",  # test 및 시연을 위해 생성
            "user_nickname",
        ]


class AccountDetailSerializer(AccountSerializer):
    class Meta:
        model = Account
        fields = [
            "id",  # test 및 시연을 위해 생성
            "user_nickname",
            "name",
            "number",
            "account_type",
            "bank_code_display",
            "is_active",
            "balance",
            "updated_at",
            "created_at",
        ]
        read_only_fields = [
            "id",  # test 및 시연을 위해 생성
            "user_nickname",
            "number",
            "account_type",
            "bank_code_display",
            "balance",
            "updated_at",
            "created_at",
        ]
