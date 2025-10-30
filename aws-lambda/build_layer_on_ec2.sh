#!/bin/bash

# This script runs ON the EC2 instance to build the Lambda layer
# It should be uploaded to EC2 and executed there

set -e

echo "=========================================="
echo "Building Lambda Layer on Amazon Linux 2"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install development tools needed for PyMuPDF
echo "🔧 Installing build dependencies..."
sudo yum groupinstall -y "Development Tools"
sudo yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    gcc \
    gcc-c++ \
    make \
    freetype-devel \
    libjpeg-turbo-devel \
    openjpeg2-devel \
    jbig2dec-devel \
    mupdf-devel \
    zlib-devel

# Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip

# Create directory structure for Lambda layer
echo "📁 Creating layer directory structure..."
mkdir -p lambda-layer/python
cd lambda-layer

# Install Python packages
echo "🐍 Installing Python packages..."
echo "   - PyMySQL"
echo "   - PyMuPDF 1.23.8"
echo "   - Pillow"

pip3 install \
    pymysql \
    PyMuPDF==1.23.8 \
    pillow \
    --target python/ \
    --platform manylinux2014_x86_64 \
    --only-binary=:all: \
    --python-version 3.9

# If platform-specific install fails, try standard install
if [ $? -ne 0 ]; then
    echo "⚠️  Platform-specific install failed, trying standard install..."
    pip3 install \
        pymysql \
        PyMuPDF==1.23.8 \
        pillow \
        --target python/
fi

# Check if PyMuPDF was installed successfully
if [ -d "python/fitz" ] || [ -d "python/PyMuPDF" ]; then
    echo "✅ PyMuPDF installed successfully"
else
    echo "❌ PyMuPDF installation may have failed"
fi

# Remove unnecessary files to reduce layer size
echo "🧹 Cleaning up unnecessary files..."
find python -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find python -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find python -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find python -type f -name "*.pyc" -delete 2>/dev/null || true
find python -type f -name "*.pyo" -delete 2>/dev/null || true

# Show what was installed
echo ""
echo "📋 Installed packages:"
ls -lh python/

# Check for .so files (Linux shared libraries)
echo ""
echo "🔍 Checking for Linux shared libraries (.so files):"
find python -name "*.so" | head -20

# Create zip file
echo ""
echo "📦 Creating layer.zip..."
zip -r layer.zip python/ -q

# Show final size
LAYER_SIZE=$(du -h layer.zip | cut -f1)
echo ""
echo "✅ Layer built successfully!"
echo "📊 Layer size: $LAYER_SIZE"
echo "📁 Location: $(pwd)/layer.zip"
echo ""
echo "=========================================="
echo "Next steps:"
echo "1. Download layer.zip from EC2 to your local machine"
echo "2. Upload to AWS Lambda as new layer version"
echo "=========================================="
