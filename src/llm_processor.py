from typing import Dict, List, Any, Optional
import time
from datetime import datetime
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .image_processor import ImageProcessor
from .data import MedicalReportData, ConsentFormData, BasicInfoAndHistoryExtraction, MedicalExaminationExtraction, SummaryAndExaminerExtraction, MEDICAL_HISTORY_QUESTIONS, FAMILY_HISTORY_QUESTIONS

class ClaimFormProcessor:
    """Process claim forms using Vision LLM via Ollama with timing and progress tracking"""
    
    def __init__(self, model_name: str = "gemma3:12b", base_url: Optional[str] = None):
        """
        Initialize the claim form processor
        
        :param model_name: Name of the Ollama vision model to use
        :param base_url: Optional base URL for Ollama service
        """
        self.model_name = model_name
        self.image_processor = ImageProcessor()
        
        if model_name == "gemma3:12b":
            self.llm = ChatOllama(model="gemma3:12b", base_url=base_url)
        elif model_name == "gemini-2.0-flash":
            self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="AIzaSyDJGFa_m8zgmL-jo6EfSvaWbInjvwzV1JY")
        else:
            raise ValueError(f"Model {model_name} not supported")
        
        # Ollama model
        # self.llm = OllamaLLM(model=model_name, base_url=base_url)
        self.structured_chat_llm = ChatOllama(model="gemma3:12b", base_url=base_url)
        # Gemini model
        # self.structured_chat_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="AIzaSyDJGFa_m8zgmL-jo6EfSvaWbInjvwzV1JY")
        # self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key="AIzaSyDJGFa_m8zgmL-jo6EfSvaWbInjvwzV1JY")

    
    def extract_form_data(self, list_image_b64: list[str], form_type: str = "generic", verbose: bool = True) -> str:
        """
        Extract structured data from a claim form image with timing
        """
        
        if verbose:
            print(f"🔍 Starting multi-image LLM analysis... (Model: {self.model_name})")
            print(f"📄 Processing {len(list_image_b64)} images")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Choose processing strategy based on number of images
            if len(list_image_b64) == 1:
                if verbose:
                    print("📄 Single page detected - using direct processing")
                return self._process_single_page(list_image_b64[0], form_type, verbose)
            else:
                if verbose:
                    print(f"📑 Multiple pages detected ({len(list_image_b64)}) - using sequential processing")
                return self._process_multiple_pages_sequential(list_image_b64, form_type, verbose)
            
        except Exception as e:
            if verbose:
                print(f"Error details: {str(e)}")
            return f"Error processing images: {str(e)}"
    
    def _process_single_page(self, image_b64: str, form_type: str, verbose: bool) -> str:
        """
        Process a single page with full extraction prompt
        """
        if verbose:
            print("💭 LLM is analyzing the single page...")
        
        # Use full extraction prompt for single page
        prompt = self._get_extraction_prompt(form_type)
        
        content_blocks = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
        ]
        
        message = HumanMessage(content=content_blocks)
        response = self.llm.invoke([message])
        
        return response.content
    
    def _process_multiple_pages_sequential(self, list_image_b64: list[str], form_type: str, verbose: bool) -> str:
        """
        Process multiple pages sequentially then combine results
        """
        page_results = []
        
        for i, image_b64 in enumerate(list_image_b64):
            if verbose:
                print(f"📄 Processing page {i+1}/{len(list_image_b64)}...")
            
            # Get page-specific prompt
            page_prompt = self._get_page_specific_prompt(form_type, i, len(list_image_b64))
            
            content_blocks = [
                {"type": "text", "text": page_prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
            ]
            
            message = HumanMessage(content=content_blocks)
            page_response = self.llm.invoke([message])
            
            # Store page result with header
            page_results.append(f"=== PAGE {i+1} CONTENT ===\n{page_response.content}")
            
            if verbose:
                print(f"✅ Page {i+1} completed")
        
        # Combine all page results
        combined_result = "\n\n".join(page_results)
        
        if verbose:
            print("🔗 Combining results from all pages...")
        
        # Add summary header
        final_result = f"""=== COMBINED EXTRACTION FROM {len(list_image_b64)} PAGES ===

{combined_result}

=== END OF EXTRACTION ==="""
        
        return final_result
    
    def _get_page_specific_prompt(self, form_type: str, page_index: int, total_pages: int) -> str:
        """
        Generate page-specific extraction prompt based on page position
        """
        base_instruction = f"""
        This is page {page_index + 1} of {total_pages} from a {form_type} form.
        
        Extract ALL visible information from this page only. Be thorough and include:
        - Any personal details (names, addresses, dates, ID numbers)
        - Any medical questions and their answers (Y/N/Yes/No plus details)
        - Any measurements, test results, or examination findings
        - Any checkboxes (marked or unmarked)
        - Any signatures, dates, or handwritten notes
        - Any examiner comments or conclusions
        
        Format your response clearly with section headers when appropriate.
        For yes/no questions, clearly indicate the question number and answer.
        For any unclear text, note it as "unclear" rather than guessing.
        """
        
        # Add page-specific guidance based on common medical form structure
        if page_index == 0:
            page_guidance = """
        
        This is typically the first page, which usually contains:
        - Basic personal information (name, DOB, address)
        - Policy/reference numbers
        - Contact details and identification
        - Initial signatures or declarations
        """
        elif page_index == 1 and total_pages > 2:
            page_guidance = """
        
        This is typically a middle page, which may contain:
        - Medical history questions (numbered list with Y/N answers)
        - Family history information
        - Detailed medical questionnaires
        """
        else:
            page_guidance = """
        
        This may be a later page, which often contains:
        - Physical examination results
        - Measurements and vital signs
        - Doctor's observations and conclusions
        - Examiner details and signatures
        """
        
        return base_instruction + page_guidance
    
    def extract_structured_data(self, response: str, form_type: str = "generic", verbose: bool = True) -> Any:
        """
        Convert raw LLM response to structured Pydantic data object using staged extraction
        
        :param raw_response: Raw response from vision LLM
        :param form_type: Type of form for appropriate data model selection
        :param verbose: Whether to show progress messages
        :return: Structured Pydantic data object
        """
        try: 
            if verbose:
                print("🔧 Converting to structured data object...")
            structured_data = self._convert_to_structured_data(response, form_type, verbose)
            
            if verbose:
                print(f"✅ LLM processing completed!")
            print(structured_data)

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
            if verbose:
                print(f"Error details: {str(e)}")
            
            # Return default structured data object on error
            if form_type == "medical_report":
                return MedicalReportData()
            elif form_type == "consent_form":
                return ConsentFormData()
            else:
                return MedicalReportData()
    

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
            return base_prompt + f"""
            
            Please extract ALL information according to this COMPLETE structure:

            ===== SECTION 1: BASIC INFORMATION =====
            - reference_number: Policy reference number
            - name_of_life_to_be_insured: Full name of the insured person
            - date_of_birth: Date of birth (YYYY-MM-DD format)
            - address: Street address
            - suburb: Suburb
            - state: State/Province
            - postcode: Postal code
            - occupation: Professional occupation
            - licence_number: Driver's licence number
            - passport_number: Passport number
            - other_id_description: Description of other ID
            - other_id_number: Other ID number
            - signature_of_life_to_be_insured_date: Date when insured person signed (YYYY-MM-DD)
            - witness_signature_date: Date when witness signed (YYYY-MM-DD)

            ===== SECTION 2: MEDICAL HISTORY (Questions 1-27) =====
            For EACH of the 27 predefined medical history questions, extract:
            - Status: "Y", "N", "Yes", "No", or "" if not found
            - Details: Any additional text provided if status is Yes
            
            The 27 questions are:
            {[f"{q['id']}. {q['question']}" for q in MEDICAL_HISTORY_QUESTIONS]}

            ===== SECTION 3: FAMILY HISTORY =====
            For EACH family history condition, extract:
            - Status: "Y", "N", "Yes", "No", or "" if not found
            
            The 9 family history conditions are:
            {[f"{q['id']}. {q['question']}" for q in FAMILY_HISTORY_QUESTIONS]}
            
            For positive family history, also extract detailed information:
            - relationship: Family relationship (father, mother, brother, sister, etc.)
            - medical_condition: Specific medical condition
            - age_when_diagnosed: Age when diagnosed
            - age_at_death: Age at death (if applicable)
            - details_of_investigation: Details of any investigations performed

            ===== SECTION 4: CONFIDENTIAL MEDICAL EXAMINATION =====
            - known_to_examiner: Whether applicant is known to examiner (true/false)
            - previously_attended_examiner: Whether applicant has previously attended examiner (true/false)
            - unusual_build_or_behavior: Description of unusual build or behavior
            - signs_of_tobacco_alcohol_or_drugs: Signs of tobacco, alcohol or drugs use
            - ever_smoked: Whether applicant has ever smoked (true/false)

            ===== SECTION 5: MEASUREMENTS =====
            - height_cm: Height in centimeters (numeric)
            - weight_kg: Weight in kilograms (numeric)
            - chest_full_inspiration_cm: Chest measurement at full inspiration (numeric)
            - chest_full_expiration_cm: Chest measurement at full expiration (numeric)
            - waist_circumference_cm: Waist circumference (numeric)
            - hips_circumference_cm: Hip circumference (numeric)
            - recent_weight_variation: Has there been recent weight variation? (true/false)
            - weight_variation_details: Details about weight variation
            - chest_expansion_details: Details about chest expansion

            ===== SECTION 6: RESPIRATORY SYSTEM =====
            - respiratory_abnormality: Abnormality of respiratory system to palpation, percussion or auscultation
            - respiratory_abnormality_details: Details of the abnormality
            - respiratory_sign: Sign of past or present respiratory disease
            - respiratory_sign_details: Details of the sign

            ===== SECTION 7: CIRCULATORY SYSTEM =====
            - pulse_rate_and_character: Pulse rate and character
            - apex_beat_position: Position of the apex beat
            - apex_interspace: Interspace between apex beat and midsternal border
            - apex_distance_from_midsternal: Distance from apex beat to midsternal border (numeric)
            - cardiac_enlargement: Whether there is cardiac enlargement (true/false)
            - cardiac_enlargement_details: Details of cardiac enlargement
            - abnormal_heart_sounds_or_rhythm: Whether there are abnormal heart sounds or rhythm (true/false)
            - abnormal_heart_sounds_or_rhythm_details: Details of abnormal heart sounds or rhythm
            - murmurs: Whether there are murmurs (true/false)
            - murmurs_details: Details of murmurs
            - bp_Systolic_1: First systolic blood pressure reading (numeric)
            - bp_Diastolic_1: First diastolic blood pressure reading (numeric)
            - bp_Systolic_2: Second systolic blood pressure reading (numeric)
            - bp_Diastolic_2: Second diastolic blood pressure reading (numeric)
            - bp_Systolic_3: Third systolic blood pressure reading (numeric)
            - bp_Diastolic_3: Third diastolic blood pressure reading (numeric)
            - peripheral_abnormalities: Whether there are peripheral abnormalities (true/false)
            - peripheral_abnormalities_details: Details of peripheral abnormalities
            - heart_and_vascular_system_abnormal: Whether there are heart and vascular system abnormalities (true/false)
            - heart_and_vascular_system_abnormal_details: Details of heart and vascular system abnormalities
            - on_treatment_for_hypertension: Whether applicant is on treatment for hypertension (true/false)
            - hypertension_pretreatment_bp: Pretreatment blood pressure
            - hypertension_duration: Duration of hypertension
            - hypertension_treatment_nature: Nature of hypertension treatment

            ===== SECTION 8: DIGESTIVE, ENDOCRINE AND LYMPH SYSTEMS =====
            - hernia_present: Whether a hernia is present (true/false)
            - hernia_details: Details if hernia is present
            - lymph_gland_abnormality: Whether there is lymph gland abnormality in neck, axillae, or inguinal regions (true/false)
            - lymph_gland_abnormality_details: Details if lymph gland abnormality is present

            ===== SECTION 9: GENITO-URINARY FINDINGS =====
            - genito_urinary_abnormality: Whether any genito-urinary abnormality is present (true/false)
            - genito_urinary_abnormality_details: Details if genito-urinary abnormality is present
            - urine_protein: Whether urine contains protein/albumin (true/false)
            - urine_sugar: Whether urine contains sugar (true/false)
            - urine_blood: Whether urine contains blood (true/false)
            - urine_blood_menstruating: Whether blood in urine is due to menstruation (true/false)
            - urine_other_abnormalities: Whether urine contains other abnormalities (true/false)
            - urine_other_abnormalities_details: Details of other abnormalities in urine
            - is_pregnant: Whether applicant is pregnant (true/false)
            - expected_delivery_date: Expected delivery date if pregnant (DD/MM/YYYY)

            ===== SECTION 10: NERVOUS SYSTEM =====
            - vision_defect_or_eye_abnormality: Whether there is any defect of vision or abnormality of the eyes (true/false)
            - vision_defect_or_eye_abnormality_details: Details if there is any defect of vision or abnormality of the eyes
            - hearing_or_speech_defect: Whether there is any defect in hearing or speech (true/false)
            - hearing_or_speech_defect_details: Details if there is any defect in hearing or speech

            ===== SECTION 11: MUSCULOSKELETAL AND SKIN =====
            - joint_abnormality: Whether there is any abnormality of the form or function of the joints (true/false)
            - joint_abnormality_details: Details if there is abnormality of the joints
            - muscle_or_connective_tissue_abnormality: Whether there is any abnormality of the form or function of the muscles or connective tissues (true/false)
            - muscle_or_connective_tissue_abnormality_details: Details if there is abnormality of the muscles or connective tissues
            - back_or_neck_abnormality: Whether there is any abnormality of the form or function of the back or neck including cervical and lumbar spine (true/false)
            - back_or_neck_abnormality_details: Details if there is abnormality of the back or neck
            - skin_disorder: Whether there is any evidence of disorder of the skin (true/false)
            - skin_disorder_details: Details if there is any disorder of the skin

            ===== SECTION 12: SUMMARY =====
            - medical_attendants_reports_required: Whether any medical attendant's reports or special tests are required (true/false)
            - medical_attendants_reports_details: Details if medical attendant's reports or special tests are required
            - likely_to_require_surgery: Whether the person examined is likely to require any surgical operation (true/false)
            - likely_to_require_surgery_details: Details if surgery is likely to be required
            - unfavourable_history_personal_or_family: Any unfavourable features in personal or family medical history which could reduce life expectancy or cause disablement
            - unfavourable_findings_medical_exam: Any unfavourable features disclosed by medical examination which could reduce life expectancy or cause disablement

            ===== SECTION 13: EXAMINER DETAILS =====
            - name: Full name of the examiner
            - address: Street address of the examiner
            - suburb: Suburb of the examiner's address
            - state: State of the examiner's address
            - postcode: Postcode of the examiner's address
            - phone: Phone number of the examiner
            - personal_qualifications: Personal qualifications of the examiner
            - signature_present: Whether the examiner's signature is present (true/false)
            - date_signed: Date the form was signed by the examiner (YYYY-MM-DD)

            IMPORTANT EXTRACTION GUIDELINES:
            1. Extract ALL information even if some fields are empty
            2. For boolean fields, use true/false (not True/False)
            3. For numeric fields, extract actual numbers without units
            4. For dates, ensure YYYY-MM-DD format
            5. For yes/no questions, use "Y", "N", "Yes", "No", or "" if unclear
            6. Be thorough - this is a comprehensive medical form with many sections
            7. Look for checkboxes, handwritten notes, and typed text across all pages
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
        Convert raw LLM response to structured Pydantic data object using staged extraction
        
        :param raw_response: Raw response from vision LLM
        :param form_type: Type of form for appropriate data model selection
        :param verbose: Whether to show progress messages
        :return: Structured Pydantic data object
        """
        if verbose:
            print("🔄 Converting to structured data object using staged extraction...")
        
        try:
            if form_type == "medical_report":
                return self._extract_medical_report_staged(raw_response, verbose)
            elif form_type == "consent_form":
                return self._extract_consent_form_single_stage(raw_response, verbose)
            else:
                # Default to medical report for unknown types
                return self._extract_medical_report_staged(raw_response, verbose)
            
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
    
    def _extract_medical_report_staged(self, raw_response: str, verbose: bool = True) -> MedicalReportData:
        """
        Extract medical report data using staged approach
        
        :param raw_response: Raw response from vision LLM
        :param verbose: Whether to show progress messages
        :return: MedicalReportData object
        """
        if verbose:
            print("📋 Stage 1: Extracting basic info and history...")
        
        # Stage 1: Basic info and history
        stage1_llm = self.structured_chat_llm.with_structured_output(BasicInfoAndHistoryExtraction)
        stage1_prompt = f"""
        Please extract ONLY the basic information and medical/family history from the following form data.
        
        Raw extracted data:
        {raw_response}
        
        EXTRACT ONLY:
        1. BASIC INFO: Reference number, name, date of birth, address, occupation, ID numbers, signature dates
        2. MEDICAL HISTORY: For each of the 27 predefined medical history questions, extract:
           - Status: "Y", "N", "Yes", "No", or "" if not found
           - Details: Any additional text provided if status is Yes
        3. MEDICAL HISTORY DETAILS: Any general details section for questions 1-27
        4. FAMILY HISTORY CONDITIONS: For each of the 9 predefined family history conditions, extract:
           - Status: "Y", "N", "Yes", "No", or "" if not found
        5. FAMILY HISTORY DETAILS: Detailed family member information (relationship, condition, ages)
        
        The 27 medical history questions are already predefined in the model.
        The 9 family history conditions are already predefined in the model.
        You only need to provide the extracted status and details for each question.
        
        For dates, ensure they are in YYYY-MM-DD format.
        For yes/no answers, use "Y", "N", "Yes", "No", or "" if unclear.
        """
        
        stage1_data = stage1_llm.invoke(stage1_prompt)
        
        if verbose:
            print("🏥 Stage 2: Extracting medical examination findings...")
        
        # Stage 2: Medical examination findings
        stage2_llm = self.structured_chat_llm.with_structured_output(MedicalExaminationExtraction)
        stage2_prompt = f"""
        Please extract ONLY the medical examination findings from the following form data.
        
        Raw extracted data:
        {raw_response}
        
        EXTRACT ONLY:
        1. CONFIDENTIAL MEDICAL EXAMINATION: Known to examiner, previously attended, unusual build/behavior, signs of tobacco/alcohol/drugs, smoking history
        2. MEASUREMENTS: Height, weight, chest measurements, waist, hips, weight variations
        3. RESPIRATORY SYSTEM: Abnormalities, signs of respiratory disease
        4. CIRCULATORY SYSTEM: Pulse, apex beat, blood pressure readings, cardiac findings, murmurs, peripheral abnormalities
        5. DIGESTIVE, ENDOCRINE AND LYMPH SYSTEMS: Hernia, lymph gland abnormalities
        6. GENITO-URINARY FINDINGS: Abnormalities, urine tests (protein, sugar, blood), pregnancy status
        7. NERVOUS SYSTEM: Vision defects, hearing/speech defects
        8. MUSCULOSKELETAL AND SKIN: Joint abnormalities, muscle/tissue abnormalities, back/neck issues, skin disorders
        
        Focus only on the physical examination findings and measurements.
        For boolean fields, use true/false.
        For numeric fields, extract the actual numbers.
        For text fields, extract the relevant details.
        """
        
        stage2_data = stage2_llm.invoke(stage2_prompt)
        
        if verbose:
            print("📝 Stage 3: Extracting summary and examiner details...")
        
        # Stage 3: Summary and examiner details
        stage3_llm = self.structured_chat_llm.with_structured_output(SummaryAndExaminerExtraction)
        stage3_prompt = f"""
        Please extract ONLY the summary and examiner information from the following form data.
        
        Raw extracted data:
        {raw_response}
        
        EXTRACT ONLY:
        1. SUMMARY: 
           - Whether medical attendant's reports are required
           - Whether surgery is likely to be required
           - Unfavorable features in personal/family history
           - Unfavorable findings from medical examination
        2. EXAMINER DETAILS:
           - Name, address, suburb, state, postcode
           - Phone number, qualifications
           - Whether signature is present
           - Date signed (in YYYY-MM-DD format)
        
        Focus only on the summary conclusions and examiner information.
        For boolean fields, use true/false.
        For dates, ensure they are in YYYY-MM-DD format.
        """
        
        stage3_data = stage3_llm.invoke(stage3_prompt)
        
        if verbose:
            print("🔧 Combining all stages into final MedicalReportData...")
        
        # Combine all stages into final MedicalReportData
        final_data = MedicalReportData(
            basic_info_and_history=stage1_data,
            medical_examination=stage2_data,
            summary_and_examiner=stage3_data
        )
        
        if verbose:
            print("✅ Successfully extracted data in 3 stages")
        
        return final_data
    
    def _extract_consent_form_single_stage(self, raw_response: str, verbose: bool = True) -> ConsentFormData:
        """
        Extract consent form data (single stage as it's simpler)
        
        :param raw_response: Raw response from vision LLM
        :param verbose: Whether to show progress messages
        :return: ConsentFormData object
        """
        structured_llm = self.structured_chat_llm.with_structured_output(ConsentFormData)
        conversion_prompt = f"""
        Please extract and structure the following consent form data.
        
        Raw extracted data:
        {raw_response}
        
        Please parse this information and return it in the structured format. 
        For any missing or unclear information, use empty strings or appropriate defaults.
        For dates, ensure they are in YYYY-MM-DD format.
        """
        
        structured_data = structured_llm.invoke(conversion_prompt)
        
        if verbose:
            print("✅ Successfully converted to ConsentFormData object")
        
        return structured_data
    
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
            raw_response = self.extract_form_data(image_b64_list, form_type, verbose)
            structured_data = self.extract_structured_data(raw_response, form_type, verbose)

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
    
    
    def process_file_test(self, file_path: str, form_type: str = "generic", verbose: bool = True) -> Dict[str, Any]:
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
            raw_response = self.extract_form_data(image_b64_list, form_type, verbose)

            total_time = time.time() - start_time
            
            # Create result wrapper with metadata and structured data
            if verbose:
                print("=" * 60)
                print(f"🎉 Successfully processed: {file_path}")
                print(f"⏱️  Total time: {total_time:.2f} seconds")
                print(f"📋 Form type: {form_type}")
                print(f"🏗️  Data model: {type(raw_response).__name__}")
            
            return raw_response.content
            
        except Exception as e:
            total_time = time.time() - start_time
            if verbose:
                print("=" * 60)
                print(f"❌ Unexpected error processing: {file_path}")
                print(f"⏱️  Time spent: {total_time:.2f} seconds")
                print(f"🔍 Error: {str(e)}")
            
            return str(e)
        
    