# Troubleshooting - 2026.04.07



### Generic View
- `ListCreateAPIView` — 목록 조회(GET) + 생성(POST)
- `RetrieveUpdateDestroyAPIView` — 상세 조회 + 수정 + 삭제

### 오버라이드
- `get_queryset()` — 원본은 전체 객체 반환, 본인 데이터만 필터링하기 위해 재정의
- `perform_create()` — 원본은 `serializer.save()` 한 줄, user 자동 주입을 위해 재정의

### 쿼리 파라미터
- URL 뒤에 `?key=value` 형태로 검색 조건을 전달하는 방식
- `self.request.query_params.get('key')`로 값을 꺼낸다

### Django ORM Lookup
- `amount__gte` — 이상 (>=)
- `amount__lte` — 이하 (<=)

---

## 헷갈렸던 부분

| 문제 | 원인 | 해결 |
|---|---|---|
| `query_params('type')` | 딕셔너리를 괄호로 호출 | `.get('type')`으로 수정 |
| `put()` 직접 오버라이드 | APIView 방식으로 접근 | Generic View는 `get_queryset()`만 오버라이드 |
| CASCADE 방향 혼동 | 부모가 삭제될 때 자식도 삭제되는 방향 | ForeignKey는 "내가 바라보는 대상이 삭제되면 나를 어떻게 할지" |
| PROTECT 사용 이유 | | 금융 데이터는 함부로 삭제되면 안 되므로 강제로 막는 용도 |

---

## 작성 부분

### models
```
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
```
## TextChoices

### 개념
특정 필드에 들어올 수 있는 값을 미리 제한하는 Django 기능이다.
예를 들어 `transaction_type`에 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER' 외의 값이 들어오지 못하도록 막는다.

### 구조
```python
class TransactionType(models.TextChoices):
    DEPOSIT = 'DEPOSIT', '입금'
    #          ^DB 저장값   ^사람이 읽는 이름
```

---

### views
```
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    # 원본 get_queryset()은 queryset 속성에 지정된 전체 객체를 반환한다.
    # 오버라이드 이유: 본인 거래내역만 반환하고, 쿼리 파라미터로 필터링 조건을 추가하기 위해
    def get_queryset(self):
        # 로그인한 유저의 거래내역만 조회
        transaction = Transaction.objects.filter(user=self.request.user)

        # URL 쿼리 파라미터에서 필터링 조건을 꺼낸다
        # 예: /api/transactions/?type=DEPOSIT&amount_min=1000&amount_max=50000
        transaction_type = self.request.query_params.get('type')
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')

        # 값이 있을 때만 조건을 추가한다 (없으면 전체 반환)
        if transaction_type:
            transaction = transaction.filter(transaction_type=transaction_type)
        if amount_min:
            # amount__gte: amount 필드가 amount_min 이상인 것
            transaction = transaction.filter(amount__gte=amount_min)
        if amount_max:
            # amount__lte: amount 필드가 amount_max 이하인 것
            transaction = transaction.filter(amount__lte=amount_max)

        return transaction

    # 원본 perform_create()는 serializer.save() 한 줄만 호출한다.
    # 오버라이드 이유: user 필드가 read_only라 클라이언트가 전달하지 않으므로
    # 저장 시점에 로그인한 유저를 자동으로 연결하기 위해
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    # 원본 get_queryset()은 전체 객체를 반환한다.
    # 오버라이드 이유: 타인의 pk로 접근했을 때 데이터가 반환되는 것을 막기 위해
    # 본인 거래내역만 조회 대상으로 제한한다
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

```