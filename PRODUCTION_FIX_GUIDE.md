# 🚀 UrSaviour 프로덕션 배포 가이드

## 현재 문제
- **백엔드 Docker 컨테이너가 프로덕션 서버에서 실행되지 않음**
- Health check `/health` → HTTP 404 응답
- 프론트엔드는 정상 작동하지만 API 연결 실패

## 즉시 실행 명령어들

### 1️⃣ 서버 접속 및 프로젝트 확인
```bash
# SSH로 서버 접속 후
cd /opt/ursaviour  # 또는 프로젝트가 있는 경로

# 현재 상태 확인
docker ps -a
docker-compose ps
```

### 2️⃣ Docker 서비스 시작 (가장 중요!)
```bash
# 기존 컨테이너 정지
docker-compose -f docker-compose.prod.yml down

# 프로덕션 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### 3️⃣ 즉시 확인해야 할 것들
```bash
# API 서버 상태
curl http://localhost:8000/health
# 예상 응답: {"status":"ok"}

# 컨테이너 로그 확인
docker-compose -f docker-compose.prod.yml logs api

# 포트 확인
netstat -tlnp | grep 8000
```

### 4️⃣ 환경 변수 확인
```bash
# .env 파일 존재 확인
ls -la .env

# 주요 환경 변수 확인 (민감 정보 제외)
grep -v PASSWORD .env | grep -v SECRET | head -10
```

## 🔧 문제 해결 시나리오별 대응

### 시나리오 1: Docker가 설치되지 않음
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# 로그아웃 후 재로그인 필요
```

### 시나리오 2: Docker Compose 없음
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 시나리오 3: 환경 변수 문제
```bash
# 프로덕션 환경 파일 복사
cp .env.production .env

# 필수 환경 변수 설정
nano .env
# DATABASE_URL, SECRET_KEY, BACKEND_CORS_ORIGINS 확인/수정
```

### 시나리오 4: 포트 충돌
```bash
# 8000 포트 사용 중인 프로세스 확인
sudo lsof -i :8000
# 필요시 해당 프로세스 종료
```

### 시나리오 5: 네트워크 문제
```bash
# Docker 네트워크 재설정
docker network prune
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

## ✅ 성공 확인 체크리스트

완료되면 다음이 모두 정상이어야 합니다:

1. **Docker 컨테이너 상태**
   ```bash
   $ docker-compose -f docker-compose.prod.yml ps
   NAME     COMMAND            SERVICE   STATUS    PORTS
   api      "uvicorn..."       api       Up        8000/tcp
   web      "nginx -g..."      web       Up        80/tcp, 443/tcp
   ```

2. **Health Check**
   ```bash
   $ curl http://localhost:8000/health
   {"status":"ok"}
   ```

3. **웹사이트 접속**
   - https://ursaviour.com/products.html 접속
   - 제품이 정상 로드됨
   - 콘솔에 오류 없음

## 🆘 긴급상황 연락처
- 개발팀 Slack: #dev-emergency
- 문제 발생 시 스크린샷과 함께 docker logs 공유

---
**⏰ 예상 복구 시간: 5-15분**
**👥 필요 권한: 서버 SSH 접속, Docker 실행 권한**