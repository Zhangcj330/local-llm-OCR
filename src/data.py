from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

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
    age_when_diagnosed: str = Field(description="Age when diagnosed", default="")
    age_at_death: str = Field(description="Age at death, if applicable", default="")
    details_of_investigation: str = Field(
        description="Details of any investigations performed on applicant due to family history",
        default=""
    ) 


class ConfidentialMedicalExamination(BaseModel):
    """Full data for confidential medical examination"""
    known_to_examiner: bool = Field(description="Whether the applicant is known to the examiner")
    previously_attended_examiner: bool = Field(description="Whether the applicant has previously attended the examiner")
    unusual_build_or_behavior: str = Field(description="Unusual build or behavior of the applicant")
    signs_of_tobacco_alcohol_or_drugs: str = Field(description="Signs of tobacco, alcohol or drugs use")
    ever_smoked: bool = Field(description="Whether the applicant has ever smoked")


class Measurements(BaseModel):
    height_cm: int = Field(description="Height in centimeters")
    weight_kg: int = Field(description="Weight in kilograms")
    chest_full_inspiration_cm: int = Field(description="Chest measurement at full inspiration")
    chest_full_expiration_cm: int = Field(description="Chest measurement at full expiration")
    waist_circumference_cm: int = Field(description="Waist circumference")
    hips_circumference_cm: int = Field(description="Hip circumference")
    recent_weight_variation: bool = Field(description="Has there been recent weight variation?")
    weight_variation_details: str = Field(description="Details about weight variation")
    chest_expansion_details: str = Field(description="Details about chest expansion")

    # Respiratory System
class RespiratorySystem(BaseModel):
    respiratory_abnormality: str = Field(description = "abnormality of the respiratory system to palpitation, percussion or auscultation")
    respiratory_fabnormality_details: str = Field(description = "details of the abnormality")
    respiratory_sign: str = Field(description = "sign of past or present respiratory disease")
    respiratory_sign_details: str = Field(description = "details of the sign")
    
class CirculatorySystem(BaseModel):
    pulse_rate_and_character: str = Field(description="pulse rate and character")
    apex_beat_position: str = Field(description="position of the apex beat")
    apex_interspace: str = Field(description="interspace between the apex beat and the midsternal border")
    apex_distance_from_midsternal: float = Field(description="distance from the apex beat to the midsternal border")
    cardiac_enlargement: bool = Field(description="whether there is cardiac enlargement")
    cardiac_enlargement_details: str = Field(description="details of the cardiac enlargement")
    abnormal_heart_sounds_or_rhythm: bool = Field(description="whether there is abnormal heart sounds or rhythm")
    abnormal_heart_sounds_or_rhythm_details: str = Field(description="details of the abnormal heart sounds or rhythm")
    murmurs: bool = Field(description="whether there is murmurs")
    murmurs_details: str = Field(description="details of the murmurs")
    bp_Systolic_1: int = Field(description="systolic blood pressure")
    bp_Diastolic_1: int = Field(description="diastolic blood pressure")
    bp_Systolic_2: int = Field(description="systolic blood pressure")
    bp_Diastolic_2: int = Field(description="diastolic blood pressure")
    bp_Systolic_3: int = Field(description="systolic blood pressure")
    bp_Diastolic_3: int = Field(description="diastolic blood pressure")
    peripheral_abnormalities: bool = Field(description="whether there is peripheral abnormalities")
    peripheral_abnormalities_details: str = Field(description="details of the peripheral abnormalities")
    heart_and_vascular_system_abnormal: bool = Field(description="whether there is heart and vascular system abnormalities")
    heart_and_vascular_system_abnormal_details: str = Field(description="details of the heart and vascular system abnormalities")
    on_treatment_for_hypertension: bool = Field(description="whether the applicant is on treatment for hypertension")
    hypertension_pretreatment_bp: str = Field(description="pretreatment blood pressure")
    hypertension_duration: str = Field(description="duration of hypertension")
    hypertension_treatment_nature: str = Field(description="nature of hypertension treatment")

    
