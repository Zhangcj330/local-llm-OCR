from typing import Dict, List, Any, Optional
import time
from datetime import datetime
from langchain_ollama import OllamaLLM, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .image_processor import ImageProcessor

# Add Pydantic imports for structured output
from pydantic import BaseModel, Field


# Medical History Questions Configuration
MEDICAL_HISTORY_QUESTIONS = [
    {
        "id": 1,
        "question": "Any disease, disorder or condition relating to the heart and circulatory system including high blood pressure, raised cholesterol, heart murmur, stroke, brain haemorrhage, or embolism, chest pain or palpitations?",
        "field_name": "disease_disorder_condition_relating_heart_circulatory",
        "db_column": "disease_disorder_condition_relating_heart_circulatory"
    },
    {
        "id": 2,
        "question": "Diabetes or raised blood sugar levels?",
        "field_name": "diabetes_raised_blood_sugar_levels",
        "db_column": "diabetes_raised_blood_sugar_levels"
    },
    {
        "id": 3,
        "question": "Any disorder of the kidney, bladder or genitourinary system including prostate disorders, urinary tract infections, kidney stones, blood or protein in the urine?",
        "field_name": "disorder_kidney_bladder_genitourinary_system_prostate",
        "db_column": "disorder_kidney_bladder_genitourinary_system_prostate"
    },
    {
        "id": 4,
        "question": "Any disorder of the digestive system, liver, oesophagus, stomach, gall bladder, pancreas or bowel including reflux, hernia, ulcers, haemochromatosis, colitis or Crohn's disease?",
        "field_name": "disorder_digestive_system_liver_oesophagus_stomach",
        "db_column": "disorder_digestive_system_liver_oesophagus_stomach"
    },
    {
        "id": 5,
        "question": "Any cancer, leukaemia or tumour, lump, cyst or growth either malignant or benign (non-malignant)?",
        "field_name": "cancer_leukaemia_tumour_lump_cyst_growth",
        "db_column": "cancer_leukaemia_tumour_lump_cyst_growth"
    },
    {
        "id": 6,
        "question": "Asthma, sleep apnoea, or any other respiratory, lung or breathing disorder?",
        "field_name": "asthma_sleep_apnoea_respiratory_lung_breathing",
        "db_column": "asthma_sleep_apnoea_respiratory_lung_breathing"
    },
    {
        "id": 7,
        "question": "Head injury, epilepsy, fits, convulsions or chronic headaches?",
        "field_name": "head_injury_epilepsy_fits_convulsions_chronic",
        "db_column": "head_injury_epilepsy_fits_convulsions_chronic"
    },
    {
        "id": 8,
        "question": "Numbness, tingling, altered sensation, tremor, fainting attacks, problems with balance or co-ordination, or any form of paralysis or multiple sclerosis?",
        "field_name": "numbness_tingling_altered_sensation_tremor_fainting",
        "db_column": "numbness_tingling_altered_sensation_tremor_fainting"
    },
    {
        "id": 9,
        "question": "Any disorder of the eyes or ears, including blindness, blurred or double vision (other than sight problems corrected by glasses or contact lenses) or impaired hearing or tinnitus?",
        "field_name": "disorder_eyes_ears_blindness_blurred_double",
        "db_column": "disorder_eyes_ears_blindness_blurred_double"
    },
    {
        "id": 10,
        "question": "Eczema, dermatitis, psoriasis or any other skin condition?",
        "field_name": "eczema_dermatitis_psoriasis_skin_condition",
        "db_column": "eczema_dermatitis_psoriasis_skin_condition"
    },
    {
        "id": 11,
        "question": "Back or neck pain including muscular pain, strain, whiplash and sciatica?",
        "field_name": "back_neck_pain_muscular_pain_strain",
        "db_column": "back_neck_pain_muscular_pain_strain"
    },
    {
        "id": 12,
        "question": "Any joint (eg wrist, elbow, shoulder, ankle, knee, hip), bone or muscle pain or disorder including RSI?",
        "field_name": "joint_eg_wrist_elbow_shoulder_ankle",
        "db_column": "joint_eg_wrist_elbow_shoulder_ankle"
    },
    {
        "id": 13,
        "question": "Rheumatoid arthritis, other forms of arthritis, osteoporosis or gout?",
        "field_name": "rheumatoid_arthritis_forms_arthritis_osteoporosis_gout",
        "db_column": "rheumatoid_arthritis_forms_arthritis_osteoporosis_gout"
    },
    {
        "id": 14,
        "question": "Any blood disorder including anaemia?",
        "field_name": "blood_disorder_anaemia",
        "db_column": "blood_disorder_anaemia"
    },
    {
        "id": 15,
        "question": "Any thyroid disorder or lupus?",
        "field_name": "thyroid_disorder_lupus",
        "db_column": "thyroid_disorder_lupus"
    },
    {
        "id": 16,
        "question": "Depression, anxiety, panic attacks, stress, psychosis, schizophrenia, bipolar disorder, chronic fatigue, post natal depression or any other mental or nervous condition?",
        "field_name": "depression_anxiety_panic_attacks_stress_psychosis",
        "db_column": "depression_anxiety_panic_attacks_stress_psychosis"
    },
    {
        "id": 17,
        "question": "Any disorder of the cervix (including abnormal Pap smear), ovary, uterus, breast or endometrium, or are you currently pregnant?",
        "field_name": "disorder_cervix_abnormal_pap_smear_ovary",
        "db_column": "disorder_cervix_abnormal_pap_smear_ovary"
    },
    {
        "id": 18,
        "question": "Any complications of pregnancy or childbirth or a child with congenital abnormalities?",
        "field_name": "complications_pregnancy_childbirth_child_congenital_abnormalities",
        "db_column": "complications_pregnancy_childbirth_child_congenital_abnormalities"
    },
    {
        "id": 19,
        "question": "Have you ever injected, smoked or otherwise taken recreational or non-prescription drugs, taken any drug other than as medically directed or received advice and/or counselling for excess alcohol consumption from any health professional?",
        "field_name": "injected_smoked_otherwise_taken_recreational_nonprescription",
        "db_column": "injected_smoked_otherwise_taken_recreational_nonprescription"
    },
    {
        "id": 20,
        "question": "Have you ever tested positive for HIV/AIDS, Hepatitis B or C, or are you awaiting the results of such a test (other than for this application)?",
        "field_name": "tested_positive_hivaids_hepatitis_b_c",
        "db_column": "tested_positive_hivaids_hepatitis_b_c"
    },
    {
        "id": 21,
        "question": "In the last 5 years have you engaged in any activity reasonably expected to having an increased risk or exposure to the HIV/AIDS virus? (This includes unprotected anal sex, sex with a sex worker or sex with someone you know, or suspect to be HIV positive).",
        "field_name": "5_engaged_activity_reasonably_expected_having",
        "db_column": "5_engaged_activity_reasonably_expected_having"
    },
    {
        "id": 22,
        "question": "Have you in the last five years been absent from work or your usual duties for a period of more than five days through any illness or injury not previously disclosed in this application?",
        "field_name": "absent_work_period_days_illness_injury",
        "db_column": "absent_work_period_days_illness_injury"
    },
    {
        "id": 23,
        "question": "Apart from any condition already disclosed, do you have any symptoms of illness, any physical defect, or any condition for which you receive medical advice or treatment?",
        "field_name": "apart_condition_already_symptoms_illness_physical",
        "db_column": "apart_condition_already_symptoms_illness_physical"
    },
    {
        "id": 24,
        "question": "Apart from treating any condition already disclosed, have you in the last two years had medication prescribed (except contraceptives or antibiotics)?",
        "field_name": "apart_treating_condition_already_two_had",
        "db_column": "apart_treating_condition_already_two_had"
    },
    {
        "id": 25,
        "question": "Apart from investigating any condition already disclosed, have you had any medical test (eg ECG, colonoscopy, endoscopy, gastroscopy or ultrasound)?",
        "field_name": "apart_investigating_condition_already_had_medical",
        "db_column": "apart_investigating_condition_already_had_medical"
    },
    {
        "id": 26,
        "question": "Apart from investigating any condition already disclosed, have you ever had a genetic test where you received (or are currently awaiting) an individual result or are you considering having a genetic test (excluding genetic screening of a child during pregnancy)?",
        "field_name": "apart_investigating_condition_already_had_genetic",
        "db_column": "apart_investigating_condition_already_had_genetic"
    },
    {
        "id": 27,
        "question": "Apart from any condition already disclosed, do you plan to seek or are you awaiting medical advice, investigation or treatment for any other current health condition or symptoms?",
        "field_name": "apart_condition_already_plan_seek_awaiting",
        "db_column": "apart_condition_already_plan_seek_awaiting"
    }
]

