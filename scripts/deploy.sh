#!/bin/bash
# ============================================================
# Zero-Downtime Rolling Deploy Script
# 실행 위치: EC2 서버
# 전략: web1 → web2 순서로 순차 재시작 (무중단 배포)
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
echo " Rolling Deploy 시작"
echo "======================================"

echo ""
echo "[1/5] 최신 이미지 Pull..."
docker compose -f "$COMPOSE_FILE" pull web1 web2

echo ""
echo "[2/5] Redis 및 공통 서비스 기동..."
docker compose -f "$COMPOSE_FILE" up -d redis

echo ""
echo "[2.5/5] DB 마이그레이션 및 정적 파일 수집 (1회만 실행)..."
docker compose -f "$COMPOSE_FILE" run --rm \
    -e DJANGO_SETTINGS_MODULE=config.setting.prod \
    web1 sh -c "uv run python manage.py migrate && uv run python manage.py collectstatic --noinput"

echo ""
echo "[3/5] web1 롤링 재시작 (web2가 트래픽 처리)..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate web1

echo "  web1 health check 대기 중 (최대 60s)..."
for i in $(seq 1 12); do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' \
        "$(docker compose -f "$COMPOSE_FILE" ps -q web1)" 2>/dev/null || echo "starting")
    if [ "$STATUS" = "healthy" ]; then
        echo "  web1 healthy!"
        break
    fi
    echo "  ($((i * 5))s) 상태: $STATUS..."
    sleep 5
done

echo ""
echo "[4/5] web2 롤링 재시작 (web1이 트래픽 처리)..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps --force-recreate web2

echo "  web2 health check 대기 중 (최대 60s)..."
for i in $(seq 1 12); do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' \
        "$(docker compose -f "$COMPOSE_FILE" ps -q web2)" 2>/dev/null || echo "starting")
    if [ "$STATUS" = "healthy" ]; then
        echo "  web2 healthy!"
        break
    fi
    echo "  ($((i * 5))s) 상태: $STATUS..."
    sleep 5
done

echo ""
echo "[5/5] Nginx 기동 (두 웹 서버 모두 healthy)..."
docker compose -f "$COMPOSE_FILE" up -d --no-deps nginx

echo ""
echo "사용하지 않는 이미지 정리..."
docker image prune -f

echo ""
echo "======================================"
echo " 배포 완료!"
echo "======================================"
docker compose -f "$COMPOSE_FILE" ps
