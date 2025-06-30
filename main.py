#!/usr/bin/env python3
"""
Main script for processing claim forms using Vision LLM
"""

import json
import os
from pathlib import Path
from src.llm_processor import ClaimFormProcessor


def main():
    """Main function to demonstrate claim form processing"""
    
    # Initialize the processor
    print("Initializing Claim Form Processor...")
    processor = ClaimFormProcessor(model_name="llama3.2-vision")
    
    # Define sample files (adjust paths as needed)
    sample_files = [
        "SAMPLE-TAL_Consent_for_Accessing_Health_Information.pdf",
        "SAMPLE-TAL Medical Examiner's Confidential Report.pdf"
    ]
    
    # Define corresponding form types
    form_types = [
        "consent_form",
        "medical_report"
    ]
    
    # Process each file
    results = []
    for file_path, form_type in zip(sample_files, form_types):
        if os.path.exists(file_path):
            print(f"\nProcessing: {file_path}")
            print(f"Form type: {form_type}")
            print("-" * 50)
            
            try:
                result = processor.process_file(file_path, form_type)
                results.append(result)
                
                if result["status"] == "success":
                    print("✅ Processing successful!")
                    print(f"Extracted {len(result['extracted_fields'])} fields")
                    
                    # Display some key fields
                    for key, value in list(result["extracted_fields"].items())[:5]:
                        print(f"  {key}: {value}")
                    
                    if len(result["extracted_fields"]) > 5:
                        print(f"  ... and {len(result['extracted_fields']) - 5} more fields")
                        
                else:
                    print("❌ Processing failed:")
                    print(f"  Error: {result.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Save results to output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Results saved to: {output_file}")
    print(f"Processed {len(results)} files total")


if __name__ == "__main__":
    main() 