# Family History Questions Configuration
FAMILY_HISTORY_QUESTIONS = [
    {
        "id": 1,
        "question": "Heart disease (eg angina or heart attack) or stroke",
        "field_name": "heart_disease_eg_angina_heart_attack",
        "db_column": "heart_disease_eg_angina_heart_attack"
    },
    {
        "id": 2,
        "question": "Cardiomyopathy",
        "field_name": "cardiomyopathy",
        "db_column": "cardiomyopathy"
    },
    {
        "id": 3,
        "question": "Breast, cervical and/or ovarian cancer",
        "field_name": "breast_cervical_andor_ovarian_cancer",
        "db_column": "breast_cervical_andor_ovarian_cancer"
    },
    {
        "id": 4,
        "question": "Bowel cancer or polyposis of the colon",
        "field_name": "bowel_cancer_polyposis_colon",
        "db_column": "bowel_cancer_polyposis_colon"
    },
    {
        "id": 5,
        "question": "Any other type of cancer",
        "field_name": "type_cancer",
        "db_column": "type_cancer"
    },
    {
        "id": 6,
        "question": "Diabetes",
        "field_name": "diabetes",
        "db_column": "diabetes"
    },
    {
        "id": 7,
        "question": "Alzheimer's disease",
        "field_name": "alzheimers_disease",
        "db_column": "alzheimers_disease"
    },
    {
        "id": 8,
        "question": "Multiple sclerosis",
        "field_name": "multiple_sclerosis",
        "db_column": "multiple_sclerosis"
    },
    {
        "id": 9,
        "question": "Motor neurone disease, Parkinson's disease, Polycystic kidney disease and/or Huntington's disease, mental illness and/or any other hereditary disorder (not previously listed in this section).",
        "field_name": "motor_neurone_disease_parkinsons_disease_polycystic",
        "db_column": "motor_neurone_disease_parkinsons_disease_polycystic"
    }
]


