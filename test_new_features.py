#!/usr/bin/env python3
"""
Test script for new PageProcessor features:
1. Single page processing from file
2. CSV export functionality for PageBasedMedicalReportData
"""

import json
import pandas as pd
from pathlib import Path
from src.page_processor import PageProcessor
from src.data import PageBasedMedicalReportData

def test_single_page_processing():
    """Test the new process_single_page_from_file function"""
    
    print("🔍 Testing Single Page Processing Function")
    print("=" * 50)
    
    # Initialize the processor
    processor = PageProcessor(
        model_name="llama3.2-vision:latest",
        base_url="http://localhost:11434",
        config_path="src/config.json"
    )
    
    sample_file = "SAMPLE-TAL Medical Examiner's Confidential Report.pdf"
    
    if not Path(sample_file).exists():
        print(f"⚠️  Sample file not found: {sample_file}")
        return False
    
    try:
        # Test processing different pages
        pages_to_test = [0, 1, 3]  # Test key pages
        
        for page_num in pages_to_test:
            print(f"\n📄 Testing page {page_num}...")
            
            # Process single page
            page_data = processor.process_single_page_from_file(
                sample_file, 
                page_num, 
                verbose=True
            )
            
            print(f"✅ Page {page_num} processed successfully!")
            print(f"📋 Data type: {type(page_data).__name__}")
            
            # Show sample data based on page type
            if page_num == 0:
                print(f"   Reference: {page_data.reference_number}")
                print(f"   Name: {page_data.name_of_life_to_be_insured}")
            elif page_num == 1:
                print(f"   Address: {page_data.address}")
                print(f"   DOB: {page_data.date_of_birth}")
                print(f"   Occupation: {page_data.occupation}")
            elif page_num == 3:
                print(f"   Height: {page_data.height_cm} cm")
                print(f"   Weight: {page_data.weight_kg} kg")
                print(f"   Ever smoked: {page_data.ever_smoked}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in single page processing: {str(e)}")
        return False

