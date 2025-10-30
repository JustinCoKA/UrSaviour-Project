#!/bin/bash
# Build Lambda Layer for Linux (Lambda runtime environment)

echo "🐳 Building Lambda Layer for Linux using Docker..."

cd /Users/juhwanlee/Desktop/GIT/UrSaviour-Project/aws-lambda

# Clean previous builds
rm -rf python_linux etl-dependencies-layer-linux.zip

# Build using Docker with Amazon Linux 2 (Lambda runtime)
docker run --rm -v $(pwd):/var/task \
  public.ecr.aws/lambda/python:3.9 \
  /bin/bash -c "
    pip install pymysql PyMuPDF==1.23.8 pillow -t /var/task/python_linux/ --no-cache-dir && \
    echo '✅ Dependencies installed for Linux'
  "

if [ $? -eq 0 ]; then
    echo "📦 Packaging layer..."
    cd python_linux
    zip -rq ../etl-dependencies-layer-linux.zip .
    cd ..
    
    echo "✅ Layer built successfully!"
    ls -lh etl-dependencies-layer-linux.zip
    
    echo ""
    echo "📤 Uploading to AWS Lambda..."
    aws lambda publish-layer-version \
        --layer-name UrSaviour-ETL-Dependencies \
        --description "PyMuPDF, PyMySQL, Pillow for ETL (Linux)" \
        --zip-file fileb://etl-dependencies-layer-linux.zip \
        --compatible-runtimes python3.9 python3.10 python3.11 \
        --region ap-southeast-2 \
        --query '[LayerVersionArn, Version]' \
        --output text
    
    NEW_LAYER_VERSION=$(aws lambda list-layer-versions --layer-name UrSaviour-ETL-Dependencies --region ap-southeast-2 --query 'LayerVersions[0].Version' --output text)
    
    echo ""
    echo "🔄 Updating Lambda function to use new layer..."
    aws lambda update-function-configuration \
        --function-name UrSaviour-ETL-Processor \
        --layers "arn:aws:lambda:ap-southeast-2:307946653709:layer:UrSaviour-ETL-Dependencies:${NEW_LAYER_VERSION}" \
        --region ap-southeast-2 \
        --query 'LastModified' \
        --output text
    
    echo ""
    echo "✅ Lambda layer updated successfully!"
    echo "   Version: ${NEW_LAYER_VERSION}"
else
    echo "❌ Failed to build layer"
    exit 1
fi
