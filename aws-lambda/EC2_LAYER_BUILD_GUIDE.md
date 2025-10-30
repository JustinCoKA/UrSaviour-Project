# Building Lambda Layer on EC2 - Complete Guide

**Date:** October 26, 2025  
**Purpose:** Build Linux-compatible Lambda layer with PyMuPDF on Amazon Linux 2

---

## 🎯 Why EC2?

Lambda runs on Amazon Linux 2. PyMuPDF needs to be compiled with Linux-compatible binaries (`.so` files). Building on EC2 ensures 100% compatibility.

---

## 📋 Prerequisites

✅ AWS CLI configured with credentials  
✅ EC2 key pair file: `/Users/juhwanlee/Downloads/ur.pem`  
✅ Access to AWS EC2 console  

---

## 🚀 Option 1: Automated Deployment (Recommended)

### Single Command Solution

```bash
cd /Users/juhwanlee/Desktop/GIT/UrSaviour-Project/aws-lambda
chmod +x deploy_layer_from_ec2.sh
./deploy_layer_from_ec2.sh
```

**What it does:**
1. ✅ Verifies ur.pem permissions
2. ✅ Tests SSH connection to EC2
3. ✅ Uploads build script to EC2
4. ✅ Builds layer on EC2 (5-10 minutes)
5. ✅ Downloads layer.zip to local machine
6. ✅ Publishes to Lambda (optional)
7. ✅ Updates Lambda function (optional)
8. ✅ Cleans up EC2 files (optional)

**You'll be prompted for:**
- EC2 instance public IP or DNS name

---

## 🛠️ Option 2: Manual Step-by-Step

### Step 1: Launch EC2 Instance

#### Via AWS Console:
1. Go to EC2 Dashboard
2. Click **Launch Instance**
3. Configure:
   ```
   Name: lambda-layer-builder
   AMI: Amazon Linux 2 AMI (HVM)
   Instance type: t2.micro (free tier eligible)
   Key pair: Select your existing key (ur)
   Security group: Allow SSH (port 22) from your IP
   Storage: 8 GB (default)
   ```
4. Click **Launch Instance**
5. Wait 1-2 minutes for instance to start

#### Via AWS CLI:
```bash
# Find latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text \
  --region ap-southeast-2)

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name ur \
  --security-group-ids sg-xxxxxxxx \
  --query 'Instances[0].InstanceId' \
  --output text \
  --region ap-southeast-2)

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region ap-southeast-2

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text \
  --region ap-southeast-2)

echo "Public IP: $PUBLIC_IP"
```

### Step 2: Connect to EC2

```bash
# Fix PEM permissions (if needed)
chmod 400 ~/Downloads/ur.pem

# Connect to EC2
ssh -i ~/Downloads/ur.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

**Troubleshooting:**
- If connection times out: Check security group allows SSH from your IP
- If "Permission denied": Verify PEM file permissions are 400
- If "Host key verification": Type `yes` to continue

### Step 3: Upload Build Script

**From your local machine:**
```bash
cd /Users/juhwanlee/Desktop/GIT/UrSaviour-Project/aws-lambda

scp -i ~/Downloads/ur.pem \
  build_layer_on_ec2.sh \
  ec2-user@YOUR_EC2_PUBLIC_IP:~/
```

### Step 4: Build Layer on EC2

**On EC2 instance:**
```bash
chmod +x build_layer_on_ec2.sh
./build_layer_on_ec2.sh
```

**Expected output:**
```
==========================================
Building Lambda Layer on Amazon Linux 2
==========================================
📦 Updating system packages...
🔧 Installing build dependencies...
⬆️  Upgrading pip...
📁 Creating layer directory structure...
🐍 Installing Python packages...
✅ PyMuPDF installed successfully
🧹 Cleaning up unnecessary files...
📦 Creating layer.zip...
✅ Layer built successfully!
📊 Layer size: 35M
```

**Build time:** 5-10 minutes

### Step 5: Download Layer

**From your local machine:**
```bash
cd /Users/juhwanlee/Desktop/GIT/UrSaviour-Project/aws-lambda

scp -i ~/Downloads/ur.pem \
  ec2-user@YOUR_EC2_PUBLIC_IP:~/lambda-layer/layer.zip \
  ./layer.zip
```

### Step 6: Upload to Lambda

```bash
# Publish new layer version
aws lambda publish-layer-version \
  --layer-name UrSaviour-ETL-Dependencies \
  --description "Linux-compatible layer - PyMuPDF, PyMySQL, Pillow" \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.9 \
  --region ap-southeast-2
