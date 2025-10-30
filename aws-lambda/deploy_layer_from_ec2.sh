#!/bin/bash

# Automated script to build Lambda layer on EC2
# This script runs on your LOCAL machine and connects to EC2

set -e

# Configuration
PEM_FILE="$HOME/Downloads/ur.pem"
EC2_USER="ec2-user"  # Default user for Amazon Linux 2
EC2_HOST=""  # You'll be prompted to enter this

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🚀 EC2 Lambda Layer Builder"
echo "=========================================="
echo ""

# Check if PEM file exists
if [ ! -f "$PEM_FILE" ]; then
    echo -e "${RED}❌ PEM file not found: $PEM_FILE${NC}"
    exit 1
fi

# Check PEM file permissions
PEM_PERMS=$(stat -f "%A" "$PEM_FILE" 2>/dev/null || stat -c "%a" "$PEM_FILE" 2>/dev/null)
if [ "$PEM_PERMS" != "400" ]; then
    echo -e "${YELLOW}⚠️  Fixing PEM file permissions...${NC}"
    chmod 400 "$PEM_FILE"
fi

# Get EC2 instance public IP/DNS
echo -e "${BLUE}Please enter your EC2 instance public IP or DNS:${NC}"
read -p "EC2 Host: " EC2_HOST

if [ -z "$EC2_HOST" ]; then
    echo -e "${RED}❌ EC2 host is required${NC}"
    exit 1
fi

# Test SSH connection
echo ""
echo -e "${BLUE}🔌 Testing SSH connection to $EC2_HOST...${NC}"
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" "echo '✅ SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}❌ Cannot connect to EC2 instance${NC}"
    echo "Please check:"
    echo "  - EC2 instance is running"
    echo "  - Security group allows SSH (port 22) from your IP"
    echo "  - Public IP/DNS is correct"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ SSH connection verified${NC}"
echo ""

# Upload build script to EC2
echo -e "${BLUE}📤 Uploading build script to EC2...${NC}"
scp -i "$PEM_FILE" build_layer_on_ec2.sh "$EC2_USER@$EC2_HOST:~/"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to upload build script${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build script uploaded${NC}"
echo ""

# Execute build script on EC2
echo -e "${BLUE}🔨 Building Lambda layer on EC2...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"
echo ""

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" "chmod +x build_layer_on_ec2.sh && ./build_layer_on_ec2.sh"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed on EC2${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo ""

# Download the layer
echo -e "${BLUE}📥 Downloading layer.zip from EC2...${NC}"
scp -i "$PEM_FILE" "$EC2_USER@$EC2_HOST:~/lambda-layer/layer.zip" ./layer.zip

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to download layer.zip${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Layer downloaded successfully!${NC}"
echo ""

# Show file info
LAYER_SIZE=$(du -h layer.zip | cut -f1)
echo "📊 Layer size: $LAYER_SIZE"
echo "📁 Location: $(pwd)/layer.zip"
echo ""

# Ask if user wants to upload to Lambda
echo -e "${YELLOW}Do you want to upload this layer to AWS Lambda now? (y/n)${NC}"
read -p "Upload to Lambda? " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}🚀 Publishing layer to AWS Lambda...${NC}"
    
    LAYER_VERSION=$(aws lambda publish-layer-version \
        --layer-name UrSaviour-ETL-Dependencies \
        --description "Linux-compatible layer built on EC2 - PyMuPDF, PyMySQL, Pillow" \
        --zip-file fileb://layer.zip \
        --compatible-runtimes python3.9 \
        --region ap-southeast-2 \
        --query 'Version' \
        --output text)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Layer published as version $LAYER_VERSION${NC}"
        echo ""
        
        # Update Lambda function
        echo -e "${BLUE}🔄 Updating Lambda function with new layer...${NC}"
        LAYER_ARN="arn:aws:lambda:ap-southeast-2:307946653709:layer:UrSaviour-ETL-Dependencies:$LAYER_VERSION"
        
        aws lambda update-function-configuration \
            --function-name UrSaviour-ETL-Processor \
            --layers "$LAYER_ARN" \
            --region ap-southeast-2 > /dev/null
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Lambda function updated successfully!${NC}"
            echo ""
            echo "🎯 Layer ARN: $LAYER_ARN"
        else
            echo -e "${RED}❌ Failed to update Lambda function${NC}"
        fi
    else
        echo -e "${RED}❌ Failed to publish layer${NC}"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ All done!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test PDF processing: ./test_s3_trigger.sh ../data/no.27week_special.pdf"
echo "2. Monitor execution: python3 monitor_etl_trigger.py"
echo "3. Clean up EC2 instance if no longer needed"
echo ""

# Ask if user wants to clean up EC2
echo -e "${YELLOW}Do you want to delete the build files from EC2? (y/n)${NC}"
read -p "Clean up EC2? " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🧹 Cleaning up EC2...${NC}"
    ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" "rm -rf lambda-layer build_layer_on_ec2.sh"
    echo -e "${GREEN}✅ EC2 cleaned up${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Process complete!${NC}"
