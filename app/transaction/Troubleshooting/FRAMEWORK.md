# Web Framework의 흐름(DRF)

---
### 전체 web framework 흐름
```
클라이언트 (Postman, 브라우저 등)
    ⬇ HTTP 요청 (GET, POST, PUT, DELETE)

config/urls.py
    ⬇ 요청 URL에 맞는 앱 urls.py로 라우팅

app/transaction/urls.py
    ⬇ 해당 View 클래스로 연결

app/transaction/views.py
    ⬇ permission_classes ➡ 인증확인 (JWT 토큰)
    ⬇ get_queryset() ➡ DB에서 데이터 조회
    ⬇ perform_create() ➡ 데이터 저장

app/transaction/serializers.py
    ⬇ 조회 시 ➡ DB 데이터를 JSON으로 변환
    ⬇ 생성/수정 시 ➡ 클라이언트 데이터 유효성 검사 후 DB에 저장

app/transaction/models.py
    ⬇ DB 테이블 구조 정의

PostgreSQL (Docker)
    ⬇ 실제 데이터 저장/조회

클라이언트에게 JSON 응답 반환
```
---
### view framework 흐름
```
HTTP 요청 들어옴
    ⬇

permission_classes 확인
    ⬇ 인증 실패 ➡ 401반환(IsAuthenticated에서 자동 처리)
    ⬇ 인증 성공 ➡ 200반환

GET 요청 (조회)
    ⬇ get_queryset() 실해
    ⬇ filter(user=self.requst.user) ➡ 본인 테이터만
    ⬇ select_related("account") ➡ account JOIN
    ⬇ 필터링 조건 적용 (type, amount_min, amount_max)
    ⬇ serializer로 JSON 변환 후 반환

POST 요청 (생성)
    ⬇ seializer로 데이터 유효성 검사
    ⬇ perform_create() 실행
    ⬇ seializer.save(user=self.requser.user) ➡ user 자동 주입 후 JSON형태로 저장
    ⬇ 201 반환

PUT/PATCH 요청 (수정)
    ⬇ get_queryset()으로 본인 데이터 확인
    ⬇ serializer로 데이터 유효성 검사 후 저장
    ⬇ 200 반환

DELETE 요청 (삭제)
    ⬇ get_queryset()으로 본인 데이터 확인
    ⬇ 삭제
    ⬇ 204 반환
```
