#!/usr/bin/env python3
"""
Test script for the grouped tables functionality
Demonstrates how to use the split table design with PageBasedMedicalReportData
"""

import sys
import logging
from datetime import datetime
from src.page_processor import PageProcessor
from src.data import PageBasedMedicalReportData

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_grouped_tables_structure():
    """Test the grouped tables structure without database connection"""
    print("🧪 Testing grouped tables structure...")
    
    # Create a mock report with some test data
    report = PageBasedMedicalReportData()
    
    # Create mock data for testing (you can replace this with real processed data)
    from src.data import Page0Data, Page1Data, Page3Data, Page8Data
    
    report.page_0 = Page0Data(
        reference_number="TEST123456",
        name_of_life_to_be_insured="John Smith"
    )
    
    report.page_1 = Page1Data(
        address="123 Test Street",
        suburb="Test Suburb", 
        state="NSW",
        postcode="2000",
        date_of_birth="1990-01-15",
        occupation="Software Engineer",
        licence_number="12345678",
        passport_number="A1234567",
        other_id="Test ID",
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
    
    report.page_8 = Page8Data(
        medical_attendants_reports_required="No",
        medical_attendants_reports_details="",
        likely_to_require_surgery="No", 
        likely_to_require_surgery_details="",
        unfavourable_history_personal_or_family="None noted",
        unfavourable_findings_medical_exam="None noted",
        examiner_name="Dr. Test Doctor",
        examiner_address="456 Medical Centre",
        examiner_suburb="Medical Suburb",
        examiner_state="NSW", 
        examiner_postcode="2001",
        examiner_phone="02-1234-5678",
        examiner_personal_qualifications="MBBS, FRACGP"
    )
    
    # Test the grouped tables function
    grouped_data = report.to_grouped_tables(
        policy_id="POL_TEST123",
        claim_id="CLM_TEST123", 
        process_date="2024-07-07",
        status="Processing"
    )
    
    print("\n📊 Grouped Tables Structure:")
    print("=" * 60)
    
    for table_name, table_data in grouped_data.items():
        print(f"\n🔹 {table_name} ({len(table_data)} fields):")
        for key, value in table_data.items():
            if value is not None and value != "":
                print(f"  • {key}: {value}")
    
    print(f"\n✅ Successfully created {len(grouped_data)} tables")
    return grouped_data

def test_database_import():
    """Test database import with grouped tables (requires MySQL connection)"""
    print("\n🗄️ Testing database import...")
    
    # Database connection parameters (update with your settings)
    db_config = {
        'host': 'localhost',
        'database': 'medical_reports_test',
        'username': 'root',
        'password': 'your_password',  # Update this
        'port': 3306
    }
    
    # Create a test report (same as above)
    report = PageBasedMedicalReportData()
    # ... (same mock data setup as above)
    
    try:
        # Test grouped database import
        results = report.to_mysql_db_grouped(**db_config)
        
        print(f"\n📤 Database Import Results:")
        for table_name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  • {table_name}: {status}")
            
    except Exception as e:
        print(f"⚠️ Database test skipped: {e}")
        print("💡 To test database functionality:")
        print("   1. Set up MySQL database")
        print("   2. Update db_config in this script")
        print("   3. Run the test again")

def process_actual_file_example():
    """Example of processing an actual file and using grouped tables"""
    print("\n📄 Example: Processing actual file...")
    
    # This is how you would process a real file
    file_path = "SAMPLE-TAL Medical Examiner's Confidential Report.pdf"
    
    try:
        # Initialize processor
        processor = PageProcessor()
        
        # Process the file
        print(f"Processing: {file_path}")
        result = processor.process_file(file_path, verbose=True)
        
        if isinstance(result, PageBasedMedicalReportData):
            print("✅ Successfully processed file")
            
            # Create grouped tables
            grouped_data = result.to_grouped_tables(
                policy_id="POL_REAL_001",
                claim_id="CLM_REAL_001"
            )
            
            print(f"📊 Created {len(grouped_data)} grouped tables from real data")
            
            # Show a summary of each table
            for table_name, table_data in grouped_data.items():
                non_empty_fields = sum(1 for v in table_data.values() if v not in [None, "", "No", "N"])
                print(f"  • {table_name}: {non_empty_fields} populated fields")
                
        else:
            print(f"❌ Error processing file: {result}")
            
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}")
        print("💡 Place a sample PDF in the project root to test with real data")
    except Exception as e:
        print(f"❌ Error: {e}")

def batch_import_example():
    """Example of batch importing multiple reports"""
    print("\n📦 Example: Batch Import...")
    
    # This would be a list of processed PageBasedMedicalReportData objects
    reports = []  # In practice, you'd have real data here
    
    if reports:
        # Database configuration
        db_config = {
            'host': 'localhost',
            'database': 'medical_reports_test', 
            'username': 'root',
            'password': 'your_password',
            'port': 3306
        }
        
        try:
            # Batch import to grouped tables
            stats = PageBasedMedicalReportData.batch_import_to_mysql_grouped(
                reports=reports,
                **db_config
            )
            
            print("📊 Batch Import Statistics:")
            for table_name, table_stats in stats.items():
                print(f"  • {table_name}:")
                print(f"    - Successful: {table_stats['successful']}")
                print(f"    - Failed: {table_stats['failed']}")
                print(f"    - Skipped: {table_stats['skipped']}")
                
        except Exception as e:
            print(f"❌ Batch import error: {e}")
    else:
        print("💡 No reports to process. In practice, you would:")
        print("   1. Process multiple PDF files")
        print("   2. Collect the PageBasedMedicalReportData results")
        print("   3. Use batch_import_to_mysql_grouped() for efficient import")

def main():
    """Main test function"""
    print("🚀 Testing Grouped Tables Functionality")
    print("=" * 60)
    
    # Test 1: Structure testing (always works)
    grouped_data = test_grouped_tables_structure()
    
    # Test 2: Database testing (requires MySQL setup)
    test_database_import()
    
    # Test 3: Real file processing example
    process_actual_file_example()
    
    # Test 4: Batch import example
    batch_import_example()
    
    print("\n🎉 Testing completed!")
    print("\n💡 Next Steps:")
    print("1. Set up your MySQL database")
    print("2. Update database credentials in the script")
    print("3. Process your PDF files using PageProcessor")
    print("4. Use the new grouped table methods for database import")
    
    print("\n📋 Available Methods:")
    print("• report.to_grouped_tables() - Split data into logical groups")
    print("• report.to_mysql_db_grouped() - Import to multiple tables")
    print("• PageBasedMedicalReportData.batch_import_to_mysql_grouped() - Batch import")

if __name__ == "__main__":
    main() 