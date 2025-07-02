from typing import Dict, List, Any, Optional
import time
from datetime import datetime
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .image_processor import ImageProcessor

# Add Pydantic imports for structured output
from pydantic import BaseModel, Field


# Pydantic data models for structured output
class MedicalHistoryItem(BaseModel):
    """Individual medical history question item"""
    id: int = Field(description="Question ID", default=0)
    question: str = Field(description="Question", default="")
    status: str = Field(description="Yes/No answer", default="")


class FamilyHistoryItem(BaseModel):
    """Family medical history item"""
    relationship: str = Field(description="Family relationship", default="")
    medical_condition: str = Field(description="Medical condition", default="")
    age_when_diagnosed: str = Field(description="Age when diagnosed", default="")
    age_at_death: str = Field(description="Age at death if applicable", default="")


class MeasurementsData(BaseModel):
    """Physical measurements data"""
    height_cm: Optional[float] = Field(description="Height in centimeters", default=None)
    weight_kg: Optional[float] = Field(description="Weight in kilograms", default=None)
    chest_full_inspiration_cm: Optional[float] = Field(description="Chest measurement at full inspiration", default=None)
    chest_full_expiration_cm: Optional[float] = Field(description="Chest measurement at full expiration", default=None)
    waist_circumference_cm: Optional[float] = Field(description="Waist circumference", default=None)
    hips_circumference_cm: Optional[float] = Field(description="Hip circumference", default=None)
    recent_weight_variation: str = Field(description="Recent weight variation", default="")
    weight_variation_details: str = Field(description="Weight variation details", default="")


class MedicalReportData(BaseModel):
    """Structured data for medical report form"""
    reference_number: str = Field(description="Reference number", default="")
    name_of_life_to_be_insured: str = Field(description="Name of person to be insured", default="")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format", default="")
    address: str = Field(description="Address", default="")
    suburb: str = Field(description="Suburb", default="")
    state: str = Field(description="State", default="")
    postcode: str = Field(description="Postcode", default="")
    occupation: str = Field(description="Occupation", default="")
    licence_number: str = Field(description="License number", default="")
    passport_number: str = Field(description="Passport number", default="")
    other_id_description: str = Field(description="Other ID description", default="")
    other_id_number: str = Field(description="Other ID number", default="")
    signature_of_life_to_be_insured_date: str = Field(description="Signature date of insured person", default="")
    witness_signature_date: str = Field(description="Witness signature date", default="")
    medical_history: List[MedicalHistoryItem] = Field(description="Medical history questions", default=[])
    family_history: List[FamilyHistoryItem] = Field(description="Family medical history", default=[])
    measurements: MeasurementsData = Field(description="Physical measurements", default_factory=MeasurementsData)

    def print_reference_number(self):
        print(self.reference_number)
        return self.reference_number

    def load_data(self, data: str):
        print ('1')
        pass

class ConsentFormData(BaseModel):
    """Structured data for consent form"""
    reference_number: str = Field(description="Reference number", default="")
    life_to_be_insured_name: str = Field(description="Name of person to be insured", default="")
    life_to_be_insured_dob: str = Field(description="Date of birth in YYYY-MM-DD format", default="")
    authority1_name: str = Field(description="First authority name", default="")
    authority1_signature_date: str = Field(description="First authority signature date", default="")
    authority2_name: str = Field(description="Second authority name", default="")
    authority2_signature_date: str = Field(description="Second authority signature date", default="")