# DIGESTIVE, ENDOCRINE AND LYMPH SYSTEMS
class DigestiveEndocrineLymphFindings(BaseModel):
    hernia_present: bool = Field(description="Whether a hernia is present")
    hernia_details: str = Field(description="Details if hernia is present")
    lymph_gland_abnormality: bool = Field(description="Whether there is lymph gland abnormality in neck, axillae, or inguinal regions")
    lymph_gland_abnormality_details: str = Field(description="Details if lymph gland abnormality is present")

class GenitoUrinaryFindings(BaseModel):
    genito_urinary_abnormality: bool = Field(description="Whether any genito-urinary abnormality is present (e.g. stricture, prostate)")
    genito_urinary_abnormality_details: str = Field(description="Details if genito-urinary abnormality is present")
    
    urine_protein: bool = Field(description="Whether urine contains protein (albumin)")
    urine_sugar: bool = Field(description="Whether urine contains sugar")
    urine_blood: bool = Field(description="Whether urine contains blood")
    urine_blood_menstruating: bool = Field(description="Whether blood in urine is due to menstruation (if applicable)")
    urine_other_abnormalities: bool = Field(description="Whether urine contains other abnormalities")
    urine_other_abnormalities_details: str = Field(description="Details of other abnormalities in urine if present")
    
    is_pregnant: bool = Field(description="Whether the applicant is pregnant (female applicants only)")
    expected_delivery_date: str = Field(description="Expected delivery date if pregnant (DD/MM/YYYY)")


class NervousSystemFindings(BaseModel):
    vision_defect_or_eye_abnormality: bool = Field(description="Whether there is any defect of vision or abnormality of the eyes")
    vision_defect_or_eye_abnormality_details: str = Field(description="Details if there is any defect of vision or abnormality of the eyes")
    
    hearing_or_speech_defect: bool = Field(description="Whether there is any defect in hearing or speech")
    hearing_or_speech_defect_details: str = Field(description="Details if there is any defect in hearing or speech")
    

class MusculoskeletalAndSkinFindings(BaseModel):
    joint_abnormality: bool = Field(description="Whether there is any abnormality of the form or function of the joints")
    joint_abnormality_details: str = Field(description="Details if there is abnormality of the joints")
    
    muscle_or_connective_tissue_abnormality: bool = Field(description="Whether there is any abnormality of the form or function of the muscles or connective tissues")
    muscle_or_connective_tissue_abnormality_details: str = Field(description="Details if there is abnormality of the muscles or connective tissues")
    
    back_or_neck_abnormality: bool = Field(description="Whether there is any abnormality of the form or function of the back or neck including cervical and lumbar spine")
    back_or_neck_abnormality_details: str = Field(description="Details if there is abnormality of the back or neck")
    
    skin_disorder: bool = Field(description="Whether there is any evidence of disorder of the skin")
    skin_disorder_details: str = Field(description="Details if there is any disorder of the skin")


class Summary(BaseModel):
    medical_attendants_reports_required: bool = Field(description="Whether any medical attendant's reports or special tests are required")
    medical_attendants_reports_details: str = Field(description="Details if medical attendant's reports or special tests are required")
    
    likely_to_require_surgery: bool = Field(description="Whether the person examined is likely to require any surgical operation")
    likely_to_require_surgery_details: str = Field(description="Details if surgery is likely to be required")
    
    unfavourable_history_personal_or_family: str = Field(description="Any unfavourable features in personal or family medical history which could reduce life expectancy or cause disablement")
    unfavourable_findings_medical_exam: str = Field(description="Any unfavourable features disclosed by medical examination which could reduce life expectancy or cause disablement")

class ExaminerDetails(BaseModel):
    name: str = Field(description="Full name of the examiner")
    address: str = Field(description="Street address of the examiner")
    suburb: str = Field(description="Suburb of the examiner's address")
    state: str = Field(description="State of the examiner's address")
    postcode: str = Field(description="Postcode of the examiner's address")
    phone: str = Field(description="Phone number of the examiner")
    personal_qualifications: str = Field(description="Personal qualifications of the examiner")
    signature_present: bool = Field(description="Whether the examiner's signature is present")
    date_signed: str = Field(description="Date the form was signed by the examiner (DD/MM/YYYY)")


