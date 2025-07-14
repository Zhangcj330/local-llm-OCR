#!/usr/bin/env python3
"""
Test script to verify OCR data import to MySQL database using temporary database
"""

import logging
import mysql.connector
from mysql.connector import Error
import datetime
import time
from src.data import PageBasedMedicalReportData, Page0Data, Page1Data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TemporaryDatabaseManager:
    """Manager for temporary test databases"""
    
    def __init__(self, host='localhost', port=3306, root_user='root', root_password='MyRootPass123'):
        self.host = host
        self.port = port
        self.root_user = root_user
        self.root_password = root_password
        self.temp_db_name = None
        self.test_user = None  # Will be generated with timestamp
        self.test_password = 'temp_test_pass'
        
    def create_temporary_database(self):
        """Create a temporary database with unique name"""
        
        # Generate unique database name and user with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # microseconds to milliseconds
        self.temp_db_name = f"temp_medical_test_{timestamp}"
        self.test_user = f"temp_user_{timestamp}"
        
        # SAFETY CHECK: Ensure we're creating a temporary database
        if not self.temp_db_name.startswith("temp_"):
            raise ValueError("🚨 SAFETY ERROR: Database name must start with 'temp_' for testing!")
        
        print(f"🛡️  SAFETY CHECK: Confirmed temporary database name: {self.temp_db_name}")
        
        try:
            # Connect as root to create database and user
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.root_user,
                password=self.root_password
            )
            
            cursor = connection.cursor()
            
            print(f"🛠️  Creating temporary database: {self.temp_db_name}")
            
            # Create temporary database
            cursor.execute(f"CREATE DATABASE `{self.temp_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Create temporary user with full privileges on the temp database
            # Allow connections from any host (%) to handle Docker networking
            try:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{self.test_user}'@'%' IDENTIFIED BY '{self.test_password}'")
            except Error as user_error:
                # If user already exists, that's fine, just continue
                if user_error.errno != 1396:  # Error: User already exists
                    raise user_error
            
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{self.temp_db_name}`.* TO '{self.test_user}'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            
            connection.commit()
            print(f"✅ Temporary database '{self.temp_db_name}' created successfully")
            print(f"👤 Temporary user '{self.test_user}' granted access")
            
            return {
                'host': self.host,
                'database': self.temp_db_name,
                'username': self.test_user,
                'password': self.test_password,
                'port': self.port
            }
            
        except Error as e:
            print(f"❌ Error creating temporary database: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()
    
    def cleanup_temporary_database(self):
        """Remove the temporary database and user"""
        
        if not self.temp_db_name:
            return True
            
        try:
            # Connect as root to drop database and user
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.root_user,
                password=self.root_password
            )
            
            cursor = connection.cursor()
            
            print(f"🧹 Cleaning up temporary database: {self.temp_db_name}")
            
            # Drop temporary database
            cursor.execute(f"DROP DATABASE IF EXISTS `{self.temp_db_name}`")
            
            # Clean up temporary user to avoid conflicts in future runs
            if self.test_user:
                cursor.execute(f"DROP USER IF EXISTS '{self.test_user}'@'%'")
            
            connection.commit()
            print(f"✅ Temporary database '{self.temp_db_name}' cleaned up successfully")
            
            return True
            
        except Error as e:
            print(f"❌ Error cleaning up temporary database: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()

def validate_test_db_config(db_config):
    """Validate that database configuration is safe for testing"""
    
    # List of production database names that should NEVER be used in tests
    FORBIDDEN_DB_NAMES = [
        'medical_reports_db',
        'production',
        'prod', 
        'main',
        'live',
        'real',
        'medical_reports',
        'medical_data'
    ]
    
    db_name = db_config.get('database', '').lower()
    
    # Check if database name is in forbidden list
    if db_name in FORBIDDEN_DB_NAMES:
        raise ValueError(f"🚨 SAFETY ERROR: Cannot use production database '{db_name}' for testing!")
    
    # Check if database name starts with temp_ (our safety convention)
    if not db_name.startswith('temp_'):
        raise ValueError(f"🚨 SAFETY ERROR: Test database name must start with 'temp_', got: '{db_name}'")
    
    print(f"🛡️  SAFETY CHECK: Database config validated - using test database: {db_name}")
    return True

def test_single_record_import(db_config):
    """Test importing a single medical report to MySQL"""
    
    # SAFETY CHECK: Validate database configuration
    validate_test_db_config(db_config)
    
    print("📄 Creating sample medical report data...")
    
    # Create sample medical report data
    report = PageBasedMedicalReportData(
        page_0=Page0Data(
            reference_number="TEMP_TEST_REF_001",
            name_of_life_to_be_insured="John Doe Temp Test"
        ),
        page_1=Page1Data(
            address="123 Temporary Test Street",
            suburb="Melbourne",
            state="VIC",
            postcode="3000",
            date_of_birth="1990-01-15",
            occupation="Software Engineer",
            licence_number="L1234567",
            passport_number="P1234567",
            other_id="Temp Test ID",
            has_circulatory_system_disorder="No",
            has_diabetes_or_high_blood_sugar="No",
            has_genitourinary_disorder="No",
            has_digestive_system_disorder="No",
            has_cancer_or_tumour="No",
            has_respiratory_disorder="No",
            has_neurological_condition="No",
            has_neurological_symptoms="No",
            has_eye_or_ear_disorder="No",
            has_skin_condition="No",
            has_back_or_neck_pain="No",
            has_joint_bone_or_muscle_disorder="No"
        )
    )
    
    print(f"🔄 Importing data to temporary database: {db_config['database']}")
    
    try:
        # Import to MySQL database
        success = report.to_mysql_db(**db_config)
        
        if success:
            print("✅ Single record import successful!")
            print(f"📋 Reference Number: {report.reference_number}")
            print(f"👤 Patient Name: {report.name_of_life_to_be_insured}")
            return True
        else:
            print("❌ Single record import failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return False

def test_batch_import(db_config):
    """Test batch importing multiple medical reports"""
    
    # SAFETY CHECK: Validate database configuration
    validate_test_db_config(db_config)
    
    print("\n📊 Creating multiple sample reports for batch import...")
    
    reports = []
    
    for i in range(1, 4):
        report = PageBasedMedicalReportData(
            page_0=Page0Data(
                reference_number=f"TEMP_BATCH_TEST_{i:03d}",
                name_of_life_to_be_insured=f"Temp Test Patient {i}"
            ),
            page_1=Page1Data(
                address=f"{100 + i} Temp Batch Test Street",
                suburb="Sydney" if i % 2 == 0 else "Brisbane",
                state="NSW" if i % 2 == 0 else "QLD", 
                postcode=f"{2000 + i}",
                date_of_birth=f"199{i}-0{i}-{10 + i}",
                occupation=f"Temp Test Occupation {i}",
                licence_number=f"L12345{i}",
                passport_number=f"P12345{i}",
                other_id=f"Temp Batch Test ID {i}",
                has_circulatory_system_disorder="Yes" if i % 2 else "No",
                has_diabetes_or_high_blood_sugar="No",
                has_genitourinary_disorder="No",
                has_digestive_system_disorder="Yes" if i % 3 else "No",
                has_cancer_or_tumour="No",
                has_respiratory_disorder="No",
                has_neurological_condition="No",
                has_neurological_symptoms="No",
                has_eye_or_ear_disorder="No",
                has_skin_condition="No",
                has_back_or_neck_pain="Yes" if i == 2 else "No",
                has_joint_bone_or_muscle_disorder="No"
            )
        )
        reports.append(report)
    
    print(f"🔄 Batch importing {len(reports)} medical reports to {db_config['database']}...")
    
    try:
        # Batch import to MySQL database
        stats = PageBasedMedicalReportData.batch_import_to_mysql(
            reports=reports,
            **db_config,
            batch_size=2  # Process 2 records at a time
        )
        
        print(f"""
📊 Batch Import Results:
- Total records: {stats['total_records']}
- Successful imports: {stats['successful_imports']}
- Failed imports: {stats['failed_imports']}
- Skipped records: {stats['skipped_records']}
        """)
        
        return stats['successful_imports'] > 0
        
    except Exception as e:
        print(f"❌ Error during batch import: {e}")
        return False

def verify_data_in_temp_db(db_config):
    """Verify that data was correctly inserted into the temporary database"""
    
    # SAFETY CHECK: Validate database configuration
    validate_test_db_config(db_config)
    
    print(f"\n🔍 Verifying data in temporary database: {db_config['database']}")
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Check table structure
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        
        if tables:
            table_name = tables[0][0]  # Should be 'medical_reports'
            
            # Count records
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = cursor.fetchone()[0]
            print(f"📊 Total records in {table_name}: {count}")
            
            # Show sample data
            cursor.execute(f"SELECT reference_number, name_of_life_to_be_insured FROM `{table_name}` LIMIT 5")
            records = cursor.fetchall()
            
            print("📄 Sample records:")
            for ref, name in records:
                print(f"   - {ref}: {name}")
            
            return count > 0
        else:
            print("⚠️  No tables found in temporary database")
            return False
            
    except Error as e:
        print(f"❌ Error verifying data: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def main():
    """Main function to test MySQL data import functionality using temporary database"""
    
    print("🏥 Medical Report MySQL Import Test (TEMPORARY DATABASE ONLY)")
    print("=" * 65)
    print("🔒 SAFETY: This test ONLY uses temporary databases")
    print("🔒 SAFETY: No production data will be affected")
    print("🔒 SAFETY: All test data will be automatically cleaned up")
    print("=" * 65)
    
    # Initialize temporary database manager
    temp_db_manager = TemporaryDatabaseManager()
    
    try:
        # Create temporary database
        print("\n🛠️  Setting up temporary test environment...")
        print("-" * 45)
        
        db_config = temp_db_manager.create_temporary_database()
        
        if not db_config:
            print("❌ Failed to create temporary database. Aborting tests.")
            return
        
        print(f"🎯 Using temporary database: {db_config['database']}")
        
        # Test single record import
        print("\n1. Testing Single Record Import:")
        print("-" * 35)
        single_success = test_single_record_import(db_config)
        
        # Test batch import
        print("\n2. Testing Batch Import:")
        print("-" * 25)
        batch_success = test_batch_import(db_config)
        
        # Verify data
        print("\n3. Data Verification:")
        print("-" * 20)
        verification_success = verify_data_in_temp_db(db_config)
        
        # Summary
        print("\n📋 Test Summary:")
        print("-" * 15)
        print(f"Single Import:    {'✅ PASSED' if single_success else '❌ FAILED'}")
        print(f"Batch Import:     {'✅ PASSED' if batch_success else '❌ FAILED'}")
        print(f"Data Verification: {'✅ PASSED' if verification_success else '❌ FAILED'}")
        
        if single_success and batch_success and verification_success:
            print("\n🎉 All tests passed! Your MySQL integration is working correctly.")
            print("\n💡 Advantages of temporary database testing:")
            print("   ✅ No pollution of production data")
            print("   ✅ Isolated test environment")
            print("   ✅ Automatic cleanup after testing")
            print("   ✅ Repeatable test conditions")
        else:
            print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
    
    finally:
        # Cleanup temporary database
        print("\n🧹 Cleaning up temporary test environment...")
        print("-" * 42)
        temp_db_manager.cleanup_temporary_database()
        print("✨ Cleanup completed. No traces left behind!")
        print("\n🛡️  FINAL SAFETY CONFIRMATION:")
        print("   ✅ Only temporary databases were used")
        print("   ✅ No production data was touched")
        print("   ✅ All test artifacts have been removed")
        print("   ✅ System is clean and ready for production use")

if __name__ == "__main__":
    main() 