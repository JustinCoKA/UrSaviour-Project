#!/bin/bash
# ETL Lambda function manual update script

echo "📦 Starting ETL Lambda function update..."

# 1. Package Lambda function code
echo "1️⃣ Packaging Lambda function..."
zip -r etl_processor_with_logging.zip etl_processor_lambda.py

echo "2️⃣ Attempting Lambda function update..."
aws lambda update-function-code \
    --function-name UrSaviour-ETL-Processor \
    --zip-file fileb://etl_processor_with_logging.zip \
    --region ap-southeast-2

if [ $? -eq 0 ]; then
    echo "✅ Lambda function update successful!"
    
    echo "3️⃣ Updating environment variables..."
    aws lambda update-function-configuration \
        --function-name UrSaviour-ETL-Processor \
        --environment "Variables={DB_HOST=ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com,DB_USER=admin,DB_PASSWORD=Ursaviour2025,DB_NAME=ursaviourDb}" \
        --region ap-southeast-2
    
    if [ $? -eq 0 ]; then
        echo "✅ Environment variables updated successfully!"
        echo "🎯 ETL Lambda function update complete!"
    else
        echo "⚠️ Environment variables update failed (please update manually in AWS console)"
    fi
else
    echo "❌ Lambda function update failed"
    echo "💡 Please update manually in AWS console:"
    echo "   1. Access AWS Lambda console"
    echo "   2. Select UrSaviour-ETL-Processor function" 
    echo "   3. In Code tab, select Upload from > .zip file"
    echo "   4. Upload etl_processor_with_logging.zip"
    echo "   5. In Configuration > Environment variables, change DB_NAME to 'ursaviourDb'"
fi

echo "📋 Next steps:"
echo "   - After Lambda function update completes in AWS console"
echo "   - Upload a new test file to S3 to test ETL logging"