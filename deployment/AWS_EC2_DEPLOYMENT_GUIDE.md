# 🚀 AWS EC2 배포 완전 가이드

## 1️⃣ AWS EC2 인스턴스 생성

### AWS 콘솔 접속
1. [AWS 콘솔](https://console.aws.amazon.com) 로그인
2. EC2 서비스 선택
3. "Launch Instance" 클릭

### 인스턴스 설정
```
이름: UrSaviour-Production
AMI: Ubuntu Server 22.04 LTS (Free Tier)
인스턴스 타입: t3.micro (Free Tier) 또는 t3.small (더 나은 성능)
키 페어: 새로 생성하거나 기존 키 사용
```

### 보안 그룹 설정 (매우 중요!)
```
SSH (22): 0.0.0.0/0
HTTP (80): 0.0.0.0/0
HTTPS (443): 0.0.0.0/0
Custom TCP (8000): 0.0.0.0/0  # API 서버용
Custom TCP (3001): 0.0.0.0/0  # 개발용 (나중에 제거 가능)
```

### 스토리지
```
크기: 20GB (Free Tier 한도)
타입: gp3 (General Purpose SSD)
```

## 2️⃣ 서버 접속 및 초기 설정

### SSH 접속
```bash
# 키 파일 권한 설정
chmod 400 your-key.pem

# EC2 접속 (IP는 AWS 콘솔에서 확인)
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### 시스템 업데이트
```bash
sudo apt update
sudo apt upgrade -y
```

### Git 설치
```bash
sudo apt install -y git
```

## 3️⃣ Docker 설치

### Docker 설치 스크립트
```bash
# Docker 공식 설치 스크립트
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker ubuntu

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 재로그인 또는 그룹 권한 적용
newgrp docker
```

## 4️⃣ 프로젝트 배포

### 프로젝트 클론
```bash
# 프로젝트 디렉토리 생성
sudo mkdir -p /opt/ursaviour
sudo chown ubuntu:ubuntu /opt/ursaviour
cd /opt/ursaviour

# Git 클론
git clone https://github.com/JustinCoKA/UrSaviour-Project.git .
```

### 환경 변수 설정
```bash
# 프로덕션용 .env 파일 생성
cp .env.production .env

# 필요한 환경 변수 수정
nano .env
```

### 배포 실행
```bash
# 배포 스크립트 실행
chmod +x deploy.sh
./deploy.sh
```

## 5️⃣ AWS RDS (데이터베이스) 설정

### RDS 인스턴스 생성
```
엔진: MySQL 8.0
템플릿: 프리 티어
DB 인스턴스 식별자: ursaviour-db
마스터 사용자 이름: admin
마스터 암호: 강력한 암호 설정
DB 인스턴스 클래스: db.t3.micro
스토리지: 20GB
VPC: EC2와 같은 VPC
퍼블릭 액세스: 예 (개발용, 나중에 변경)
보안 그룹: MySQL/Aurora (3306) 포트 오픈
```

### 데이터베이스 연결 테스트
```bash
# EC2에서 MySQL 클라이언트 설치
sudo apt install -y mysql-client

# RDS 연결 테스트
mysql -h your-rds-endpoint -u admin -p
```

## 6️⃣ 도메인 및 HTTPS 설정

### Route 53 설정
1. 도메인 구매 또는 기존 도메인 사용
2. Hosted Zone 생성
3. A 레코드로 EC2 퍼블릭 IP 연결

### SSL 인증서 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 7️⃣ 최종 확인

### 서비스 상태 확인
```bash
# 컨테이너 상태
docker-compose -f docker-compose.prod.yml ps

# API 헬스 체크
curl http://localhost:8000/health

# 웹 사이트 접근 확인
curl http://your-domain.com
```

### 로그 확인
```bash
# API 서버 로그
docker-compose -f docker-compose.prod.yml logs -f api

# Nginx 로그
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🆘 문제 해결

### 일반적인 문제들
1. **포트 접근 안됨**: EC2 보안 그룹 확인
2. **Docker 권한 에러**: `sudo usermod -aG docker ubuntu` 실행 후 재로그인
3. **데이터베이스 연결 실패**: RDS 보안 그룹 및 VPC 설정 확인
4. **SSL 인증서 실패**: 도메인 DNS 설정 확인

### 유용한 명령어들
```bash
# 서비스 재시작
docker-compose -f docker-compose.prod.yml restart

# 서비스 중단
docker-compose -f docker-compose.prod.yml down

# 새 버전 배포
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# 시스템 리소스 확인
htop
df -h
```

## 💡 비용 최적화 팁

1. **Free Tier 사용**: t3.micro EC2 + db.t3.micro RDS
2. **예약 인스턴스**: 장기 사용시 비용 절약
3. **모니터링**: CloudWatch로 리소스 사용량 확인
4. **스케줄링**: 개발용 인스턴스는 밤에 중단

## 📞 지원

배포 중 문제가 발생하면:
1. 로그 파일 확인
2. AWS 지원 센터 문의
3. 커뮤니티 포럼 활용