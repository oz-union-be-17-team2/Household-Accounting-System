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
