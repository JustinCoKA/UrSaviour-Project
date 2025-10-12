#!/bin/bash

# AWS EC2 자동 배포 스크립트
# 사용법: ./aws-deploy.sh

set -e  # 에러 발생시 스크립트 중단

echo "🚀 AWS EC2 UrSaviour 배포 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 시스템 환경 확인
check_system() {
    log_info "시스템 환경 확인 중..."
    
    # 운영체제 확인
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Linux 환경 감지됨"
    else
        log_error "이 스크립트는 Linux 환경에서 실행해야 합니다."
        exit 1
    fi
    
    # 필수 디렉토리 확인
    if [ ! -f "docker-compose.prod.yml" ]; then
        log_error "docker-compose.prod.yml 파일을 찾을 수 없습니다."
        exit 1
    fi
}

# 2. Docker 설치 확인 및 설치
install_docker() {
    log_info "Docker 설치 상태 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        log_warn "Docker가 설치되지 않음. Docker 설치 중..."
        
        # Docker 공식 설치 스크립트
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        
        # 현재 사용자를 docker 그룹에 추가
        sudo usermod -aG docker $USER
        
        log_info "Docker 설치 완료"
    else
        log_info "Docker가 이미 설치되어 있습니다."
    fi
    
    # Docker Compose 확인 및 설치
    if ! command -v docker-compose &> /dev/null; then
        log_warn "Docker Compose가 설치되지 않음. 설치 중..."
        
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        log_info "Docker Compose 설치 완료"
    else
        log_info "Docker Compose가 이미 설치되어 있습니다."
    fi
}

# 3. 환경 변수 설정
setup_environment() {
    log_info "환경 변수 설정 중..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.aws.production" ]; then
            log_info "AWS 프로덕션 환경 변수 파일을 복사합니다..."
            cp .env.aws.production .env
            log_warn "⚠️  .env 파일을 편집해서 실제 값들을 입력하세요!"
            echo "   - RDS 엔드포인트 및 비밀번호"
            echo "   - AWS 액세스 키"
            echo "   - 도메인 이름"
            echo "   - JWT 시크릿"
        else
            log_error ".env.aws.production 파일을 찾을 수 없습니다."
            exit 1
        fi
    else
        log_info ".env 파일이 이미 존재합니다."
    fi
}

# 4. 기존 서비스 중단
stop_existing_services() {
    log_info "기존 서비스 중단 중..."
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml down
        log_info "기존 서비스가 중단되었습니다."
    else
        log_info "실행 중인 서비스가 없습니다."
    fi
}

# 5. 이미지 빌드 및 서비스 시작
deploy_services() {
    log_info "Docker 이미지 빌드 및 서비스 시작 중..."
    
    # 이미지 빌드 및 서비스 시작
    docker-compose -f docker-compose.prod.yml up -d --build
    
    log_info "서비스가 시작되었습니다."
}

# 6. 헬스 체크
health_check() {
    log_info "서비스 상태 확인 중..."
    
    # 30초 대기
    sleep 30
    
    # API 서버 헬스 체크
    max_attempts=10
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "API 서버 헬스 체크 시도 $attempt/$max_attempts..."
        
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "✅ API 서버가 정상적으로 실행되고 있습니다!"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                log_error "❌ API 서버 헬스 체크 실패"
                log_error "로그를 확인하세요: docker-compose -f docker-compose.prod.yml logs api"
                exit 1
            fi
            log_warn "헬스 체크 실패. 5초 후 재시도..."
            sleep 5
            ((attempt++))
        fi
    done
    
    # 웹 서버 확인
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        log_info "✅ 웹 서버가 정상적으로 실행되고 있습니다!"
    else
        log_warn "⚠️  웹 서버 접근에 문제가 있을 수 있습니다."
    fi
}

# 7. 배포 상태 출력
show_status() {
    log_info "배포 완료! 현재 상태:"
    echo ""
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    log_info "🌐 웹사이트: http://$(curl -s ifconfig.me)"
    log_info "🔧 API: http://$(curl -s ifconfig.me):8000"
    log_info "📊 상태 확인: http://$(curl -s ifconfig.me):8000/health"
    echo ""
    log_info "🔍 로그 확인:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f api"
    echo "   docker-compose -f docker-compose.prod.yml logs -f web"
    echo ""
    log_info "🛠  서비스 관리:"
    echo "   재시작: docker-compose -f docker-compose.prod.yml restart"
    echo "   중단: docker-compose -f docker-compose.prod.yml down"
    echo "   업데이트: git pull && ./aws-deploy.sh"
}

# 메인 실행 함수
main() {
    log_info "========================================="
    log_info "      AWS EC2 UrSaviour 배포 스크립트"
    log_info "========================================="
    echo ""
    
    check_system
    install_docker
    setup_environment
    stop_existing_services
    deploy_services
    health_check
    show_status
    
    echo ""
    log_info "🎉 배포가 성공적으로 완료되었습니다!"
    echo ""
}

# 스크립트 실행
main "$@"