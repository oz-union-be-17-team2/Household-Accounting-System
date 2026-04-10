# 테스트 전역 기본값 설적

루트 경로에 conftest.py는 pytest에서 임포트하지 않아도 사용할 수 있도록 된다
파이테스트를 실행했을 때 자동으로 루트에 conftest를 탐색해 주입하는 방식

## 오버라이드 하는 방법

자신의 app내에서 conftest.py를 생성해 같은 이름으로 작성하면 오버라이드 한 것처럼 사용된다

(1)root.conftest.user 와 (2)app.conftest.user가 있을 경우 테스트 실행 위치가 app일 때 후자(2)가 사용된다.
