#!/bin/bash

# UrSaviour 안전한 AWS 배포 스크립트
# 문제 해결 및 단계별 배포

set -e

echo "🔧 UrSaviour 배포 문제 해결 중..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 현재 위치 확인
log_info "현재 디렉토리 확인..."
pwd
ls -la

# 2. 최신 코드 업데이트
log_info "최신 코드 가져오기..."
git pull origin main

# 3. nginx 설정 파일이 frontend에 있는지 확인
log_info "nginx 설정 파일 확인..."
if [ ! -f "frontend/default.conf" ]; then
    log_warn "frontend/default.conf가 없습니다. deployment에서 복사중..."
    if [ -f "deployment/default.conf" ]; then
        cp deployment/default.conf frontend/
        log_info "nginx 설정 파일 복사 완료"
    else
        log_error "deployment/default.conf 파일을 찾을 수 없습니다!"
        exit 1
    fi
else
    log_info "nginx 설정 파일이 이미 존재합니다"
fi

# 4. 환경 변수 파일 확인
log_info "환경 변수 파일 확인..."
if [ ! -f ".env" ]; then
    if [ -f ".env.aws.production" ]; then
        log_info ".env.aws.production을 .env로 복사합니다"
        cp .env.aws.production .env
    else
        log_error ".env 파일이 없습니다!"
        exit 1
    fi
fi

# 5. 기존 컨테이너 정리
log_info "기존 컨테이너 정리..."
docker compose -f docker-compose.prod.yml down --remove-orphans || true
docker system prune -f || true

# 6. 이미지 빌드 (캐시 없이 새로 빌드)
log_info "Docker 이미지 빌드 중..."
docker compose -f docker-compose.prod.yml build --no-cache

# 7. 서비스 시작
log_info "서비스 시작 중..."
docker compose -f docker-compose.prod.yml up -d

# 8. 서비스 상태 확인
log_info "서비스 상태 확인 중..."
sleep 10
docker compose -f docker-compose.prod.yml ps

# 9. 헬스 체크
log_info "헬스 체크 수행 중..."
sleep 30

# API 헬스 체크
for i in {1..10}; do
    log_info "API 헬스 체크 시도 $i/10..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ API 서버가 정상 작동합니다!"
        break
    else
        if [ $i -eq 10 ]; then
            log_error "❌ API 서버 헬스 체크 실패"
            docker compose -f docker-compose.prod.yml logs api
            exit 1
        fi
        log_warn "API 서버 시작 중... 5초 후 재시도"
        sleep 5
    fi
done

# 웹 서버 확인
if curl -f http://localhost > /dev/null 2>&1; then
    log_info "✅ 웹 서버가 정상 작동합니다!"
else
    log_warn "⚠️ 웹 서버 접근에 문제가 있을 수 있습니다"
    docker compose -f docker-compose.prod.yml logs web
fi

# 10. 최종 상태 출력
log_info "🎉 배포 완료! 현재 상태:"
echo ""
docker compose -f docker-compose.prod.yml ps
echo ""
log_info "🌐 웹사이트: http://$(curl -s ifconfig.me || echo 'YOUR-EC2-IP')"
log_info "🔧 API: http://$(curl -s ifconfig.me || echo 'YOUR-EC2-IP'):8000"
log_info "📊 헬스체크: http://$(curl -s ifconfig.me || echo 'YOUR-EC2-IP'):8000/health"
echo ""
log_info "🔍 로그 확인 명령어:"
echo "   docker compose -f docker-compose.prod.yml logs -f api"
echo "   docker compose -f docker-compose.prod.yml logs -f web"

log_info "✅ 배포가 성공적으로 완료되었습니다!"