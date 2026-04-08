from django.db import models
from django.conf import settings
from account.models import Account

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', '입금'
        WITHDRAWAL = 'WITHDRAWAL', '출금'
        TRANSFER = 'TRANSFER', '이체'

    class Status(models.TextChoices):
        PENDING = 'PENDING', '처리중'
        COMPLETED = 'COMPLETED', '완료'
        FAILED = 'FAILED', '실패'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    to_account = models.ForeignKey(
        Account, on_delete=models.PROTECT,
        related_name='to_transaction'
    )
    from_account = models.ForeignKey(
        Account, on_delete=models.PROTECT,
        related_name='from_transaction'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING)
