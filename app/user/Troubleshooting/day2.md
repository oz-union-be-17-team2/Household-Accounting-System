## 2026.04.08

### CustomUser 모델 변경

**변경 내용**
- `name`, `phone_number` 필드 제거 (가계부 서비스 특성상 불필요)
- 선택 필드 추가: `gender`, `age`, `job`

**gender, job TextChoices 사용 이유**
선택지가 정해진 필드는 `CharField` 대신 `TextChoices`로 제한.
```python
class Gender(models.TextChoices):
    MALE = "M", "남"
    FEMALE = "F", "여"
```

**blank=True, null=True 차이**
- `null=True` — DB에 NULL 저장 허용
- `blank=True` — 시리얼라이저에서 빈 값 허용

선택사항 필드라 둘 다 써줘야 에러안남.

---

### RegisterSerializer 작성

**변경 내용**
- `gender`, `age`, `job` 선택 필드 추가
- 선택사항이라 `create`에서 `validated_data.get()` 사용

**get() 사용 이유**
`validated_data["key"]` 는 키 없으면 에러남.
`validated_data.get("key")` 는 키 없으면 `None` 반환.
선택사항 필드는 `get()` 써야 함.

---

### 마이그레이션 에러 해결

**문제**
ModuleNotFoundError: No module named 'household_budget'

**원인**
팀에서 프로젝트 구조 변경. `household_budget/` 안에 있던 파일들이 밖으로 이동했는데 `user` 브랜치는 옛날 구조 기준이라 충돌.

**해결**
기존 클론 삭제 후 새로 클론받아서 `develop` 기준으로 `USER` 브랜치 새로 파서 작업.