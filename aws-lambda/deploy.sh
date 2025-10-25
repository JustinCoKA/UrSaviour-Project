#!/bin/bash

# AWS Lambda Deployment Script
# Deploy ETL automation system to AWS.

set -e

echo "🚀 Starting UrSaviour ETL Lambda deployment..."

# Configuration variables
AWS_REGION=${AWS_REGION:-"ap-southeast-2"}  # Use same region as RDS
S3_BUCKET_NAME=${S3_BUCKET_NAME:-"ursaviour-data-group03-20250608"}  # Existing discount pamphlet bucket
LAMBDA_ROLE_NAME=${LAMBDA_ROLE_NAME:-"UrSaviourETLRole"}
ETL_TRIGGER_FUNCTION_NAME="UrSaviour-ETL-Trigger"
ETL_PROCESSOR_FUNCTION_NAME="UrSaviour-ETL-Processor"
LAMBDA_LAYER_NAME="UrSaviour-ETL-Dependencies"

# Color output functions
print_step() {
    echo "📋 Step $1: $2"
}

print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

# 1. Create IAM Role
print_step "1" "Creating IAM Role"

# Create Lambda execution role policy file
cat > lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
