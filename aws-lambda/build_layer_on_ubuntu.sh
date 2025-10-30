#!/bin/bash

# Build Lambda Layer on Ubuntu EC2 Instance
# This script is optimized for Ubuntu (not Amazon Linux 2)

set -e

echo "=========================================="
echo "Building Lambda Layer on Ubuntu"
echo "=========================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y

# Install Python and development tools
echo "🔧 Installing Python and build dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    libjbig2dec0-dev \
    zlib1g-dev \
    libmupdf-dev

# Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip

# Create directory structure for Lambda layer
echo "📁 Creating layer directory structure..."
mkdir -p lambda-layer/python
cd lambda-layer

# Install Python packages
echo "🐍 Installing Python packages for Lambda..."
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
echo "1. Download layer.zip to your Mac"
echo "2. Upload to AWS Lambda"
echo "=========================================="
cd /opt/ursaviour/aws-lambda