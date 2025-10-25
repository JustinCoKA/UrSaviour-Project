#!/bin/bash
# ETL Lambda 함수 수동 업데이트 스크립트

echo "📦 ETL Lambda 함수 업데이트 시작..."

# 1. Lambda 함수 코드 패키징
echo "1️⃣ Lambda 함수 패키징 중..."
zip -r etl_processor_with_logging.zip etl_processor_lambda.py

echo "2️⃣ Lambda 함수 업데이트 시도..."
aws lambda update-function-code \
    --function-name UrSaviour-ETL-Processor \
    --zip-file fileb://etl_processor_with_logging.zip \
    --region ap-southeast-2

if [ $? -eq 0 ]; then
    echo "✅ Lambda 함수 업데이트 성공!"
    
    echo "3️⃣ 환경 변수 업데이트 중..."
    aws lambda update-function-configuration \
        --function-name UrSaviour-ETL-Processor \
        --environment "Variables={DB_HOST=ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com,DB_USER=admin,DB_PASSWORD=Ursaviour2025,DB_NAME=ursaviourDb}" \
        --region ap-southeast-2
    
    if [ $? -eq 0 ]; then
        echo "✅ 환경 변수 업데이트 성공!"
        echo "🎯 ETL Lambda 함수 업데이트 완료!"
    else
        echo "⚠️ 환경 변수 업데이트 실패 (수동으로 AWS 콘솔에서 업데이트해주세요)"
    fi
else
    echo "❌ Lambda 함수 업데이트 실패"
    echo "💡 AWS 콘솔에서 수동으로 업데이트해주세요:"
    echo "   1. AWS Lambda 콘솔 접속"
    echo "   2. UrSaviour-ETL-Processor 함수 선택" 
    echo "   3. Code 탭에서 Upload from > .zip file 선택"
    echo "   4. etl_processor_with_logging.zip 업로드"
    echo "   5. Configuration > Environment variables에서 DB_NAME을 'ursaviourDb'로 변경"
fi

echo "📋 다음 단계:"
echo "   - AWS 콘솔에서 Lambda 함수 업데이트 완료 후"
echo "   - 새로운 테스트 파일을 S3에 업로드하여 ETL 로깅 테스트"