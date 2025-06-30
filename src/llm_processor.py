from typing import Dict, List, Any, Optional
import time
from datetime import datetime
from langchain_ollama import OllamaLLM
from .image_processor import ImageProcessor


class ClaimFormProcessor:
    """Process claim forms using Vision LLM via Ollama with timing and progress tracking"""
    
    def __init__(self, model_name: str = "llama3.2-vision", base_url: Optional[str] = None):
        """
        Initialize the claim form processor
        
        :param model_name: Name of the Ollama vision model to use
        :param base_url: Optional base URL for Ollama service
        """
        self.model_name = model_name
        self.llm = OllamaLLM(model=model_name, base_url=base_url)
        self.image_processor = ImageProcessor()
        self.processing_stats = {
            "total_processed": 0,
            "total_time": 0.0,
            "average_time": 0.0
        }
    
    def extract_form_data(self, list_image_b64: list[str], form_type: str = "generic", verbose: bool = True) -> Dict[str, Any]:
        """
        Extract structured data from a claim form image with timing
        
        :param list_image_b64: List of Base64 encoded image strings
        :param form_type: Type of form for specialized prompts
        :param verbose: Whether to show progress messages
        :return: Dictionary containing extracted form data
        """
        start_time = time.time()
        
        if verbose:
            print(f"🔍 Starting multi-image LLM analysis... (Model: {self.model_name})")
            print(f"📄 Processing {len(list_image_b64)} images together")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Bind images to LLM context using chain binding (required for llama3.2-vision)
            llm_with_image = self.llm
            for image_b64 in list_image_b64:
                llm_with_image = llm_with_image.bind(images=[image_b64])
            
            # Get appropriate prompt based on form type
            prompt = self._get_extraction_prompt(form_type)
            
            # Process with LLM
            if verbose:
                print("💭 LLM is analyzing the image and extracting information...")
            
            response = llm_with_image.invoke(prompt)
            
            processing_time = time.time() - start_time
            
            if verbose:
                print(f"✅ LLM processing completed!")
                print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            
            # Update stats
            self._update_stats(processing_time)
            
            # Parse and structure the response
            result = self._parse_llm_response(response, form_type)
            result["processing_time"] = processing_time
            result["model_used"] = self.model_name
            result["timestamp"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            if verbose:
                print(f"❌ Error during LLM processing after {processing_time:.2f} seconds")
                print(f"Error details: {str(e)}")
            
            return {
                "form_type": form_type,
                "raw_response": "",
                "extracted_fields": {},
                "confidence": "error",
                "processing_time": processing_time,
                "model_used": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _update_stats(self, processing_time: float):
        """Update processing statistics"""
        self.processing_stats["total_processed"] += 1
        self.processing_stats["total_time"] += processing_time
        self.processing_stats["average_time"] = (
            self.processing_stats["total_time"] / self.processing_stats["total_processed"]
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.processing_stats.copy()
    
    def _get_extraction_prompt(self, form_type: str) -> str:
        """
        Get specialized extraction prompt based on form type
        
        :param form_type: Type of form (generic, medical_report, consent_form, etc.)
        :return: Optimized prompt string
        """
        base_prompt = """
        Please analyze these form images as a complete multi-page document and extract all the key information in a structured format.
        
        IMPORTANT: You are viewing ALL pages of a single document. Please consolidate information across all pages.
        Focus on:
        1. Personal information (names, dates, addresses, phone numbers) from any page
        2. Form-specific data fields and their values across all pages
        3. Signatures and dates from any page
        4. Any checkbox selections or marked fields on any page
        5. Important notes or comments from any page
        
        For information that appears on multiple pages, consolidate it (don't duplicate).
        
        For each yes/no question, extract:"answer" as “Yes” or “No”, "details" text if present.
        Keep missing fields as null or empty string "".
        Format all dates as YYYY-MM-DD
        Please provide the information in a clear, structured format with field names and values.
        If a field is empty or unclear, mark it as "Not provided" or "Unclear".

        Return results in this JSON structure:
        """
        
        if form_type == "medical_report":
            return base_prompt + """
            
            {
  "reference_number": "",
  "name_of_life_to_be_insured": "",
  "date_of_birth": "",
  "address": "",
  "suburb": "",
  "state": "",
  "postcode": "",
  "occupation": "",
  "licence_number": "",
  "passport_number": "",
  "other_id_description": "",
  "other_id_number": "",
  "signature_of_life_to_be_insured_date": "",
  "witness_signature_date": "",
  "medical_history": {
    "1": { "answer": "", "details": "" },
    "2": { "answer": "", "details": "" },
    "...": "...",
    "27": { "answer": "", "details": "" }
  },
  "family_history": [
    {
      "relationship": "",
      "medical_condition": "",
      "age_when_diagnosed": "",
      "age_at_death": ""
    }
  ],
  "measurements": {
    "height_cm": null,
    "weight_kg": null,
    "chest_full_inspiration_cm": null,
    "chest_full_expiration_cm": null,
    "waist_circumference_cm": null,
    "hips_circumference_cm": null,
    "recent_weight_variation": "",
    "weight_variation_details": ""
  },
  "...": "Other systems and summary fields as per document"
}
            """
        
        elif form_type == "consent_form":
            return base_prompt + """
            
            {
  "reference_number": "202506253110",
  "life_to_be_insured_name": "Kevin Smith",
  "life_to_be_insured_dob": "1998-10-31",
  "authority1_name": "Kevin Smith",
  "authority1_signature_date": "2025-06-25",
  "authority2_name": "Kevin Smith",
  "authority2_signature_date": "2025-06-25"
}
            """
        
        return base_prompt
    
    def _parse_llm_response(self, response: str, form_type: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format
        
        :param response: Raw LLM response
        :param form_type: Type of form for specialized parsing
        :return: Structured dictionary
        """
        # Basic parsing - can be enhanced with more sophisticated parsing logic
        result = {
            "form_type": form_type,
            "raw_response": response,
            "extracted_fields": {},
            "confidence": "medium"  # Could implement confidence scoring
        }
        
        # Simple field extraction from response
        # This can be enhanced with regex patterns or structured output prompting
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':', 1)) == 2:
                key, value = line.split(':', 1)
                result["extracted_fields"][key.strip()] = value.strip()
        
        return result
    
    def process_file(self, file_path: str, form_type: str = "generic", verbose: bool = True) -> Dict[str, Any]:
        """
        Process a file (PDF or image) and extract form data with detailed progress tracking
        
        :param file_path: Path to the file
        :param form_type: Type of form for specialized processing
        :param page_index: Page index for PDF files (0-based)
        :param verbose: Whether to show progress messages
        :return: Extracted form data
        """
        start_time = time.time()
        
        if verbose:
            print(f"\n🚀 Processing file: {file_path}")
            print(f"📋 Form type: {form_type}")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
        
        try:
            # Convert file to base64
            if verbose:
                print("🖼️  Converting file to image format...")
            image_b64_list = []

            # process all pages of the file
            images = self.image_processor.pdf_to_images(file_path)
            for i in range(len(images)):
                image_b64 = self.image_processor.process_file_to_base64(file_path, i)
                image_b64_list.append(image_b64)
            
            if verbose:
                print(f"✅ All pages Image conversion completed")
                print(f"✅ LLM is analyzing the image and extracting information...")
            
            # Extract form data
            result = self.extract_form_data(image_b64_list, form_type, verbose)
            
            total_time = time.time() - start_time
            
            # Add metadata
            result["source_file"] = file_path
            result["total_processing_time"] = total_time
            
            if "error" not in result:
                result["status"] = "success"
                if verbose:
                    print("=" * 60)
                    print(f"🎉 Successfully processed: {file_path}")
                    print(f"⏱️  Total time: {total_time:.2f} seconds")
                    print(f"📊 Extracted {len(result['extracted_fields'])} fields")
            else:
                result["status"] = "error"
                if verbose:
                    print("=" * 60)
                    print(f"❌ Failed to process: {file_path}")
                    print(f"⏱️  Time spent: {total_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            if verbose:
                print("=" * 60)
                print(f"❌ Unexpected error processing: {file_path}")
                print(f"⏱️  Time spent: {total_time:.2f} seconds")
                print(f"🔍 Error: {str(e)}")
            
            return {
                "source_file": file_path,
                "status": "error",
                "error_message": str(e),
                "extracted_fields": {},
                "total_processing_time": total_time,
                "timestamp": datetime.now().isoformat()
            }
    
   