class MedicalHistoryItem(BaseModel):
    """Individual medical history question item with predefined questions"""
    id: int = Field(description="Predefined question ID")
    question: str = Field(description="Predefined medical question text")
    field_name: str = Field(description="Database field name")
    db_column: str = Field(description="Database column name")
    status: str = Field(description="Yes/No/Y/N answer extracted from form", default="")
    details: str = Field(description="Additional details if status is Yes", default="")
    
    @classmethod
    def from_config(cls, config_item: dict, status: str = "", details: str = ""):
        """Create MedicalHistoryItem from configuration with extracted values"""
        return cls(
            id=config_item["id"],
            question=config_item["question"],
            field_name=config_item["field_name"],
            db_column=config_item["db_column"],
            status=status,
            details=details
        )


class FamilyHistoryCondition(BaseModel):
    """Family history condition with predefined questions"""
    id: int = Field(description="Predefined condition ID")
    question: str = Field(description="Predefined family history question")
    field_name: str = Field(description="Database field name")
    db_column: str = Field(description="Database column name")
    status: str = Field(description="Yes/No/Y/N answer extracted from form", default="")
    
    @classmethod
    def from_config(cls, config_item: dict, status: str = ""):
        """Create FamilyHistoryCondition from configuration with extracted values"""
        return cls(
            id=config_item["id"],
            question=config_item["question"],
            field_name=config_item["field_name"],
            db_column=config_item["db_column"],
            status=status
        )


class FamilyHistoryDetails(BaseModel):
    """Detailed family history information for positive cases"""
    relationship: str = Field(description="Family relationship", default="")
    medical_condition: str = Field(description="Medical condition", default="")
    age_when_diagnosed: Optional[str] = Field(description="Age when diagnosed", default="")
    age_at_death: Optional[str] = Field(description="Age at death, if applicable", default="")
    details_of_investigation: Optional[str] = Field(
        description="Details of any investigations performed on applicant due to family history",
        default=""
    )


class BPReading(BaseModel):
    """Single blood pressure reading"""
    systolic: Optional[int] = Field(description="Systolic BP mmHg", default=None)
    diastolic: Optional[int] = Field(description="Diastolic BP mmHg", default=None)


class MeasurementsData(BaseModel):
    """Physical measurements and weight variation"""
    height_cm: Optional[float] = Field(description="Height in centimeters", default=None)
    weight_kg: Optional[float] = Field(description="Weight in kilograms", default=None)
    chest_full_inspiration_cm: Optional[float] = Field(description="Chest measurement at full inspiration", default=None)
    chest_full_expiration_cm: Optional[float] = Field(description="Chest measurement at full expiration", default=None)
    waist_circumference_cm: Optional[float] = Field(description="Waist circumference", default=None)
    hips_circumference_cm: Optional[float] = Field(description="Hip circumference", default=None)
    recent_weight_variation: Optional[bool] = Field(description="Has there been recent weight variation?", default=None)
    weight_variation_details: Optional[str] = Field(description="Details about weight variation", default=None)
    chest_expansion_details: Optional[str] = Field(description="Details about chest expansion", default=None)

