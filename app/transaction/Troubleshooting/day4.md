# Troubleshooting - 2026.04.10

## Analysis 앱 구현

---

## analyzers.py - 서비스 파일 역할

### 왜 analyzers.py를 따로 만들었나?

```
views.py     → API 요청/응답 처리만
tasks.py     → "언제 실행할지"만
analyzers.py → "어떻게 분석할지"만 (역할 분리)
```

- `services.py`와 동일하게 비즈니스 로직을 담당하는 파일
- 차이점은 **누가 호출하냐**에 있음

```
services.py  → 사용자 요청(HTTP)이 트리거
analyzers.py → Celery 스케줄러가 트리거
```

---

## tasks.py - 2단계 필터링 구조

### 왜 tasks.py와 analyzers.py에서 각각 필터링하나?

```
tasks.py
└── 전체 유저 조회 (is_active=True, is_delete=False)
    → "누구한테 분석 돌릴지 결정"

analyzers.py
└── Transaction.filter(user=self.user)
    → "그 사람 것만 분석"
```

- `tasks.py` : 분석 대상 유저 선별 (탈퇴, 비활성 유저 제외)
- `analyzers.py` : 해당 유저의 거래내역만 조회 및 분석

---

## @shared_task vs @app.task

### 차이점

| | @app.task | @shared_task |
|---|---|---|
| tasks.py에서 celery.py import | 필요 | 불필요 |
| 경로 변경 시 수정 범위 | 모든 tasks.py 수정 필요 | 수정 불필요 |
| 순환 참조 위험 | 있음 | 없음 |
| Django 권장 | ❌ | ✅ |

### 왜 @shared_task를 선택했나?

```python
# @app.task - celery.py 경로를 직접 알아야 함
from config.celery import app
@app.task
def analyze_weekly_task():
    pass

# @shared_task - celery.py 몰라도 됨
from celery import shared_task
@shared_task
def analyze_weekly_task():
    pass
```

- Django는 앱이 여러 개라 각 `tasks.py`가 `celery.py`를 직접 import하면 순환 참조 위험이 있음
- `celery.py` 경로가 바뀌어도 `tasks.py`를 수정할 필요가 없어 유지보수에 유리

---

## timezone 설정

### 문제
`created_at__range`에 timezone 정보 없는 `date` 타입을 넣으면 경고 발생
```
RuntimeWarning: DateTimeField received a naive datetime while time zone support is active.
```

### 원인
- `period_start`, `period_end`는 `date` 타입 (timezone 정보 없음)
- `created_at`은 `DateTimeField` (timezone 정보 있음)
- 타입이 달라서 Django가 "이게 어느 나라 시간이야?" 모름

### 해결
```python
from django.utils import timezone
from datetime import datetime, time

# date → timezone 정보가 있는 datetime으로 변환
timezone.make_aware(datetime.combine(self.period_start, time.min))
# → 2026-04-01 00:00:00+09:00 (Asia/Seoul 기준)
```

### settings.py 타임존 설정
```python
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
```
- `make_aware()`는 `settings.py`의 `TIME_ZONE` 기준으로 변환

---

## Matplotlib 한글 폰트 설정

### 문제
Matplotlib 기본 폰트가 한글을 지원하지 않아 차트에 한글이 깨짐
```
UserWarning: Glyph missing from font(s) DejaVu Sans.
```

### 해결
```python
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"  # macOS 한글 폰트
plt.rcParams["axes.unicode_minus"] = False   # 마이너스 기호 깨짐 방지
```

- `AppleGothic` : macOS 기본 한글 폰트
- `axes.unicode_minus = False` : 한글 폰트로 바꾸면 `-` 기호가 깨지는 문제 방지
