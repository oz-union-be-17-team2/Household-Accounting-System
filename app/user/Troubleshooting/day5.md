## 2026.04.12


### 쿠키 보안 옵션 3개

**`httponly=True`** → JS로 쿠키 접근 차단 (XSS 방어)

**`secure=True`** → HTTPS에서만 쿠키 전송 (패킷 도청 방어)

**`samesite="Lax"`** → 외부 사이트 POST 요청에 쿠키 차단 (CSRF 방어)

**`samesite="Strict"`** → 무조건 같은 사이트 요청만 쿠키 허용.
-  외부 링크 GET 요청도 차단해서, 카카오톡 링크 타고 들어오면 쿠키 안 붙어서 로그인 풀려보임. 보안은 더 강한데 UX 문제 있어서 보통 `Lax` 씀.

### HTTP vs HTTPS

HTTPS = HTTP + TLS 암호화

TLS가 추가한 것: 암호화 / 서버 인증 / 변조 감지

---

### CSRF

다른 사이트가 로그인된 사용자인 척 요청 보내는 공격. `samesite` 가 쿠키 레벨에서 방어.

---

### not settings.DEBUG

| 환경 | DEBUG | secure | 결과 |
|------|-------|--------|------|
| 로컬 | True | False | HTTP도 쿠키 전송 됨 |
| 배포 | False | True | HTTPS만 쿠키 전송 |

`DEBUG` 값을 바꾸는 게 아니라, `DEBUG` 값을 읽어서 `secure` 를 뭘로 할지 결정하는 것.
로컬에서 `secure=True` 고정하면 HTTP라 쿠키 전송 자체가 안 돼서 개발 불가. 차단 `UX 문제 있음` 라 쿠키 전송 자체가 안 돼서 개발 불가.
