# Troubleshooting - 2026.04.09



## get_querset() 오버라이드

### 원본 동작
```
def get_queryset(self):
    return self.queryset    # queryset 속성에 지정된 전체 객체 반환
```
### 오버라이드 이유
- 원본은 모든 유저의 데이터를 반환하기 때문에
- 로그인한 본인 데이터만 필터링하기 위해 재 정의
```
def get_queryset(self):
    return Transaction.objects.filter(user=self.request.user)
```

---
## perform_create() 오버라이드

### 원본 동작
```
def perform_create(self, serializer):
    serializer.save()   # 그냥 저장만 함
```
### 오버라이드 이유
- `user`필드가 `read_only`라 클라이언트가 전달하지 않기 때문에
- 저장 시점에 로그인한 유저를 자동으로 주입하기 위해 재 정의
```
def perform_create(self, serializer):
    serializer.save(user=self.request.user)
```

---
## select_related()를 사용한 N+1 문제 해결

### N+1 문제란?
- 거래내역 100개 조회 시 account에 접근할 때마다 DB 쿼리가 100번 추가 발생 (총 101번)
- 데이터가 많아질수록 DB 쿼리가 늘어나 성능 저하 발생

### select_related() 사용 이유
- Transaction(N) -> Account(1) 관계에서 select_related()로 JOIN해서 가져와 N+1 문제 해결
- select_related() 없이 필터링만 하면 account 접근 시마다 DB에서 조회 (N+1 문제 발생)
- select_related()로 account를 미리 JOIN해서 메모리에 올려두면 account 접근 시 DB 쿼리 없이 메모리에서 찾음 (총 1번)

```python
# select_related() 사용 전 (N+1 문제 발생)
Transaction.objects.filter(user=self.request.user)

# select_related() 사용 후 (N+1 문제 해결)
Transaction.objects.filter(user=self.request.user).select_related('account')
```
