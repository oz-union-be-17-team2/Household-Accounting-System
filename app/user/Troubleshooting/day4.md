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
