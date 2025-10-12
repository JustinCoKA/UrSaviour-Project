# 🧹 AWS 배포 준비 완료 - 환경 변수 설정 가이드

## ✅ 정리 완료 사항

### 🗑️ 삭제된 불필요한 파일/디렉토리:
- `debug/` - 디버그용 HTML 파일들
- `diagnose-api-issues.sh` - 중복 스크립트
- `fix-api-404.sh` - 중복 스크립트  
- `get-docker.sh` - 중복 스크립트
- `local_api_server.py` - 로컬 개발용만 사용
- `schema_dump.txt` - 임시 파일
- `.env.production` - 중복 환경 파일
- `ur.pem` - 보안 키 파일
- `.idea/`, `.vscode/` - IDE 설정 디렉토리
- `.DS_Store` - macOS 시스템 파일

### ✏️ 수정된 파일들:
- `.env.aws.production` - 실제 AWS RDS 정보로 업데이트
- `.gitignore` - 보안 및 임시 파일 제외 규칙 추가

## 🎯 AWS 배포 전 필수 설정

### 1️⃣ `.env.aws.production` 파일에서 변경해야 할 값들:

```bash
# ⚠️ 실제 RDS 마스터 비밀번호로 변경
DB_PASSWORD=YOUR_RDS_PASSWORD
DATABASE_URL=mysql://admin:YOUR_RDS_PASSWORD@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviour

# ⚠️ 실제 AWS 액세스 키로 변경  
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY

# ⚠️ EC2 퍼블릭 IP나 도메인으로 변경
BACKEND_CORS_ORIGINS=["http://YOUR_EC2_IP", "https://YOUR_DOMAIN.com"]
FRONTEND_URL=http://YOUR_EC2_IP

# ⚠️ 강력한 JWT 시크릿 키 생성 (32자 이상)
SECRET_KEY=YOUR_SUPER_SECRET_JWT_KEY_GENERATE_NEW_ONE

# ⚠️ 이메일 설정 (선택사항)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2️⃣ JWT 시크릿 키 생성 명령어:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3️⃣ AWS 액세스 키 발급:
1. AWS IAM 콘솔 접속
2. 사용자 생성 또는 기존 사용자 선택
3. "보안 자격 증명" 탭에서 액세스 키 생성
4. 권한: AmazonRDSFullAccess, AmazonS3FullAccess

## 🚀 다음 배포 단계

### 1. EC2 인스턴스 생성
- **리전**: ap-southeast-2 (Sydney) ⚠️ 필수
- **VPC**: vpc-09b863de1b93fc683
- **보안 그룹**: HTTP(80), HTTPS(443), SSH(22), API(8000), MySQL(3306)

### 2. EC2에서 배포 명령어:
```bash
# EC2 SSH 접속
ssh -i "your-key.pem" ubuntu@your-ec2-ip

# 프로젝트 클론
git clone https://github.com/JustinCoKA/UrSaviour-Project.git /opt/ursaviour
cd /opt/ursaviour

# 환경 설정
cp .env.aws.production .env
nano .env  # 실제 값들 입력

# 자동 배포
sudo chmod +x aws-deploy.sh
./aws-deploy.sh
```

### 3. 배포 후 확인:
- 웹사이트: `http://your-ec2-ip`
- API: `http://your-ec2-ip:8000`
- 헬스체크: `http://your-ec2-ip:8000/health`

## 📋 현재 프로젝트 구조 (정리 후):

```
UrSaviour-Project/
├── 🔧 Configuration
│   ├── .env.aws.production     # AWS 프로덕션 환경변수
│   ├── docker-compose.prod.yml # 프로덕션 Docker 설정
│   └── aws-deploy.sh          # 자동 배포 스크립트
├── 📚 Documentation  
│   ├── README.md
│   ├── PROJECT_STRUCTURE.md
│   └── deployment/            # 배포 가이드들
├── 🐍 Backend
│   └── backend/              # FastAPI 서버
├── 🌐 Frontend
│   └── frontend/             # HTML/JS/CSS
└── 📊 Data
    └── data/                 # CSV 데이터 파일들
```

## 🔒 보안 체크리스트:
- ✅ .env 파일이 .gitignore에 포함됨
- ✅ 개발용 파일들 제거됨  
- ✅ IDE 설정 파일들 제거됨
- ✅ 보안 키 파일(.pem) 제거됨
- ✅ 프로덕션용 DEBUG=False 설정됨

## 🎉 배포 준비 완료!
모든 파일이 정리되고 AWS 설정이 적용되었습니다. 이제 EC2 인스턴스만 생성하면 바로 배포할 수 있습니다!