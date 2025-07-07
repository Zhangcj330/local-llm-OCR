#!/usr/bin/env python3
"""
Test script for sequential page processing functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_processor import ClaimFormProcessor


def test_sequential_processing():
    """Test the new sequential processing functionality"""
    
    print("🧪 Testing Sequential Page Processing")
    print("=" * 60)
    
    # Initialize processor
    processor = ClaimFormProcessor(model_name="gemini-2.0-flash")
    
    # Test file
    test_file = "SAMPLE-TAL Medical Examiner's Confidential Report.pdf"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📁 Testing with file: {test_file}")
    
    try:
        # Process the multi-page file
        result = processor.process_file(test_file, "medical_report", verbose=True)
        
        print("\n" + "=" * 60)
        print("✅ Sequential processing test completed!")
        print(f"📊 Result type: {type(result).__name__}")
        
        # Print basic extracted information if available
        if hasattr(result, 'name_of_life_to_be_insured'):
            print(f"👤 Name: {result.name_of_life_to_be_insured}")
        if hasattr(result, 'date_of_birth'):
            print(f"📅 DOB: {result.date_of_birth}")
        if hasattr(result, 'reference_number'):
            print(f"🔢 Reference: {result.reference_number}")
            
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")


def test_single_page_vs_multi_page():
    """Compare single page processing vs multi-page processing"""
    
    print("\n" + "🔍 Comparing Processing Strategies")
    print("=" * 60)
    
    processor = ClaimFormProcessor(model_name="gemini-2.0-flash")
    
    # Create dummy base64 list for testing
    dummy_b64 = ["dummy_data_123"]
    
    print("📄 Testing with single page...")
    try:
        single_result = processor.extract_form_data(dummy_b64, "medical_report", verbose=True)
        print(f"✅ Single page processing: Success ({len(single_result)} chars)")
    except Exception as e:
        print(f"❌ Single page processing failed: {str(e)}")
    
    print("\n📑 Testing with multiple pages...")
    try:
        multi_result = processor.extract_form_data(["dummy1", "dummy2", "dummy3"], "medical_report", verbose=True)
        print(f"✅ Multi-page processing: Success ({len(multi_result)} chars)")
    except Exception as e:
        print(f"❌ Multi-page processing failed: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Sequential Processing Tests")
    print("=" * 60)
    
    test_sequential_processing()
    test_single_page_vs_multi_page()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!") 