# Troubleshooting - 2026.04.13

## Redis 개념 정리

---

## Redis 메모리 기반 저장소

### 일반 DB vs Redis

```
일반 DB (PostgreSQL, MySQL)
→ 디스크(HDD/SSD)에 저장
→ 읽기/쓰기 속도: 밀리초(ms) ~ 초(s)

Redis
→ RAM(메모리)에 저장
→ 읽기/쓰기 속도: 마이크로초(μs) → 100배 이상 빠름
```

### 메모리 기반이라서 생기는 특징

| 특징 | 설명 |
|---|---|
| 빠름 | 디스크 대신 RAM에 저장 |
| 비쌈 | RAM 용량이 디스크보다 비쌈 |
| 손실 위험 | 서버 재시작 시 데이터 손실 가능 |
| 용도 | 캐싱, 메시지 큐, 세션 등 임시 데이터 |

---

## RDB (Redis Database Snapshot)

### 개념
- Redis 기본 저장 방식
- 주기적으로 메모리 데이터를 `dump.rdb` 파일로 디스크에 저장
- 사람이 직접 읽을 수 없는 바이너리 파일
- Redis 재시작 시 자동으로 불러와서 복구

### 저장 조건 (기본값)
```
3600초(1시간) 동안 1번 이상 변경   → 저장
300초(5분) 동안 100번 이상 변경    → 저장
60초(1분) 동안 10000번 이상 변경   → 저장
```
→ 조건 미달 시 저장 안 됨 (변경이 거의 없으면 오래된 스냅샷이 남아있을 수 있음)

### 확인 방법
```bash
# dump.rdb 파일 존재 여부
docker exec -it <컨테이너이름> ls /data/

# 마지막 저장 시간 확인
docker exec -it <컨테이너이름> redis-cli LASTSAVE

# 강제 저장
docker exec -it <컨테이너이름> redis-cli BGSAVE

# 저장된 키 확인
docker exec -it <컨테이너이름> redis-cli KEYS "*"
```

---

## AOF (Append Only File)

### 개념
- 모든 명령어를 실시간으로 파일에 기록
- Redis 재시작 시 파일을 읽어서 복구
- RDB보다 안전하지만 느리고 용량이 큼

### RDB vs AOF 비교

| | RDB | AOF |
|---|---|---|
| 저장 방식 | 주기적 스냅샷 | 실시간 명령어 기록 |
| 데이터 손실 | 마지막 스냅샷 이후 손실 가능 | 거의 손실 없음 |
| 속도 | 빠름 | 느림 |
| 파일 크기 | 작음 | 큼 |
| 용도 | 캐시, 메시지 큐 | 결제, 세션 등 중요 데이터 |

### 용도별 저장 방식 선택

```
캐시 용도          → 저장 불필요 또는 RDB
Celery 브로커 용도 → RDB (기본값으로 충분)
세션/결제 데이터   → AOF 또는 RDB + AOF
```

---

## Redis 이중화

### 구조
```
Redis Primary (쓰기/읽기)
    ↓ 자동 복제
Redis Replica (읽기 전용)
    ↓ 장애 감지
Redis Sentinel (자동 failover)
```

### 이중화가 필요한 이유
```
Primary 장애 → Replica가 Primary로 자동 승격
→ 서비스 중단 없이 운영 가능
```

### Sentinel이 필요한 이유
```
Replica만 있으면 Primary 죽어도 자동 승격 안 됨
Sentinel 3개가 과반수(2개) 동의 시 자동 failover 실행
```

### 환경별 이중화 방법

| 환경 | 방법 |
|---|---|
| 로컬 개발 | 단일 Redis (이중화 불필요) |
| Docker 배포 | Primary + Replica + Sentinel |
| AWS 배포 | ElastiCache (AWS에서 이중화 자동 관리) |

---

## Celery 브로커 대체제

| | Redis | RabbitMQ | SQS | DB |
|---|---|---|---|---|
| 속도 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| 안정성 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 설정 난이도 | 쉬움 | 보통 | 복잡 | 매우 쉬움 |
| 비용 | 무료 | 무료 | 유료 | 무료 |
| 주 용도 | 캐시 + 브로커 | 브로커 전용 | AWS 환경 | 임시방편 |

```
소규모/개발   → Redis
메시지 안정성 → RabbitMQ
AWS 배포      → ElastiCache(Redis) 또는 SQS
```

---

## RabbitMQ 개념

### 핵심 구성 요소

```
Producer  → 메시지를 보내는 쪽 (Django, Celery Beat)
Exchange  → 라우팅 담당 (어느 큐에 넣을지 결정)
Queue     → 메시지 대기 공간 (선입선출 FIFO)
Consumer  → 메시지를 처리하는 쪽 (Celery Worker)
```

### Exchange 타입

#### Direct Exchange
```
라우팅 키가 정확히 일치하는 큐 하나에만 전달

Producer → Exchange (routing_key: "email") → email 큐만 전달
                                           → sms 큐 전달 안 됨
```

#### Fanout Exchange
```
모든 큐에 동시에 전달 (브로드캐스트)

Producer → Exchange → email 큐 (동시)
                    → sms 큐   (동시)
                    → push 큐  (동시)
```

#### Topic Exchange
```
패턴 매칭으로 전달

routing_key: "order.created.korea"
→ "order.*"   매칭 ✅
→ "order.#"   매칭 ✅
→ "payment.*" 매칭 ❌
```

### Exchange vs Queue 역할 구분

| 역할 | 담당 |
|---|---|
| 어느 큐에 넣을지 | Exchange |
| 순서대로 처리 (선입선출) | Queue |

### ACK (메시지 확인) - Redis와의 차이점

```
RabbitMQ
→ Worker 작업 완료 후 ACK 전송
→ ACK 없으면 다른 Worker에게 재전달
→ 메시지 손실 없음 ✅

Redis
→ ACK 개념 없음
→ Worker 죽으면 메시지 그냥 손실 ❌
```

---

## Docker Compose Celery 배포 설정

### docker-compose.yml에 추가할 내용

```yaml
celery-worker:
  build: .
  command: celery -A config worker --loglevel=info
  env_file:
    - .env
  environment:
    DB_HOST: db
    DB_PORT: 5432
    CELERY_BROKER_URL: redis://redis:6379/0
  depends_on:
    - redis
    - db

celery-beat:
  build: .
  command: celery -A config beat --loglevel=info
  env_file:
    - .env
  environment:
    DB_HOST: db
    DB_PORT: 5432
    CELERY_BROKER_URL: redis://redis:6379/0
  depends_on:
    - redis
    - db
```

### Celery Beat 흐름

```
Celery Beat
    ↓ 정해진 시간 확인 (스케줄 관리)
    ↓ 조건 충족 시 Redis 큐에 작업 넣음
Redis
    ↓ 큐에 작업 대기
Celery Worker
    ↓ 큐에서 꺼내서 실행
analyze_weekly_task() 실행
```

```
Beat  = 알람 설정하고 울리는 역할
Redis = 알람 메모 전달
Worker = 알람 듣고 실제로 일하는 역할
```

### EC2 배포 시 코드 변경 불필요한 이유

```python
# settings.py
CELERY_BROKER_URL = "redis://localhost:6379/0"

# 로컬에서도 → localhost:6379 (Docker Redis)
# EC2에서도  → localhost:6379 (EC2 Redis)
# 주소가 같아서 코드 변경 불필요
```
