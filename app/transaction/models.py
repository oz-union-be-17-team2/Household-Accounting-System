from django.conf import settings
from django.db import models

from app.account.models import Account
from core.models import TimeStampModel


class Transaction(TimeStampModel):
    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "입금"
        WITHDRAWAL = "WITHDRAWAL", "출금"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    # 역할 : 해당 유저임을 확인하고 해당 유저만 거래내역 수정 삭제를 할 수 있는 역할
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    # 역할 : 해당 유저의 계좌에서 계좌를 받기 위해서
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    # 역할 : 거래내역의 해당거래 금액
    description = models.CharField(max_length=255)
    # 역할 : 거래내역에서 사용자의 비고 사항을 작성하기 위해
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)

    # 역할 : 거래유형을 입금, 출금으로 강제해둬서 사용자가 이 두가지중 하나를 선택할 수 있게 설계
    def __str__(self):
        return f"{self.user} | {self.transaction_type} | {self.amount}"
