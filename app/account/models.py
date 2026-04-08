from django.conf import settings
from django.db import models

from core.models import TimeStampModel


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
        CHECKING = "CHECKING", "입출금"
        SAVINGS = "SAVINGS", "적금"
        DEPOSIT = "DEPOSIT", "예금"
        OVERDRAFT = "OVERDRAFT", "마이너스"
        LOAN = "LOAN", "대출"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="accounts")
    name = models.CharField(max_length=20, default="통장")
    number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=AccountType.choices)
    bank_code = models.CharField(max_length=3, choices=BankCode.choices)
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=20, decimal_places=0, default=0)

    objects = models.Manager()

    class Meta:
        verbose_name = "계좌"
        verbose_name_plural = f"{verbose_name} 목록"
        ordering = ["name", "-updated_at"]

    def __str__(self):
        return f"{self.user.name} - {self.get_bank_code_display()} {self.number} {self.get_type_display()}"