class BasicInfoExtraction(BaseModel):
    """Structured data for basic information"""
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


# Intermediate models for staged extraction
class BasicInfoAndHistoryExtraction(BaseModel):
    """First stage: Basic info and history data"""
    basic_info: BasicInfoExtraction = Field(default_factory=BasicInfoExtraction)
    medical_history: List[MedicalHistoryItem] = Field(default_factory=list)
    medical_history_details: str = Field(description="General details for questions 1-27 if any answered yes", default="")
    family_history_conditions: List[FamilyHistoryCondition] = Field(default_factory=list)
    family_history_details: List[FamilyHistoryDetails] = Field(default_factory=list)

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


class MedicalExaminationExtraction(BaseModel):
    """Second stage: Medical examination findings"""
    confidential_medical_examination: ConfidentialMedicalExamination = Field(default_factory=ConfidentialMedicalExamination)
    measurements: Measurements = Field(default_factory=Measurements)
    respiratory_system: RespiratorySystem = Field(default_factory=RespiratorySystem)
    circulatory_system: CirculatorySystem = Field(default_factory=CirculatorySystem)
    digestive_endocrine_lymph_findings: DigestiveEndocrineLymphFindings = Field(default_factory=DigestiveEndocrineLymphFindings)
    genito_urinary_findings: GenitoUrinaryFindings = Field(default_factory=GenitoUrinaryFindings)
    nervous_system_findings: NervousSystemFindings = Field(default_factory=NervousSystemFindings)
    musculoskeletal_and_skin_findings: MusculoskeletalAndSkinFindings = Field(default_factory=MusculoskeletalAndSkinFindings)


class SummaryAndExaminerExtraction(BaseModel):
    """Third stage: Summary and examiner details"""
    summary: Summary = Field(default_factory=Summary)
    examiner_details: ExaminerDetails = Field(default_factory=ExaminerDetails)


