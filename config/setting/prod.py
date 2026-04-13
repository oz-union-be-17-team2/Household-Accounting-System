from .base import *  # noqa: F401, F403

# 프로덕션 환경에서는 반드시 False
DEBUG = False

# EC2 퍼블릭 IP 또는 도메인을 .env의 ALLOWED_HOSTS에 추가
# 예: ALLOWED_HOSTS=123.456.789.0,mydomain.com
