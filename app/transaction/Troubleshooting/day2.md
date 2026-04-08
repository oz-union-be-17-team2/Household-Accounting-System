# Troubleshooting - 2026.04.08



## 코드 수정 % 해석
- model에서 core에 basemodel(`TimeStempModel`)을 상속받아서 사용

```
class Transaction(TimeStampModel):
    # core에서 basemodel을 상속받아
    # updated_at과 created_at을 사용
    class TransactionType(models.TextChoices):
        # TextChoices에서 첫 번째 인자는 DB에 저장되는 값
        # 두 번째 인자는 라벨(표시용 텍스트)
        # 만약 그냥 문자열로 저장하면 오타가 들어와도 DB에 그대로 저장
        # TextChoices를 쓰면 지정 된 값에서 선택 가능
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
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING)
```