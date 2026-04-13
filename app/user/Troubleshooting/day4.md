## 2026.04.10

### 회원정보 조회/수정/삭제 기능 구현

UserProfileView 구현 (APIView)
- GET: 본인 프로필 조회
- PATCH: 회원정보 수정 (변경할 필드만 보내면 됨)
- DELETE: 소프트 딜리트 (is_delete=True, DB row 유지)
- 하드 딜리트 : request.user.delete()
PUT vs PATCH
- PUT은 전체 필드 다 보내야 함. 일부만 보내면 나머지 null로 덮어씌움
- PATCH는 변경할 필드만 보내면 나머지 유지됨
- 회원정보 수정은 PATCH가 적합함

권한 제한
- permission_classes = [IsAuthenticated]로 로그인한 유저만 접근 가능
- request.user로 현재 로그인한 유저만 조회/수정/삭제됨

새롭게 알게 된 점
- app/user/serializers.py
  - create() 에서 선택 필드(gender, job) None 대신 `""` 반환하도록 수정
  - validated_data.get("gender") → validated_data.get("gender", "")
  - NOT NULL 제약 조건 위반 방지

- 소프트 딜리트는 DB에서 row를 지우는 게 아니라 is_delete=True로 변경하는것.
변경사항을 DB에 저장해야 하니까 save() 필요. -> `request.user.save()` 추가

### Swagger 문서화 설정
- drf-spectacular을 사용해서 API 문서를 자동 생성함.

설정 내용
settings.py

DEFAULT_SCHEMA_CLASS 추가 — drf-spectacular가 view 읽고 자동으로 API 스키마 생성
SPECTACULAR_SETTINGS 추가 — Swagger UI 제목/설명/버전 설정, Bearer 토큰 입력창 생성

config/urls.py

/api/schema/ — API 스키마 json 반환
/api/docs/ — Swagger UI 페이지


authentication.py
CookieJWTAuthentication은 쿠키 방식이라 Swagger가 인식 못 함.
OpenApiAuthenticationExtension 상속받아서 Swagger에 등록.
get_security_definition에서 Bearer 방식으로 정의.

extend_schema
각 view 메서드에 붙이는 데코레이터. Swagger UI에 표시될 내용 커스텀.

summary — API 제목
description — 상세 설명
request — 요청 body 형식. 시리얼라이저 넣으면 필드 자동 표시
responses — 상태코드별 응답 설명

성공 응답 → 시리얼라이저
에러 응답 → OpenApiResponse (설명만 필요할 때)

### 어드민 페이지 설정
admin.py 구성

- list_display — 목록 페이지에서 보여줄 컬럼
- search_fields — 검색창에서 검색 가능한 필드
- list_filter — 오른쪽 사이드바 필터 버튼


#### is_staff vs is_superuser

- is_staff=True — 어드민 페이지 로그인 가능. 권한은 별도로 부여해야 함. 기본적으로 아무것도 못 함
- is_superuser=True — 어드민 페이지 + 모든 권한 자동으로 가짐. 권한 체크 자체를 bypass


#### 어드민 페이지 접근 조건

- is_staff=True 인 유저만 접근 가능
- is_superuser=True 면 모든 모델 읽기/쓰기/삭제 가능
- is_staff=True 만 있으면 어드민 로그인은 되는데 권한 없으면 아무것도 못 함
