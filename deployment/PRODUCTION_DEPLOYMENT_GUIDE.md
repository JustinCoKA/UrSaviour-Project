# Production Deployment Guide

## 🚨 현재 문제: Backend Service가 실행되지 않음

### 1. 서버 접속 및 상태 확인
```bash
# 서버에 SSH로 접속 후
cd /path/to/UrSaviour-Project

# Docker 상태 확인
docker ps -a
docker-compose ps

# 로그 확인
docker-compose logs
```

### 2. 백엔드 서비스 시작
```bash
# Production 환경으로 Docker Compose 실행
docker-compose -f docker-compose.prod.yml up -d

# 또는 일반 docker-compose 사용
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
curl http://localhost:8000/health
```

### 3. Nginx 재시작 (필요시)
```bash
# Nginx 설정 확인
nginx -t

# Nginx 재시작
systemctl restart nginx
# 또는
service nginx restart
```

### 4. 전체 시스템 재시작 (마지막 수단)
```bash
# 모든 컨테이너 중지
docker-compose down

# 이미지 재빌드 및 시작
docker-compose -f docker-compose.prod.yml up -d --build

# 서비스 상태 확인
docker-compose ps
docker-compose logs api
```

### 5. 포트 및 네트워크 확인
```bash
# 포트 8000이 열려있는지 확인
netstat -tlnp | grep 8000
ss -tlnp | grep 8000

# Docker 네트워크 확인
docker network ls
docker network inspect ursaviour-project_default
```

## 🔧 문제 해결 체크리스트

- [ ] Docker가 설치되어 있는가?
- [ ] Docker Compose가 설치되어 있는가?
- [ ] 환경 변수(.env 파일)가 올바른가?
- [ ] 포트 8000이 사용 가능한가?
- [ ] Nginx 설정이 올바른가?
- [ ] 방화벽에서 포트가 열려있는가?

## 📋 Expected Status After Fix

### Healthy State:
```bash
$ docker-compose ps
NAME                COMMAND             SERVICE             STATUS              PORTS
api                 "uvicorn..."        api                 Up                  8000/tcp
nginx               "nginx -g..."       nginx               Up                  0.0.0.0:80->80/tcp
```

### Health Check:
```bash
$ curl http://localhost:8000/health
{"status":"ok"}

$ curl https://ursaviour.com/health
{"status":"ok"}
```