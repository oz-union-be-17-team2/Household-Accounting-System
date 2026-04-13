## 2026.04.09

### 이메일/로그인/로그아웃/토큰재발급 기능 구현

**구조 - 책임 분리**
- `serializers.py` — 이메일/비밀번호 형식 검증
- `services.py` — 인증, 토큰 생성/블랙리스트 비즈니스 로직
- `views.py` — 요청 받고 응답 반환 + 쿠키 세팅
- `authentication.py` — 쿠키에서 JWT 토큰 꺼내는 커스텀 인증 클래스

---

### 구현 내용

**회원가입**
- `RegisterSerializer` — 이메일 중복 검사, 비밀번호 유효성 검사, 비밀번호 일치 확인
- `RegisterView` — 검증 후 유저 생성, 201 반환

**로그인**
- `LoginSerializer` — 이메일/비밀번호 형식 검증
- `login()` service — `authenticate()`로 유저 인증, JWT 발급
- `LoginView` — 토큰 쿠키에 저장, `httponly=True`로 XSS 방어

**로그아웃**
- `logout()` service — Refresh Token 블랙리스트 추가
- `LogoutView` — 쿠키 삭제, `IsAuthenticated`로 인증된 유저만 접근 가능

**토큰 재발급**
- `token_refresh()` service — Refresh Token으로 새 Access Token 발급
- `TokenRefreshView` — 쿠키에서 Refresh Token 꺼내서 새 Access Token 쿠키에 저장

**CookieJWTAuthentication**
- `JWTAuthentication` 상속
- 헤더 대신 쿠키에서 Access Token 꺼내도록 `authenticate()` 오버라이드
- `settings.py` `DEFAULT_AUTHENTICATION_CLASSES`에 등록
- Swagger fallback으로 `JWTAuthentication` 같이 등록

---

### 헷갈렸던 부분

- 어드민 로그인 안됨 -> `create_superuser`에 `is_active=True` 없었음. 추가함
- `ALLOWED_HOSTS` 에러 -> `.env`에 `127.0.0.1` 없었음 -> `ALLOWED_HOSTS=127.0.0.1,localhost` 추가
- 커밋 전 ruff 안 돌림 -> 커밋 전 `ruff check --fix .` 습관화

---

### 미완료
- 이메일 인증 기능 (`is_active=False` → 인증 후 `True`) — 내일 구현 예정, 이메일 전 인증넘어가려면 True로 임시로 바꾸기