```

**Note the version number from output!**

### Step 7: Update Lambda Function

```bash
# Replace VERSION with the version number from step 6
LAYER_VERSION=14  # Example: your new version number

aws lambda update-function-configuration \
  --function-name UrSaviour-ETL-Processor \
  --layers "arn:aws:lambda:ap-southeast-2:307946653709:layer:UrSaviour-ETL-Dependencies:$LAYER_VERSION" \
  --region ap-southeast-2
```

### Step 8: Test PDF Processing

```bash
# Upload test PDF
./test_s3_trigger.sh ../data/no.27week_special.pdf

# Monitor execution
python3 monitor_etl_trigger.py
```

**Expected result:**
```
✅ ETL Job completed successfully
✅ Records processed: 30+
✅ PyMuPDF working on Lambda
```

### Step 9: Clean Up EC2

**Terminate instance when done:**
```bash
# Via AWS CLI
aws ec2 terminate-instances \
  --instance-ids $INSTANCE_ID \
  --region ap-southeast-2

# Or via AWS Console:
# EC2 Dashboard → Instances → Select instance → Instance State → Terminate
```

**Important:** 
- Terminated instances cannot be recovered
- Wait to terminate until you've confirmed PDF processing works
- You can stop (not terminate) the instance to pause billing but keep it for future builds

---

## 📝 Quick Reference Commands

### EC2 Connection
```bash
# SSH to EC2
ssh -i ~/Downloads/ur.pem ec2-user@YOUR_EC2_PUBLIC_IP

# Upload file to EC2
scp -i ~/Downloads/ur.pem LOCAL_FILE ec2-user@YOUR_EC2_PUBLIC_IP:~/

# Download file from EC2
scp -i ~/Downloads/ur.pem ec2-user@YOUR_EC2_PUBLIC_IP:~/REMOTE_FILE ./
```

### Check EC2 Status
```bash
# List your running instances
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name]' \
  --output table \
  --region ap-southeast-2
```

### Lambda Layer Management
```bash
# List layer versions
aws lambda list-layer-versions \
  --layer-name UrSaviour-ETL-Dependencies \
  --region ap-southeast-2

# Get current Lambda configuration
aws lambda get-function-configuration \
  --function-name UrSaviour-ETL-Processor \
  --region ap-southeast-2 \
  --query 'Layers'
```

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Layer version incremented
- [ ] Lambda function shows new layer
- [ ] Upload test CSV → ✅ Success
- [ ] Upload test PDF → ✅ Success
- [ ] Check database → Records inserted
- [ ] Review CloudWatch logs → No errors
- [ ] ETL job status → Completed

---

## 🐛 Troubleshooting

### SSH Connection Issues

**Problem:** `Connection timed out`
```bash
# Solution: Check security group
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.from-port,Values=22" \
  --region ap-southeast-2
```

**Problem:** `Permission denied (publickey)`
```bash
# Solution: Fix PEM permissions
chmod 400 ~/Downloads/ur.pem
```

### Build Issues

**Problem:** Build script fails on EC2
```bash
# Check logs on EC2
tail -f /var/log/cloud-init-output.log

# Try manual package install
sudo yum install -y python3-devel gcc gcc-c++
```

**Problem:** PyMuPDF installation fails
```bash
# Try without platform-specific flags
pip3 install PyMuPDF==1.23.8 --target python/
```

### Lambda Issues

**Problem:** Lambda still can't import PyMuPDF
```bash
# Verify layer is attached
aws lambda get-function-configuration \
  --function-name UrSaviour-ETL-Processor \
  --region ap-southeast-2 \
  --query 'Layers'

# Check layer contents
unzip -l layer.zip | grep -i pymupdf
```

---

## 💰 Cost Estimate

| Resource | Cost |
|----------|------|
| EC2 t2.micro | ~$0.01 for 1 hour |
| Data transfer | Negligible |
| Lambda layer storage | Free (< 75 GB) |
| **Total** | **< $0.05** |

**Tip:** Terminate EC2 immediately after downloading layer.zip

---

## 📚 Additional Resources

- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [Lambda Layers Documentation](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)

---

## ✅ Success Criteria

You'll know it worked when:

1. ✅ `layer.zip` downloads successfully (~35-40 MB)
2. ✅ Layer publishes to Lambda without errors
3. ✅ Lambda function updates with new layer version
4. ✅ Test PDF upload triggers successful ETL
5. ✅ Database shows new records from PDF
6. ✅ CloudWatch logs show "PyMuPDF" imported successfully

---

**Last Updated:** October 26, 2025  
**Status:** Ready for deployment
