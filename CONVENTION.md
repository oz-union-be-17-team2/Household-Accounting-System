# 📐 프로젝트 컨벤션

## 유저 스토리

> 가상인물: 32살, 회사원, 남성

### 회원가입

1. 이메일로 회원가입 (추후 소셜 회원가입으로 확장 가능)
2. 인증 방법은 이메일 인증
3. 필수 입력: 이메일, 비밀번호, 닉네임
4. 선택 입력: 성별, 나이, 직업 (데이터 분석 시 참고)
5. 관리자 계정과 일반 유저 계정 구분
6. 이메일 인증 여부에 따라 계정 활성화/비활성화 구분

### 로그인

1. 이메일 + 비밀번호로 로그인 (추후 소셜 로그인 확장 가능)
2. 아이디/비밀번호 찾기 (현재 미구현)

### 계좌

1. 수동으로 계좌 추가
2. 계좌별 은행이름, 금액, 입출금/적금/예금 표시

### 거래내역

1. 최신순 정렬 (오래된순 변경 가능, 기간 직접 설정)
2. 거래내역 비고 수정 가능
3. 계좌별 은행이름, 금액, 입출금/적금/예금 표시
4. 거래 유형별 필터링 (예: 입금만 최신순 조회)

---

## Git 컨벤션

### 브랜치 전략

- 각자 로컬 브랜치를 앱 이름으로 생성한다. (`transaction`, `user`, `account`)
- 로컬 브랜치 → GitHub `develop` 브랜치로 PR한다.
- `main` 브랜치에 직접 push하지 않는다.
- PR 단위는 클래스 단위로 한다. (예: `TransactionListView` 구현 완료 시 PR)

### 커밋 메시지

```
타입: 한 줄 요약
```

| 타입 | 설명 |
|---|---|
| `feat` | 새로운 기능 추가 |
| `fix` | 기능 수정, 버그 수정, 코드 리팩터링 |
| `chore` | 오타 수정 및 코드 변경 (주석 포함) |
| `docs` | 문서 수정 (README 등) |
| `test` | 테스트 코드 추가/수정 |

예시:
```
feat: TransactionListView 구현
fix: serializer read_only_fields 오류 수정
docs: CONVENTION.md 작성
test: Transaction CRUD 테스트 코드 추가
```

---

## 폴더 구조

```
Household-Accounting-System/
├── .github/
│   └── workflows/
│       └── checks.yml          # GitHub Actions CI 설정
├── app/                        # Django 앱 모음
│   ├── account/                # 계좌 CRD (APIView)
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── notification/           # 알림 (추후 확장)
│   ├── transaction/            # 거래내역 CRUD + 필터링 (Generic View)
│   │   ├── migrations/
│   │   ├── Troubleshooting/    # 트러블슈팅 기록
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── user/                   # 회원가입, 로그인, 로그아웃 (APIView)
│       ├── migrations/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── tests.py
│       └── views.py
├── config/                     # 프로젝트 설정
│   ├── setting/
│   │   ├── base.py             # 개발 설정
│   │   └── prod.py             # 배포 설정
│   ├── urls.py                 # 루트 URL
│   ├── asgi.py
│   └── wsgi.py
├── core/                       # 공통 유틸리티
│   ├── admin.py
│   └── models.py               # TimeStampModel (추상 베이스 모델)
├── scripts/
│   └── run.sh                  # 서버 실행 스크립트
├── .env                        # 환경변수 (git 제외)
├── .env.example                # 환경변수 템플릿
├── .pre-commit-config.yaml     # pre-commit 훅 설정
├── docker-compose.dev.yml      # 개발용 Docker 설정
├── Dockerfile
├── manage.py
├── pyproject.toml              # 의존성 및 Ruff 설정
├── CONVENTION.md               # 팀 컨벤션 문서
└── README.md
```

---

## 코드 품질 관리

### 2중 방어 구조

```
git commit  →  pre-commit 훅  →  Ruff 실행  →  코드 품질/유효성 검사  →  통과하면 커밋 완료
     ↓
git push  →  GitHub Actions (CI)  →  Ruff 실행  →  코드 품질/유효성 검사  →  통과하면 push 완료
```

### pre-commit

- `git commit` 시 자동으로 실행되는 Git 훅
- Ruff를 실행해서 코드 품질/유효성 검사
- 실패하면 커밋이 막히고 자동으로 수정
- 나쁜 코드가 **커밋되는 걸** 막음

### CI (GitHub Actions)

- `git push` 시 GitHub 서버에서 자동으로 실행
- Ruff를 실행해서 코드 품질/유효성 검사
- 실패하면 push가 막힘
- 나쁜 코드가 **팀 코드베이스(develop)에 들어오는 걸** 막음

### 초기 세팅

```bash
uv sync --dev
pre-commit install
```

---

## 환경변수 관리

- `.env` 파일은 git에 올리지 않는다.
- 새로운 환경변수 추가 시 `.env.example`도 반드시 같이 업데이트한다.
- 실제 값은 팀원끼리 따로 공유한다. (디스코드, 노션 등)
