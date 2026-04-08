## ERD

```mermaid
erDiagram
    USER {
        int id PK
        varchar email
        varchar password
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime last_login
        datetime created_at
        varchar name
        varchar nickname
        varchar phone_number
        boolean is_deleted
        datetime updated_at
    }

    ACCOUNT {
        int id PK
        int user_id FK
        varchar account_type
        decimal balance
        varchar bank_code
        varchar account_number
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    TRANSACTION {
        int id PK
        int user_id FK
        int from_account_id FK
        int to_account_id FK
        decimal amount
        decimal balance_after
        varchar description
        varchar status
        varchar transaction_type
        datetime created_at
        datetime updated_at
    }

    USER ||--o{ ACCOUNT : "소유"
    USER ||--o{ TRANSACTION : "발생"
    ACCOUNT ||--o{ TRANSACTION : "출금 계좌(from)"
    ACCOUNT ||--o{ TRANSACTION : "입금 계좌(to)"
```

## 사용자 인증 플로우차트

### 회원가입
```mermaid
flowchart TD
    A([시작]) --> B[이메일/이름/닉네임\n휴대폰번호/비밀번호 입력]
    B --> C{유효성 검사}
    C -- 실패 --> D[오류 반환]
    C -- 통과 --> E[비밀번호 암호화\nset_password]
    E --> F[User DB 저장]
    F --> G[201 Created 반환]
```

### 로그인
```mermaid
flowchart TD
    A([시작]) --> B[이메일/비밀번호 입력]
    B --> C{이메일/비밀번호 검증}
    C -- 실패 --> D[401 Unauthorized 반환]
    C -- 성공 --> E[JWT 발급\nAccess + Refresh Token]
    E --> F[쿠키에 토큰 저장 후 반환]
```

### 로그아웃
```mermaid
flowchart TD
    A[로그아웃 요청] --> B[Refresh Token 블랙리스트 추가]
    B --> C[쿠키 삭제 후 200 반환]
```
