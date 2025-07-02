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
                    
                    # Get structured data
                    structured_data = result["structured_data"]
                    data_model_name = type(structured_data).__name__
                    print(f"📋 Data model: {data_model_name}")
                    
                    # Display some key fields from structured data
                    data_dict = structured_data.model_dump()
                    non_empty_fields = {k: v for k, v in data_dict.items() if v and v != {} and v != []}
                    
                    print(f"📊 Extracted {len(non_empty_fields)} non-empty fields:")
                    for key, value in list(non_empty_fields.items())[:5]:
                        if isinstance(value, (dict, list)):
                            print(f"  {key}: {type(value).__name__} with {len(value)} items")
                        else:
                            print(f"  {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                    
                    if len(non_empty_fields) > 5:
                        print(f"  ... and {len(non_empty_fields) - 5} more fields")
                        
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
    
    # Convert results for JSON serialization
    serializable_results = []
    for result in results:
        serializable_result = result.copy()
        # Convert Pydantic object to dictionary for JSON serialization
        if "structured_data" in serializable_result:
            serializable_result["structured_data"] = serializable_result["structured_data"].model_dump()
        serializable_results.append(serializable_result)
    
    output_file = output_dir / "extraction_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 Results saved to: {output_file}")
    print(f"Processed {len(results)} files total")


if __name__ == "__main__":
    main() 