class CirculatorySystem(BaseModel):
    pulse_rate_and_character: Optional[str] = Field(default=None)
    apex_beat_position: Optional[str] = Field(default=None)
    apex_interspace: Optional[str] = Field(default=None)
    apex_distance_from_midsternal: Optional[str] = Field(default=None)
    cardiac_enlargement: Optional[str] = Field(default=None)
    abnormal_heart_sounds_or_rhythm: Optional[str] = Field(default=None)
    murmurs: Optional[str] = Field(default=None)
    bp_readings: List[BPReading] = Field(default_factory=list)
    peripheral_abnormalities: Optional[str] = Field(default=None)
    heart_and_vascular_system_abnormal: Optional[str] = Field(default=None)
    on_treatment_for_hypertension: Optional[bool] = Field(default=None)
    hypertension_pretreatment_bp: Optional[str] = Field(default=None)
    hypertension_duration: Optional[str] = Field(default=None)
    hypertension_treatment_nature: Optional[str] = Field(default=None)


class ExaminationSection(BaseModel):
    """Captures any 'Yes/No + details' section"""
    question: str
    answer: Optional[bool] = None
    details: Optional[str] = None


class MedicalExamData(BaseModel):
    """Full data for medical examiner's findings"""
    known_to_examiner: Optional[bool] = None
    previously_attended_examiner: Optional[bool] = None
    unusual_build_or_behavior: Optional[str] = None
    signs_of_tobacco_alcohol_or_drugs: Optional[str] = None
    ever_smoked: Optional[bool] = None

    measurements: MeasurementsData = Field(default_factory=MeasurementsData)

    respiratory_findings: List[ExaminationSection] = Field(default_factory=list)
    circulatory_system: CirculatorySystem = Field(default_factory=CirculatorySystem)
    digestive_endocrine_lymph_findings: List[ExaminationSection] = Field(default_factory=list)
    genito_urinary_findings: List[ExaminationSection] = Field(default_factory=list)
    nervous_system_findings: List[ExaminationSection] = Field(default_factory=list)
    musculoskeletal_and_skin_findings: List[ExaminationSection] = Field(default_factory=list)

    summary_additional_tests_needed: Optional[str] = None
    summary_surgical_op_required: Optional[str] = None
    summary_unfavourable_features_personal_family_history: Optional[str] = None
    summary_unfavourable_features_exam: Optional[str] = None