def test_csv_export():
    """Test the new CSV export functionality"""
    
    print("\n📊 Testing CSV Export Functionality")
    print("=" * 50)
    
    # Create sample data
    sample_data = PageBasedMedicalReportData()
    
    # Fill some sample data for Page 0
    sample_data.page_0.reference_number = "TEST-001"
    sample_data.page_0.name_of_life_to_be_insured = "John Doe"
    
    # Fill some sample data for Page 1
    sample_data.page_1.address = "123 Main St"
    sample_data.page_1.suburb = "Anytown"
    sample_data.page_1.state = "NSW"
    sample_data.page_1.postcode = "2000"
    sample_data.page_1.date_of_birth = "01/01/1990"
    sample_data.page_1.occupation = "Software Engineer"
    sample_data.page_1.signature_of_life_to_be_insured_date = "01/12/2024"
    sample_data.page_1.witness_signature_date = "01/12/2024"
    sample_data.page_1.licence_number = "12345678"
    sample_data.page_1.passport_number = "A1234567"
    
    # Medical history questions (now boolean fields)
    sample_data.page_1.has_circulatory_system_disorder = False
    sample_data.page_1.has_diabetes_or_high_blood_sugar = False
    sample_data.page_1.has_respiratory_disorder = True  # Has asthma
    sample_data.page_1.has_cancer_or_tumour = False
    sample_data.page_1.has_genitourinary_disorder = False
    sample_data.page_1.has_digestive_system_disorder = False
    sample_data.page_1.has_neurological_condition = False
    sample_data.page_1.has_neurological_symptoms = False
    sample_data.page_1.has_eye_or_ear_disorder = False
    sample_data.page_1.has_skin_condition = False
    sample_data.page_1.has_back_or_neck_pain = False
    sample_data.page_1.has_joint_bone_or_muscle_disorder = False
    
    # Page 2 medical history questions
    sample_data.page_2.has_arthritis_or_osteoporosis_or_gout = False
    sample_data.page_2.has_blood_disorder = False
    sample_data.page_2.has_thyroid_disorder_or_lupus = False
    sample_data.page_2.has_mental_or_nervous_condition = False
    sample_data.page_2.has_female_reproductive_disorder_or_pregnancy = False
    sample_data.page_2.has_pregnancy_or_childbirth_complications = False
    sample_data.page_2.has_substance_or_alcohol_use_history = False
    sample_data.page_2.has_positive_hiv_or_hepatitis_test = False
    sample_data.page_2.has_high_risk_hiv_exposure_history = False
    sample_data.page_2.has_absence_from_work_due_to_illness_or_injury = False
    sample_data.page_2.has_undiagnosed_symptoms_or_condition = False
    sample_data.page_2.has_recent_medication_prescribed = False
    sample_data.page_2.has_recent_medical_tests = False
    sample_data.page_2.has_genetic_testing_history_or_intention = False
    sample_data.page_2.plans_future_medical_advice_or_treatment = False
    
    # Page 3 data
    sample_data.page_3.height_cm = 180
    sample_data.page_3.weight_kg = 75
    sample_data.page_3.ever_smoked = False
    sample_data.page_3.known_to_examiner = False
    sample_data.page_3.previously_attended_examiner = False
    sample_data.page_3.unusual_build_or_behavior = "None noted"
    sample_data.page_3.signs_of_tobacco_alcohol_or_drugs = "None"
    sample_data.page_3.chest_full_inspiration_cm = 100
    sample_data.page_3.chest_full_expiration_cm = 95
    sample_data.page_3.waist_circumference_cm = 85
    sample_data.page_3.hips_circumference_cm = 90
    
    # Family history conditions (now a list of FamilyHistoryCondition objects)
    from src.data import FamilyHistoryCondition, FAMILY_HISTORY_QUESTIONS
    
    family_conditions = []
    # Add some sample family history conditions
    family_conditions.append(FamilyHistoryCondition.from_config(FAMILY_HISTORY_QUESTIONS[5], "Yes"))  # Diabetes
    family_conditions.append(FamilyHistoryCondition.from_config(FAMILY_HISTORY_QUESTIONS[0], "No"))   # Heart disease
    sample_data.page_3.family_history_conditions = family_conditions
    
    try:
        # Test single row CSV export
        print("🔄 Converting to CSV record...")
        csv_record = sample_data.to_csv_records()
        
        print(f"✅ CSV record created with {len(csv_record)} fields")
        print("\n📋 Sample fields:")
        sample_fields = [
            "reference_number", "name_of_life_to_be_insured", 
            "address", "date_of_birth", "height_cm", "weight_kg",
            "has_respiratory_disorder", "has_circulatory_system_disorder"
        ]
        
        for field in sample_fields:
            if field in csv_record:
                print(f"   {field}: {csv_record[field]}")
        
        # Test list export (for pandas compatibility)
        print("\n🔄 Converting to CSV records list...")
        csv_records_list = sample_data.to_csv_records_list()
        
        print(f"✅ CSV records list created with {len(csv_records_list)} record(s)")
        
        # Test with pandas
        print("\n📊 Testing with pandas DataFrame...")
        df = pd.DataFrame(csv_records_list)
        
        print(f"✅ DataFrame created: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"📋 Column names: {list(df.columns)[:10]}...")  # Show first 10 columns
        
        # Save to CSV file
        output_file = "sample_page_based_export.csv"
        df.to_csv(output_file, index=False)
        print(f"💾 CSV saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in CSV export: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """Test complete workflow: single page processing + CSV export"""
    
    print("\n🔄 Testing Complete Workflow")
    print("=" * 50)
    
    processor = PageProcessor(
        model_name="llama3.2-vision:latest",
        base_url="http://localhost:11434",
        config_path="src/config.json"
    )
    
    sample_file = "SAMPLE-TAL Medical Examiner's Confidential Report.pdf"
    
    if not Path(sample_file).exists():
        print(f"⚠️  Sample file not found: {sample_file}")
        return False
    
    try:
        # Process only the first page (fastest test)
        print("📄 Processing page 0 for quick test...")
        page_0_data = processor.process_single_page_from_file(sample_file, 0, verbose=True)
        
        # Create a partial PageBasedMedicalReportData object
        result = PageBasedMedicalReportData()
        result.page_0 = page_0_data
        
        # Export to CSV
        print("\n📊 Exporting to CSV...")
        csv_record = result.to_csv_records()
        
        # Save to file
        df = pd.DataFrame([csv_record])
        output_file = "single_page_test_export.csv"
        df.to_csv(output_file, index=False)
        
        print(f"✅ Workflow completed successfully!")
        print(f"📋 Processed: Page 0")
        print(f"📊 Exported: {len(csv_record)} fields")
        print(f"💾 Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in complete workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🧪 Testing New PageProcessor Features")
    print("=" * 60)
    
    # Test 1: Single page processing
    print("\n1️⃣ Testing single page processing...")
    success1 = test_single_page_processing()
    
    # Test 2: CSV export functionality
    print("\n2️⃣ Testing CSV export functionality...")
    success2 = test_csv_export()
    
    # Test 3: Complete workflow
    print("\n3️⃣ Testing complete workflow...")
    success3 = test_complete_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Single page processing: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ CSV export functionality: {'PASSED' if success2 else 'FAILED'}")
    print(f"✅ Complete workflow: {'PASSED' if success3 else 'FAILED'}")
    
    if success1 and success2 and success3:
        print("\n🎉 All tests passed! New features are working correctly.")
        print("\n📋 Usage examples:")
        print("```python")
        print("# Single page processing")
        print("processor = PageProcessor(config_path='src/config.json')")
        print("page_data = processor.process_single_page_from_file('file.pdf', 0)")
        print("")
        print("# CSV export")
        print("result = PageBasedMedicalReportData()")
        print("result.page_0 = page_data")
        print("csv_record = result.to_csv_records()")
        print("df = pd.DataFrame([csv_record])")
        print("df.to_csv('output.csv', index=False)")
        print("```")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 