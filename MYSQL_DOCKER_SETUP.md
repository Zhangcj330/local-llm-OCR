# MySQL Docker Setup Guide for OCR System

## 🎉 Current Status: FULLY OPERATIONAL

Your MySQL Docker container is successfully running and integrated with the OCR system!

## 📊 System Overview

### Container Details
- **Container Name**: `mysql8`
- **MySQL Version**: 8.0.42
- **Port Mapping**: `3306:3306` (localhost:3306 → container:3306)
- **Root Password**: `MyRootPass123`

### Database Configuration
- **Database Name**: `medical_reports_db`
- **User**: `ocr_user`
- **Password**: `ocr_password`
- **Character Set**: `utf8mb4`
- **Collation**: `utf8mb4_unicode_ci`

### Table Status
- **Table Name**: `medical_reports`
- **Total Columns**: 26 columns (auto-generated from data model)
- **Primary Key**: `reference_number`
- **Records Imported**: 4 test records ✅

## 🔧 Connection Configuration

### For Your Applications
```python
db_config = {
    'host': 'localhost',
    'database': 'medical_reports_db',
    'username': 'ocr_user',
    'password': 'ocr_password',
    'port': 3306
}
```

### Environment Variables (Recommended)
Create a `.env` file:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medical_reports_db
DB_USER=ocr_user
DB_PASSWORD=ocr_password
```

## 🛠️ Docker Commands

### Check Container Status
```bash
docker ps -a | grep mysql
```

### View Container Logs
```bash
docker logs mysql8
```

### Stop Container
```bash
docker stop mysql8
```

### Start Container
```bash
docker start mysql8
```

### Remove Container (⚠️ This will delete all data)
```bash
docker stop mysql8
docker rm mysql8
```

### Access MySQL Shell
```bash
# Using root user
docker exec -it mysql8 mysql -u root -p
# Password: MyRootPass123

# Using ocr_user
docker exec -it mysql8 mysql -u ocr_user -p
# Password: ocr_password
```

## 🧪 Test Scripts

You have several test scripts available:

### 1. Connection Test
```bash
python test_mysql_connection.py
```
- Tests root connection
- Creates database and user
- Verifies OCR user permissions

### 2. Data Import Test
```bash
python test_data_import.py
```
- Tests single record import
- Tests batch import functionality
- Verifies all import features

### 3. Database Verification
```bash
python verify_database.py
```
- Shows table structure
- Displays recent records
- Counts total records

## 📈 Production Recommendations

### 1. Data Persistence
Your current setup uses Docker's default storage. For production, consider:

```bash
# Create named volume for data persistence
docker volume create mysql_ocr_data

# Run container with persistent volume
docker run -d \
  --name mysql8 \
  -v mysql_ocr_data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=MyRootPass123 \
  -e MYSQL_DATABASE=medical_reports_db \
  -e MYSQL_USER=ocr_user \
  -e MYSQL_PASSWORD=ocr_password \
  -p 3306:3306 \
  mysql:8.0
```

### 2. Security Improvements
- Use stronger passwords
- Limit network access
- Regular backups
- SSL/TLS encryption

### 3. Performance Tuning
```bash
# Add MySQL configuration
docker run -d \
  --name mysql8 \
  -v mysql_ocr_data:/var/lib/mysql \
  -v ./my.cnf:/etc/mysql/conf.d/my.cnf \
  -e MYSQL_ROOT_PASSWORD=strong_password \
  -p 3306:3306 \
  mysql:8.0
```

## 🔄 Using with OCR System

### Single Record Import
```python
from src.data import PageBasedMedicalReportData, Page0Data

# Create your OCR-extracted data
report = PageBasedMedicalReportData(
    page_0=Page0Data(
        reference_number="YOUR_REF",
        name_of_life_to_be_insured="Patient Name"
    )
    # ... add more pages as needed
)

# Import to MySQL
success = report.to_mysql_db(
    host='localhost',
    database='medical_reports_db',
    username='ocr_user',
    password='ocr_password',
    port=3306
)
```

### Batch Import
```python
# For multiple reports
stats = PageBasedMedicalReportData.batch_import_to_mysql(
    reports=report_list,
    host='localhost',
    database='medical_reports_db',
    username='ocr_user',
    password='ocr_password',
    port=3306,
    batch_size=50
)
```

## 🚨 Troubleshooting

### Connection Issues
1. **Check if container is running**: `docker ps`
2. **Check port mapping**: `docker port mysql8`
3. **Verify credentials**: Use test scripts
4. **Check logs**: `docker logs mysql8`

### Permission Issues
```sql
-- Connect as root and fix permissions
GRANT ALL PRIVILEGES ON medical_reports_db.* TO 'ocr_user'@'%';
FLUSH PRIVILEGES;
```

### Data Issues
```sql
-- Check table structure
DESCRIBE medical_reports;

-- Check recent records
SELECT * FROM medical_reports ORDER BY created_at DESC LIMIT 5;
```

## ✅ Verification Checklist

- [x] Docker container running
- [x] MySQL server accessible
- [x] Database `medical_reports_db` created
- [x] User `ocr_user` created with proper permissions
- [x] Table `medical_reports` auto-created
- [x] Single record import working
- [x] Batch import working
- [x] Data persistence verified

## 📞 Next Steps

1. **Integrate with your OCR pipeline**
2. **Set up regular backups**
3. **Configure monitoring**
4. **Optimize for your data volume**
5. **Consider production deployment**

Your MySQL integration is ready for production use! 🚀 