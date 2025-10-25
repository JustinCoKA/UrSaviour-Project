# ETL Issue Analysis and Fixes

## 📊 Database Status Summary

**Date:** October 26, 2025

### Current State
- ✅ **Database Connection:** Working properly
- ✅ **Existing Data:** 10 records in storeOfferings (loaded Oct 19)
- ✅ **Tables:** All tables exist and properly structured
- ❌ **Recent ETL Jobs:** All failing since Oct 19

### Database Contents
- **Products:** 100 total
- **Stores:** 4 total (Aadarsh Deals, Austin Fresh, Justin Groceries, Mio Mart)
- **Store Offerings:** 10 records (last loaded Oct 19, 2025)

---

## 🔍 Issues Found

### Issue #1: CSV Field Mapping Mismatch ❌ FIXED
**Problem:**
- CSV files use snake_case field names (`product_name`, `store_name`, `final_price`)
- ETL processor expected camelCase names (`productName`, `storeName`, `price`)
- Result: 30 records extracted but 0 validated (all failed transformation)

**Error Message:**
```
"No valid data after transformation"
```

**Solution:**
Updated `map_csv_fields()` function in `etl_processor_lambda.py` to support both formats:
```python
field_mapping = {
    'store_name': 'storeName',      # snake_case
    'storeName': 'storeName',       # camelCase
    'product_name': 'productName',
    'productName': 'productName',
    'final_price': 'price',
    'price': 'price',
    'base_price': 'basePrice',
    'basePrice': 'basePrice',
    'discount_type': 'offerDetails',
    'offerDetails': 'offerDetails'
}
```

**Status:** ✅ Fixed and deployed to Lambda (Oct 25, 2025 23:56:53 UTC)

---

### Issue #2: PyMuPDF Not Available ❌ NEEDS FIX
**Problem:**
- Lambda function cannot process PDF files
- PyMuPDF library not installed in Lambda Layer

**Error Message:**
```
"PDF processing not available - PyMuPDF not installed"
```

**Files Affected:**
- `no.43week_special.pdf`
- `no.36week_special.pdf`

**Solution Required:**
1. Create Lambda Layer with PyMuPDF:
   ```bash
   mkdir -p python
   pip install PyMuPDF==1.23.8 -t python/
   zip -r pymupdf-layer.zip python/
   ```

2. Upload to AWS Lambda Layer:
   ```bash
   aws lambda publish-layer-version \
       --layer-name UrSaviour-PyMuPDF \
       --zip-file fileb://pymupdf-layer.zip \
       --compatible-runtimes python3.11 \
       --region ap-southeast-2
   ```

3. Attach layer to Lambda function

**Status:** ⚠️ Needs implementation

---

### Issue #3: S3 Permission Error (Resolved)
**Problem:**
- Earlier error: `403 Forbidden` when accessing S3 files
- Lambda function couldn't download files from S3

**Status:** ✅ Appears to be resolved (recent attempts succeeded)

---

## 🚀 Deployment History

### Lambda Function Updates
| Date | Time (UTC) | Update | Status |
|------|-----------|--------|--------|
| Oct 25 | 23:56:53 | CSV mapping fix deployed | ✅ Success |
| Oct 19 | 08:16:21 | Last successful ETL run | ✅ Success |

---

## 📝 Testing Results

### CSV Mapping Test
**File:** `test_csv_mapping.py`
**Results:**
- ✅ All 3 test records parsed correctly
- ✅ All fields mapped: storeName, productName, price, basePrice, offerDetails
- ✅ All records passed validation

**Sample Output:**
```
Raw CSV row: {'product_name': 'Rice', 'store_name': 'Mio Mart', 
              'base_price': '8.09', 'final_price': '7.28', 
              'discount_type': '10% OFF'}
Mapped: {'storeName': 'Mio Mart', 'productName': 'Rice', 
         'price': 7.28, 'basePrice': 8.09, 'offerDetails': '10% OFF'}
✅ Valid record
```

---

## 🔧 Next Steps

### Immediate Actions
1. ✅ **CSV Processing** - Fixed and deployed
2. ⚠️ **PDF Processing** - Needs Lambda Layer update
3. 📊 **Test** - Upload new CSV file to S3 to verify fix

### Recommended Actions
1. **Create PyMuPDF Lambda Layer**
   - Package PyMuPDF and dependencies
   - Upload as Lambda Layer
   - Attach to ETL Processor function

2. **Monitor ETL Jobs**
   - Check CloudWatch logs for next ETL run
   - Verify data loads successfully to database

3. **Set Up Alerts**
   - Configure SNS notifications for ETL failures
   - Monitor success/failure rates

---

## 📞 Database Connection Details

**Endpoint:** `ursaviour-db.cp4emoqegwfy.ap-southeast-2.rds.amazonaws.com`
**Database:** `ursaviourDb`
**Region:** ap-southeast-2

---

## 🔗 Useful Commands

### Check Database Status
```bash
python3 check_database_status.py
```

### Check ETL Error Logs
```bash
python3 check_etl_errors.py
```

### Update Lambda Function
```bash
./update_lambda.sh
```

### Test CSV Mapping
```bash
python3 test_csv_mapping.py
```

---

## 📈 Expected Behavior After Fix

When a new CSV file is uploaded to S3:
1. S3 trigger activates Lambda
2. Lambda downloads CSV from S3
3. Extracts data (e.g., 30 records)
4. Maps fields correctly (snake_case → camelCase)
5. Validates all records (should pass validation)
6. Deletes existing storeOfferings data
7. Inserts new data
8. Logs success to etlJobs table
9. Sends SNS notification

**Expected Result:** All 30 records loaded successfully ✅

---

Last Updated: October 26, 2025
