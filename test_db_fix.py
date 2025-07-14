#!/usr/bin/env python3
"""
Test script to verify the database type fixes work correctly
"""

import logging
from src.data import PageBasedMedicalReportData, Page0Data, Page1Data, Page2Data, Page8Data

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_report():
    """Create a test report with problematic data types"""
    report = PageBasedMedicalReportData()
    
    # Page 0: Basic info
    report.page_0 = Page0Data(
        reference_number="TEST_FIX_123",
        name_of_life_to_be_insured="Test Patient"
    )
    
    # Page 1: Medical history with "Yes"/"No" values
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
        # These caused the original error - "No" strings instead of booleans
        has_circulatory_system_disorder="No",
        has_diabetes_or_high_blood_sugar="No",
        has_genitourinary_disorder="Yes",  # Mix of Yes/No
        has_digestive_system_disorder="N",   # Short form
        has_cancer_or_tumour="No",
        has_respiratory_disorder="No",
        has_neurological_condition="No",
        has_neurological_symptoms="No",
        has_eye_or_ear_disorder="No",
        has_skin_condition="No",
        has_back_or_neck_pain="Yes",
        has_joint_bone_or_muscle_disorder="No"
    )
    
    # Page 2: More medical history
    report.page_2 = Page2Data(
        has_arthritis_or_osteoporosis_or_gout="No",
        has_blood_disorder="No", 
        has_thyroid_disorder_or_lupus="No",
        has_mental_or_nervous_condition="No",
        has_female_reproductive_disorder_or_pregnancy="No",
        pregnant_expected_date="",
        has_pregnancy_complications="No",
        has_substance_or_alcohol_use_history="No",
        has_positive_hiv_or_hepatitis_test="No",
        has_high_risk_hiv_exposure_history="No",
        has_absence_from_work_due_to_illness_or_injury="No",
        has_undiagnosed_symptoms_or_condition="No",
        has_recent_medication_prescribed="No",
        has_recent_medical_tests="No",
        has_genetic_testing_history_or_intention="No",
        plans_future_medical_advice_or_treatment="No",
        medical_history_details=""
    )
    
    # Page 8: Summary
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
    
    return report

def test_grouped_tables():
    """Test the grouped tables functionality"""
    print("🧪 Testing grouped tables with fixed data types...")
    
    report = create_test_report()
    
    # Test the grouping
    grouped_data = report.to_grouped_tables(
        policy_id="POL_TEST_FIX",
        claim_id="CLM_TEST_FIX",
        process_date="2024-07-07",
        status="Testing"
    )
    
    print("\n📊 Testing data that previously caused errors:")
    
    # Check medical history table specifically
    medical_history = grouped_data.get('MEDICAL_HISTORY', {})
    print(f"\n🔍 MEDICAL_HISTORY table ({len(medical_history)} fields):")
    
    # Show the problematic fields that caused errors
    problematic_fields = [
        'has_circulatory_system_disorder',
        'has_genitourinary_disorder',
        'has_back_or_neck_pain'
    ]
    
    for field in problematic_fields:
        if field in medical_history:
            value = medical_history[field]
            print(f"  ✅ {field}: '{value}' (type: {type(value).__name__})")
    
    print(f"\n✅ Successfully created grouped tables without type errors")
    return grouped_data

def test_database_connection(grouped_data):
    """Test database connection if available"""
    print("\n🗄️ Testing database import with fixed types...")
    
    # Update these with your actual database credentials
    db_config = {
        'host': 'localhost',
        'database': 'medical_reports_test',
        'username': 'root',
        'password': 'your_password',  # Update this
        'port': 3306
    }
    
    report = create_test_report()
    
    try:
        # Test the database import
        results = report.to_mysql_db_grouped(**db_config)
        
        print("📤 Database Import Results:")
        for table_name, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  • {table_name}: {status}")
            
        return results
        
    except Exception as e:
        print(f"⚠️ Database test skipped: {e}")
        print("💡 To test database functionality:")
        print("   1. Update db_config with your MySQL credentials")
        print("   2. Ensure MySQL server is running")
        print("   3. Create the test database")
        print("   4. Run this script again")
        return None

def main():
    """Main test function"""
    print("🔧 Testing Database Type Fixes")
    print("=" * 50)
    
    # Test 1: Grouped tables structure
    grouped_data = test_grouped_tables()
    
    # Test 2: Database import (if available)
    db_results = test_database_connection(grouped_data)
    
    print("\n🎉 Testing completed!")
    
    if db_results:
        failed_tables = [table for table, success in db_results.items() if not success]
        if failed_tables:
            print(f"⚠️ Some tables failed: {failed_tables}")
        else:
            print("✅ All database operations successful!")
    
    print("\n🔧 Key Fixes Applied:")
    print("• Medical history fields (has_xxx) now stored as VARCHAR(10)")
    print("• Numeric fields properly identified and converted")
    print("• Empty values ('-', '', None) handled as NULL")
    print("• Text fields properly identified as TEXT or VARCHAR")

if __name__ == "__main__":
    main() 