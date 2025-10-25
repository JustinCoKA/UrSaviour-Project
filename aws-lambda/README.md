# UrSaviour ETL Automation System

## Overview
A fully automated ETL pipeline that automatically detects discount pamphlets (PDF/CSV) uploaded to S3 and updates the database.

## System Architecture

```
📄 S3 Upload          ⚡ Lambda Trigger     🔄 ETL Processor      🗄️ Database Update
(PDF/CSV) ──────────→ (Event Detection) ──→ (Data Processing) ──→ (Store Offerings)
    │                        │                      │                   │
    └─ week_special.*         └─ File validation    └─ Extract          └─ TRUNCATE + INSERT
                                 Pattern matching      Transform
                                 Type detection        Load
```

## Key Features

### 🎯 Automatic Detection
- Real-time detection based on S3 bucket events
- File name pattern filtering (`week_special`, `discount`, `pamphlet`)
- Supported formats: PDF, CSV

### 🔄 ETL Pipeline
- **Extract**: PDF text extraction, CSV parsing
- **Transform**: Data normalization and validation
- **Load**: Complete deletion of existing data and insertion of new data

### 📊 Database Update
- Complete replacement of `storeOfferings` table
- Automatic addition of new products/stores
- Data consistency guarantee

### 🔔 Notification System
- Success/failure SNS notifications
- Detailed processing results
- CloudWatch logging

## Deployment Method

### 1. Environment Variable Setup
```bash
export AWS_REGION="ap-northeast-2"
export S3_BUCKET_NAME="ursaviour-discount-data"
export DB_HOST="your-rds-endpoint"
export DB_USER="your-db-user"
export DB_PASSWORD="your-db-password"
export DB_NAME="ursaviour"
export SNS_TOPIC_ARN="arn:aws:sns:region:account:topic" # Optional
```

### 2. Lambda Layer Creation
```bash
# Create dependencies layer
mkdir -p python
pip install -r requirements.txt -t python/
zip -r etl-dependencies-layer.zip python/
```

### 3. Lambda Function Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 4. S3 Event Configuration
```bash
# Configure S3 bucket notifications
aws s3api put-bucket-notification-configuration \
    --bucket ursaviour-discount-data \
    --notification-configuration file://s3-notification-config.json
```

## File Structure

```
aws-lambda/
├── etl_processor_lambda.py        # Main ETL processor
├── etl_trigger_lambda.py          # S3 event trigger
├── requirements.txt               # Python dependencies
├── deploy.sh                     # Deployment script
├── s3-notification-config.json   # S3 event configuration
└── test_*.py                     # Test scripts
```

## Usage

### File Upload
```bash
# Upload discount file to S3
aws s3 cp week_special_27.pdf s3://ursaviour-discount-data/discount/
aws s3 cp discount_data.csv s3://ursaviour-discount-data/discount/
```

### Monitoring
```bash
# Check CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/UrSaviour"

# Check database results
python test_db_connection.py
```

## Supported File Formats

### PDF Format
```
Product Name    Store           Original Price    Discount Type    Final Price
Donut          Justin Grocery   $5.87            Half Price       $2.94
Bread          Austin Fresh     $1.20            30% OFF          $0.84
```

### CSV Format
```csv
storeName,productName,price,basePrice,offerDetails
Justin Groceries,Donut,2.94,5.87,Half Price
Austin Fresh,Bread,0.84,1.20,30% OFF
```

## Database Schema

### storeOfferings Table
- `offeringId` (AUTO_INCREMENT)
- `productId` (FK to products)
- `storeId` (FK to stores)
- `price` (DECIMAL) - Discount price
- `basePrice` (DECIMAL) - Original price
- `offerDetails` (VARCHAR) - Discount description
- `loaded_at` (TIMESTAMP) - Load time

### ETL Logging Tables
- `etlJobs` - ETL job execution records
- `etlJobLogs` - Detailed execution logs

## Configuration

### S3 Event Trigger
- Event Type: `s3:ObjectCreated:*`
- Prefix Filter: `discount/`
- Suffix Filter: `.pdf`, `.csv`

### Lambda Functions
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 5 minutes
- **Layer**: Custom layer with PyMuPDF, PyMySQL

### Environment Variables
- `DB_HOST` - RDS endpoint
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name (default: ursaviourDb)
- `SNS_TOPIC_ARN` - SNS topic for notifications (optional)

## Error Handling

### Common Issues
1. **File format not supported** - Check file extension and content
2. **Database connection failed** - Verify RDS security group and credentials
3. **PDF parsing failed** - Check PDF text content and format
4. **Lambda timeout** - Increase timeout setting for large files

### Debugging
```bash
# Test database connection
python test_db_connection.py

# Check ETL logs
python check_etl_results.py

# Test logging functions
python test_etl_logging.py
```

## Security

### IAM Permissions
- S3: `s3:GetObject` on source bucket
- RDS: Database connection permissions
- Lambda: Function invocation permissions
- SNS: `sns:Publish` for notifications (optional)
- CloudWatch: Logging permissions

### Network Security
- RDS security group allows Lambda subnet access
- Lambda functions deployed in private subnet (recommended)
- VPC endpoints for AWS services (recommended)

## Monitoring and Alerting

### CloudWatch Metrics
- Lambda invocation count
- Lambda duration
- Lambda error rate
- Database connection success rate

### SNS Notifications
- ETL success with processing statistics
- ETL failure with error details
- Processing time and record counts

## Maintenance

### Regular Tasks
1. Monitor CloudWatch logs for errors
2. Check database storage usage
3. Review ETL processing times
4. Update Lambda layer dependencies as needed

### Performance Tuning
- Adjust Lambda memory allocation based on file sizes
- Optimize database queries for large datasets
- Consider batch processing for high-volume scenarios

## License
This project is licensed under the MIT License - see the LICENSE file for details.