class MedicalReportData(BaseModel):
    """Structured data for entire TAL Medical Examiner's report"""

    basic_info_and_history: BasicInfoAndHistoryExtraction = Field(default_factory=BasicInfoAndHistoryExtraction)
    medical_examination: MedicalExaminationExtraction = Field(default_factory=MedicalExaminationExtraction)
    summary_and_examiner: SummaryAndExaminerExtraction = Field(default_factory=SummaryAndExaminerExtraction)

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize nested structures if needed
        # The initialization is handled by the nested models themselves
        pass
    
    # Convenience properties for backward compatibility
    @property
    def basic_info(self) -> BasicInfoExtraction:
        """Get basic info for backward compatibility"""
        return self.basic_info_and_history.basic_info
    
    @property
    def medical_history(self) -> List[MedicalHistoryItem]:
        """Get medical history for backward compatibility"""
        return self.basic_info_and_history.medical_history
    
    @property
    def family_history_conditions(self) -> List[FamilyHistoryCondition]:
        """Get family history conditions for backward compatibility"""
        return self.basic_info_and_history.family_history_conditions
    
    @property
    def reference_number(self) -> str:
        """Get reference number for backward compatibility"""
        return self.basic_info_and_history.basic_info.reference_number

    
    def to_csv_records(self) -> List[Dict[str, Any]]:
        """Convert to CSV-compatible records matching the database structure"""
        records = []
        
        # Add basic info records
        basic_fields = [
            ("reference number", "reference_number", self.basic_info_and_history.basic_info.reference_number),
            ("name of life to be insured", "name_of_life_to_be_insured", self.basic_info_and_history.basic_info.name_of_life_to_be_insured),
            ("Address", "address", self.basic_info_and_history.basic_info.address),
            ("Suburb", "suburb", self.basic_info_and_history.basic_info.suburb),
            ("State", "state", self.basic_info_and_history.basic_info.state),
            ("Postcode", "postcode", self.basic_info_and_history.basic_info.postcode),
            ("Date of birth", "date_of_birth", self.basic_info_and_history.basic_info.date_of_birth),
            ("Occupation", "occupation", self.basic_info_and_history.basic_info.occupation),

            ("Licence number", "licence_number", self.basic_info_and_history.basic_info.licence_number),
            ("Passport number", "passport_number", self.basic_info_and_history.basic_info.passport_number),
            ("Other ID description", "other_id_description", self.basic_info_and_history.basic_info.other_id_description),
            ("Other ID number", "other_id_number", self.basic_info_and_history.basic_info.other_id_number),
            ("Witness signature date", "witness_signature_date", self.basic_info_and_history.basic_info.witness_signature_date),
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
        for item in self.basic_info_and_history.medical_history:
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
        for condition in self.basic_info_and_history.family_history_conditions:
            records.append({
                "label": condition.question,
                "Field name": f"yn {condition.id}",
                "db_column": condition.db_column,
                "field_value": condition.status,
                "section_number": 7,
                "section_name": "FAMILY HISTORY",
                "type": "checkbox"
            })
        
        # Add medical history details
        if self.basic_info_and_history.medical_history_details:
            records.append({
                "label": "Please provide details if any questions 1-27 answered yes",
                "Field name": "27 details",
                "db_column": "details_questions_127_answered_yes",
                "field_value": self.basic_info_and_history.medical_history_details,
                "section_number": 6,
                "section_name": "INFORMATION TO BE OBTAINED FROM APPLICANT",
                "type": "text"
            })

        # add confidential_medical_examination
        for key, value in self.medical_examination.confidential_medical_examination.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 8,
                "section_name": "CONFIDENTIAL MEDICAL EXAMINATION",
                "type": "text"
            })

        # add measurements
        for key, value in self.medical_examination.measurements.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 9,
                "section_name": "MEASUREMENTS",
                "type": "text"
            })

        # add respiratory_system
        for key, value in self.medical_examination.respiratory_system.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 10,
                "section_name": "RESPIRATORY SYSTEM",
                "type": "text"
            })  

        # add circulatory_system
        for key, value in self.medical_examination.circulatory_system.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,   
                "section_number": 11,
                "section_name": "CIRCULATORY SYSTEM",
                "type": "text"
            })

        # add digestive_endocrine_lymph_findings            
        for key, value in self.medical_examination.digestive_endocrine_lymph_findings.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 12,
                "section_name": "DIGESTIVE, ENDOCRINE AND LYMPH SYSTEMS",
                "type": "text"
            })

        # add genito_urinary_findings
        for key, value in self.medical_examination.genito_urinary_findings.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 13,
                "section_name": "GENITO-URINARY FINDINGS",
                "type": "text"
            })

        # add nervous_system_findings
        for key, value in self.medical_examination.nervous_system_findings.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 14,
                "section_name": "NEUROLOGICAL SYSTEM",
                "type": "text"
            })

        # add musculoskeletal_and_skin_findings
        for key, value in self.medical_examination.musculoskeletal_and_skin_findings.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 15,
                "section_name": "MUSCULOSKELETAL AND SKIN FINDINGS",
                "type": "text"
            })

        # add summary
        for key, value in self.summary_and_examiner.summary.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 16,
                "section_name": "SUMMARY",
                "type": "text"
            })  

        # add examiner_details
        for key, value in self.summary_and_examiner.examiner_details.dict().items():
            records.append({
                "label": key,
                "Field name": key,
                "db_column": key,
                "field_value": value,
                "section_number": 17,
                "section_name": "EXAMINER DETAILS",
                "type": "text"
            })

        return records

    def print_reference_number(self):
        print(self.reference_number)
        return self.reference_number


class ConsentFormData(BaseModel):
    """Structured data for consent form"""
    reference_number: str = Field(description="Reference number", default="")
    life_to_be_insured_name: str = Field(description="Name of person to be insured", default="")
    life_to_be_insured_dob: str = Field(description="Date of birth in YYYY-MM-DD format", default="")
    authority1_name: str = Field(description="First authority name", default="")
    authority1_signature_date: str = Field(description="First authority signature date", default="")
    authority2_name: str = Field(description="Second authority name", default="")
    authority2_signature_date: str = Field(description="Second authority signature date", default="")
