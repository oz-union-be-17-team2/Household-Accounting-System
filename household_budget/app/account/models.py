from django.conf import settings
from django.db import models

from household_budget.core.models import TimeStampModel

User = settings.AUTH_USER_MODEL
class Account(TimeStampModel):

    class BankCode(models.TextChoices):
        KB = "004", "국민은행"
        SHINHAN = "088", "신한은행"
        WOORI = "020", "우리은행"
        HANA = "081", "하나은행"
        NH = "011", "농협은행"
        IBK = "003", "기업은행"
        SC = "023", "SC제일은행"
        CITI = "027", "씨티은행"
        BUSAN = "032", "부산은행"
        DAEGU = "031", "대구은행"
        KAKAO = "090", "카카오뱅크"
        TOSS = "092", "토스뱅크"
        K = "089", "케이뱅크"

    class AccountType(models.TextChoices):
        CHECKING    = 'CHECKING',    '입출금'
        SAVINGS     = 'SAVINGS',     '적금'
        DEPOSIT     = 'DEPOSIT',     '예금'
        OVERDRAFT   = 'OVERDRAFT',   '마이너스'
        LOAN        = 'LOAN',        '대출'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bank_code = models.CharField(max_length=3, choices=BankCode.choices)
    account_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    daily_transfer_limit = models.DecimalField(max_digits=10, decimal_places=2)
    per_transaction_limit = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_transfer_limit = models.DecimalField(max_digits=10, decimal_places=2)