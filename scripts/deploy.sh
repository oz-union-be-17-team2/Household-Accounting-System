#!/bin/bash
# ============================================================
# Deploy Script
# 실행 위치: EC2 서버
# ============================================================
set -e

DEPLOY_DIR="/home/ubuntu/household-accounting"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.prod.yml"

# EC2에 직접 설치된 Nginx가 있다면 비활성화 (최초 1회)
if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "[초기 설정] EC2 Nginx 서비스 중지 (Docker Nginx로 대체)..."
    sudo systemctl stop nginx
    sudo systemctl disable nginx
fi

cd "$DEPLOY_DIR"

echo "======================================"
echo " Deploy 시작"
echo "======================================"

echo ""
echo "[1/4] 최신 이미지 Pull..."
docker compose -f "$COMPOSE_FILE" pull web

echo ""
echo "[2/4] Redis 기동..."
docker compose -f "$COMPOSE_FILE" up -d redis

echo ""
echo "[3/4] DB 마이그레이션 및 정적 파일 수집..."
docker compose -f "$COMPOSE_FILE" run --rm \
    -e DJANGO_SETTINGS_MODULE=config.setting.prod \
    web sh -c "uv run python manage.py migrate && uv run python manage.py collectstatic --noinput"

echo ""
echo "[4/4] web 및 nginx 기동..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate web
docker compose -f "$COMPOSE_FILE" up -d --no-deps nginx

echo ""
echo "사용하지 않는 이미지 정리..."
docker image prune -f

echo ""
echo "======================================"
echo " 배포 완료!"
echo "======================================"
docker compose -f "$COMPOSE_FILE" ps