class ClaimFormProcessor:
    """Process claim forms using Vision LLM via Ollama with timing and progress tracking"""
    
    def __init__(self, model_name: str = "llama3.2-vision", base_url: Optional[str] = None):
        """
        Initialize the claim form processor
        
        :param model_name: Name of the Ollama vision model to use
        :param base_url: Optional base URL for Ollama service
        """
        self.model_name = model_name
        # self.llm = OllamaLLM(model=model_name, base_url=base_url)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="AIzaSyDJGFa_m8zgmL-jo6EfSvaWbInjvwzV1JY")
        self.image_processor = ImageProcessor()
        
        # Create a separate ChatOllama instance for structured output (using llama3.2 for text processing)
        # self.structured_chat_llm = ChatOllama(model="llama3.2:3b", base_url=base_url)
        self.structured_chat_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="AIzaSyDJGFa_m8zgmL-jo6EfSvaWbInjvwzV1JY")
        
        self.processing_stats = {
            "total_processed": 0,
            "total_time": 0.0,
            "average_time": 0.0
        }
    
    def extract_form_data(self, list_image_b64: list[str], form_type: str = "generic", verbose: bool = True) -> Any:
        """
        Extract structured data from a claim form image with timing
        
        :param list_image_b64: List of Base64 encoded image strings
        :param form_type: Type of form for specialized prompts
        :param verbose: Whether to show progress messages
        :return: Structured Pydantic data object (MedicalReportData or ConsentFormData)
        """
        start_time = time.time()
        
        if verbose:
            print(f"🔍 Starting multi-image LLM analysis... (Model: {self.model_name})")
            print(f"📄 Processing {len(list_image_b64)} images together")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Bind images to LLM context using chain binding (required for llama3.2-vision)
            llm_with_image = self.llm
            # for image_b64 in list_image_b64:
            #     llm_with_image = llm_with_image.bind(images=[image_b64])
            
            # Get appropriate prompt based on form type
            prompt = self._get_extraction_prompt(form_type)
            
            # Create content blocks for Gemini format with HumanMessage
            content_blocks = [{"type": "text", "text": prompt}]
            
            # Add images in proper Gemini format
            for b64 in list_image_b64:
                content_blocks.append({
                    "type": "image_url", 
                    "image_url": f"data:image/png;base64,{b64}"
                })

            # Create HumanMessage for Gemini
            message = HumanMessage(content=content_blocks)

            # Process with LLM
            if verbose:
                print("💭 LLM is analyzing the image and extracting information...")
            
            response = llm_with_image.invoke([message])
            print(response)
            
            # Convert to structured data object
            if verbose:
                print("🔧 Converting to structured data object...")
            structured_data = self._convert_to_structured_data(response, form_type, verbose)

            processing_time = time.time() - start_time
            
            if verbose:
                print(f"✅ LLM processing completed!")
                print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(structured_data)

            # Update stats
            self._update_stats(processing_time)
            
            # Parse and structure the response
            # result = self._parse_llm_response(response, form_type)
            # result = {}
            # result["processing_time"] = processing_time
            # result["model_used"] = self.model_name
            # result["timestamp"] = datetime.now().isoformat()
            
            # # Convert to structured data object
            # result["response"] = response
            # result["structured_data"] = structured_data
            
            return structured_data
            
        except Exception as e:
            processing_time = time.time() - start_time
            if verbose:
                print(f"❌ Error during LLM processing after {processing_time:.2f} seconds")
                print(f"Error details: {str(e)}")
            
            # Return default structured data object on error
            if form_type == "medical_report":
                return MedicalReportData()
            elif form_type == "consent_form":
                return ConsentFormData()
            else:
                return MedicalReportData()
    
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
        
        For each yes/no question, extract:"answer" as "Yes" or "No", "details" text if present.
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
    "1": { "id": 1, "question": "Any disease, disorder or condition relating to the heart and circulatory system including high blood pressure, raised cholesterol, heart murmur, stroke, brain haemorrhage, or embolism, chest pain
or palpitations", "status": "Yes/No" },
    "2": { "id": 2, "question": "Diabetes or raised blood sugar levels?", "status": "" },
    "...": "...",
    "27": { "id": 27, "question": "Apart from any condition already disclosed, do you plan to seek or are you awaiting medical advice, investigation or treatment for any other current health condition or symptoms?", "status": "" }
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
  "reference_number": "",
  "life_to_be_insured_name": "",
  "life_to_be_insured_dob": "",
  "authority1_name": "",
  "authority1_signature_date": "",
  "authority2_name": "",
  "authority2_signature_date": ""
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
    
    def _convert_to_structured_data(self, raw_response: str, form_type: str, verbose: bool = True) -> Any:
        """
        Convert raw LLM response to structured Pydantic data object using ChatOllama
        
        :param raw_response: Raw response from vision LLM
        :param form_type: Type of form for appropriate data model selection
        :param verbose: Whether to show progress messages
        :return: Structured Pydantic data object
        """
        if verbose:
            print("🔄 Converting to structured data object...")
        
        try:
            # Select appropriate Pydantic model based on form type
            if form_type == "medical_report":
                structured_llm = self.structured_chat_llm.with_structured_output(MedicalReportData)
                data_model = MedicalReportData
            elif form_type == "consent_form":
                structured_llm = self.structured_chat_llm.with_structured_output(ConsentFormData)
                data_model = ConsentFormData
            else:
                # Default to medical report for unknown types
                structured_llm = self.structured_chat_llm.with_structured_output(MedicalReportData)
                data_model = MedicalReportData
            
            # Create prompt for structured conversion
            conversion_prompt = f"""
            Please extract and structure the following form data into the appropriate format.
            
            Raw extracted data:
            {raw_response}
            
            Please parse this information and return it in the structured format. 
            For any missing or unclear information, use empty strings or appropriate defaults.
            For dates, ensure they are in YYYY-MM-DD format.
            For yes/no answers, use "Yes", "No", or "" if unclear.
            """
            
            # Get structured output
            structured_data = structured_llm.invoke(conversion_prompt)
            
            if verbose:
                print(f"✅ Successfully converted to {data_model.__name__} object")
            
            return structured_data
            
        except Exception as e:
            if verbose:
                print(f"❌ Error converting to structured data: {str(e)}")
            
            # Return default instance on error
            if form_type == "medical_report":
                return MedicalReportData()
            elif form_type == "consent_form":
                return ConsentFormData()
            else:
                return MedicalReportData()
    
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
            
            # Extract form data (returns Pydantic object)
            structured_data = self.extract_form_data(image_b64_list, form_type, verbose)
            
            total_time = time.time() - start_time
            
            # Create result wrapper with metadata and structured data
            if verbose:
                print("=" * 60)
                print(f"🎉 Successfully processed: {file_path}")
                print(f"⏱️  Total time: {total_time:.2f} seconds")
                print(f"📋 Form type: {form_type}")
                print(f"🏗️  Data model: {type(structured_data).__name__}")
            
            return structured_data
            
        except Exception as e:
            total_time = time.time() - start_time
            if verbose:
                print("=" * 60)
                print(f"❌ Unexpected error processing: {file_path}")
                print(f"⏱️  Time spent: {total_time:.2f} seconds")
                print(f"🔍 Error: {str(e)}")
            
            return str(e)
    
    def extract_structured_data(self, file_path: str, form_type: str = "generic", verbose: bool = True) -> Any:
        """
        Extract form data and return only the structured Pydantic data object
        
        :param file_path: Path to the file
        :param form_type: Type of form for specialized processing
        :param verbose: Whether to show progress messages
        :return: Structured Pydantic data object (MedicalReportData or ConsentFormData)
        """
        result = self.process_file(file_path, form_type, verbose)
        
        # The structured_data should always be present in the new format
        return result["structured_data"]
   