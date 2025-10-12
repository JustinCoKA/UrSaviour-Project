# 🎯 실제 RDS 데이터베이스 연결 설정

## 데이터베이스 정보
```
엔드포인트: ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com
포트: 3306
리전: ap-southeast-2 (시드니)
VPC: vpc-09b863de1b93fc683
보안 그룹: ursaviour-db-sg (sg-0cf1dedfd2c17e246)
```

## EC2 배포시 필요한 설정

### 1. EC2 인스턴스는 같은 리전에 생성해야 함
- **리전**: ap-southeast-2 (Asia Pacific - Sydney)
- **VPC**: vpc-09b863de1b93fc683 (RDS와 동일한 VPC)

### 2. EC2 보안 그룹 설정
EC2 인스턴스의 보안 그룹에 다음 규칙 추가:
```
Type: Custom TCP
Port: 3306
Source: sg-0cf1dedfd2c17e246 (RDS 보안 그룹)
Description: MySQL access to RDS
```

### 3. RDS 보안 그룹 설정 확인
RDS 보안 그룹 `ursaviour-db-sg`에 다음 규칙이 있는지 확인:
```
Type: MySQL/Aurora
Port: 3306
Source: EC2 보안 그룹 또는 0.0.0.0/0 (임시)
```

### 4. 환경 변수 설정 (.env 파일)
```bash
# RDS 연결 정보 (실제 비밀번호로 변경 필요)
DATABASE_URL=mysql://admin:실제비밀번호@ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com:3306/ursaviour

# AWS 리전
AWS_REGION=ap-southeast-2
S3_REGION=ap-southeast-2
```

### 5. 데이터베이스 연결 테스트
EC2에서 MySQL 클라이언트로 연결 테스트:
```bash
# MySQL 클라이언트 설치
sudo apt update
sudo apt install -y mysql-client

# RDS 연결 테스트
mysql -h ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com -u admin -p

# 연결 성공시 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS ursaviour;
USE ursaviour;
SHOW TABLES;
```

### 6. FastAPI에서 데이터베이스 초기화
```bash
# EC2에서 프로젝트 디렉토리에서 실행
cd /opt/ursaviour/backend
python init_db.py  # 테이블 생성
```

## 중요 참고사항

### 네트워킹
- RDS는 퍼블릭 액세스가 가능하므로 EC2에서 직접 연결 가능
- VPC가 같으므로 프라이빗 IP로 더 빠른 연결 가능

### 보안
- RDS 보안 그룹을 EC2 보안 그룹으로만 제한하는 것을 권장
- 프로덕션에서는 퍼블릭 액세스를 비활성화하는 것을 권장

### 비용
- 현재 RDS가 실행 중이므로 비용 발생 중
- t3.micro 인스턴스라면 Free Tier 범위 내

## 다음 단계
1. EC2 인스턴스를 ap-southeast-2 리전에 생성
2. 같은 VPC (vpc-09b863de1b93fc683) 사용
3. 보안 그룹 설정으로 RDS 연결 허용
4. 배포 후 데이터베이스 연결 확인