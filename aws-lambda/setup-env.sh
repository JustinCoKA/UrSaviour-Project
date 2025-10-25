#!/bin/bash

# ETL Lambda Environment Variables Setup Script
# Update with actual database information

echo "🔧 ETL Lambda Environment Variables Setup"
echo ""
echo "Please enter or verify the following information:"
echo ""

# Existing S3 bucket already verified
export S3_BUCKET_NAME="ursaviour-data-group03-20250608"
echo "✅ S3 Bucket: $S3_BUCKET_NAME"

# Region configuration
export AWS_REGION="ap-northeast-2"
echo "✅ AWS Region: $AWS_REGION"

echo ""
echo "⚠️  The following database information needs to be configured:"
echo ""

# Database information (update with actual values)
echo "DB_HOST: Database host address"
echo "DB_USER: Database username"
echo "DB_PASSWORD: Database password"
echo "DB_NAME: Database name"

echo ""
echo "📝 Configuration steps:"
echo "1. Check current database connection information"
echo "2. Set as environment variables:"
echo ""
echo "   export DB_HOST='your-database-host'"
echo "   export DB_USER='your-database-user'"
echo "   export DB_PASSWORD='your-database-password'"
echo "   export DB_NAME='your-database-name'"
echo ""
echo "3. (Optional) SNS notification setup:"
echo "   export SNS_TOPIC_ARN='arn:aws:sns:region:account:topic'"
echo ""

# Display current backend configuration
echo "💡 Current backend default settings:"
echo "   DB_HOST: db (when using docker-compose)"
echo "   DB_PORT: 3306"
echo "   DB_USER: ursaviour"
echo "   DB_NAME: ursaviour"
echo ""
echo "For production environment, please change to actual"
echo "RDS endpoint or actual database address."