class ExaminerDetails(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    suburb: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    phone: Optional[str] = None
    qualifications: Optional[str] = None
    signature_date: Optional[str] = None


class MedicalReportData(BaseModel):
    """Structured data for entire TAL Medical Examiner's report"""
    # Basic information
    reference_number: str = Field(default="")
    name_of_life_to_be_insured: str = Field(default="")
    date_of_birth: str = Field(default="")
    address: str = Field(default="")
    suburb: str = Field(default="")
    state: str = Field(default="")
    postcode: str = Field(default="")
    occupation: str = Field(default="")
    licence_number: str = Field(default="")
    passport_number: str = Field(default="")
    other_id_description: str = Field(default="")
    other_id_number: str = Field(default="")
    signature_of_life_to_be_insured_date: str = Field(default="")
    witness_signature_date: str = Field(default="")
    
    # Medical history with predefined questions
    medical_history: List[MedicalHistoryItem] = Field(default_factory=list)
    medical_history_details: str = Field(description="General details for questions 1-27 if any answered yes", default="")
    
    # Family history
    family_history_conditions: List[FamilyHistoryCondition] = Field(default_factory=list)
    family_history_details: List[FamilyHistoryDetails] = Field(default_factory=list)
    
    # Medical examination data
    medical_exam_data: MedicalExamData = Field(default_factory=MedicalExamData)
    
    # Examiner details
    examiner_details: ExaminerDetails = Field(default_factory=ExaminerDetails)

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize medical history with predefined questions if not provided
        if not self.medical_history:
            self.medical_history = [
                MedicalHistoryItem.from_config(config) for config in MEDICAL_HISTORY_QUESTIONS
            ]
        
        # Initialize family history conditions with predefined questions if not provided
        if not self.family_history_conditions:
            self.family_history_conditions = [
                FamilyHistoryCondition.from_config(config) for config in FAMILY_HISTORY_QUESTIONS
            ]

    
    def to_csv_records(self) -> List[Dict[str, Any]]:
        """Convert to CSV-compatible records matching the database structure"""
        records = []
        
        # Add basic info records
        basic_fields = [
            ("reference number", "reference_number", self.reference_number),
            ("Life to be insured", "life_be_insured", self.name_of_life_to_be_insured),
            ("Address", "address", self.address),
            ("Suburb", "suburb", self.suburb),
            ("State", "state", self.state),
            ("Postcode", "postcode", self.postcode),
            ("Occupation", "occupation", self.occupation),
        ]
        
        for label, db_column, value in basic_fields:
            records.append({
                "label": label,
                "Field name": db_column,
                "db_column": db_column,
                "field_value": value,
                "section_number": 0 if label == "reference number" else 4,
                "section_name": "Top" if label == "reference number" else "POLICY DETAILS",
                "type": "text"
            })
        
        # Add medical history records
        for item in self.medical_history:
            records.append({
                "label": item.question,
                "Field name": f"yn {item.id}",
                "db_column": item.db_column,
                "field_value": item.status,
                "section_number": 6,
                "section_name": "INFORMATION TO BE OBTAINED FROM APPLICANT",
                "type": "checkbox"
            })
        
        # Add family history records
        for condition in self.family_history_conditions:
            records.append({
                "label": condition.question,
                "Field name": f"yn {condition.id}",
                "db_column": condition.db_column,
                "field_value": condition.status,
                "section_number": 7,
                "section_name": "FAMILY HISTORY",
                "type": "checkbox"
            })
        
        return records

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
            
            # Create HumanMessage for Gemini
            for b64 in list_image_b64:
                content_blocks.append({
                    "type": "image_url", 
                    "image_url": f"data:image/png;base64,{b64}"
                })

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
            return base_prompt + f"""
            
            Please extract the information according to this structure:
            
            BASIC INFORMATION:
            - Reference number, name, date of birth, address, occupation, ID numbers
            - Signature dates
            
            MEDICAL HISTORY (Questions 1-27):
            For each of the 27 predefined medical history questions, extract:
            - Status: "Y", "N", "Yes", "No", or "" if not found
            - Details: Any additional text provided if status is Yes
            
            The 27 questions are:
            {[f"{q['id']}. {q['question']}" for q in MEDICAL_HISTORY_QUESTIONS]}
            
            FAMILY HISTORY:
            For each family history condition, extract:
            - Status: "Y", "N", "Yes", "No", or "" if not found
            
            The family history conditions are:
            {[f"{q['id']}. {q['question']}" for q in FAMILY_HISTORY_QUESTIONS]}
            
            For positive family history, also extract detailed information:
            - Relationship (father, mother, brother, sister)
            - Medical condition
            - Age when diagnosed
            - Age at death (if applicable)
            
            MEASUREMENTS AND EXAMINATION:
            - Height, weight, chest measurements, waist, hips
            - Blood pressure readings
            - Any examination findings
            
            EXAMINER DETAILS:
            - Name, address, qualifications, signature date
            
            Return the extracted information in a structured format that matches the predefined question IDs and field names.
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
            
            # Create enhanced prompt for structured conversion
            if form_type == "medical_report":
                conversion_prompt = f"""
                Please extract and structure the following form data into the MedicalReportData format.
                
                Raw extracted data:
                {raw_response}
                
                IMPORTANT INSTRUCTIONS:
                1. For medical_history: Extract the status (Y/N/Yes/No) and details for each of the 27 predefined questions
                2. For family_history_conditions: Extract the status (Y/N/Yes/No) for each of the 9 predefined conditions
                3. For family_history_details: Extract detailed family member information (relationship, condition, ages)
                4. For dates, ensure they are in YYYY-MM-DD format
                5. For yes/no answers, use "Y", "N", "Yes", "No", or "" if unclear
                6. Match the question text to the correct predefined question ID
                7. The predefined questions are already set up in the model - just extract the status and details
                
                The system will automatically initialize all 27 medical history questions and 9 family history conditions.
                You only need to provide the extracted status and details for each question.
                """
            else:
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

def medical_report_to_dataframe(report: MedicalReportData) -> 'pd.DataFrame':
    """
    Convert MedicalReportData to pandas DataFrame
    
    :param report: MedicalReportData instance
    :return: pandas DataFrame with CSV-compatible structure
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for DataFrame conversion. Install with: pip install pandas")
    
    csv_records = report.to_csv_records()
    df = pd.DataFrame(csv_records)
    return df


def create_empty_medical_report():
    """
    Create an empty medical report with all predefined questions
    """
    return MedicalReportData()
   