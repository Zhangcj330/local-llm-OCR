from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from .image_processor import ImageProcessor
from .data import (
    Page0Data, Page1Data, Page2Data, Page3Data, Page4Data, 
    Page5Data, Page6Data, Page7Data, Page8Data, 
    PageBasedMedicalReportData, MEDICAL_HISTORY_QUESTIONS, FAMILY_HISTORY_QUESTIONS
)


class PageProcessor:
    """Process medical forms page by page using ChatOllama with structured output"""
    
    def __init__(self, model_name: str = "llama3.2-vision:latest", base_url: Optional[str] = None, config_path: str = "src/config.json"):
        """
        Initialize the page processor
        
        :param model_name: Name of the Ollama model to use
        :param base_url: Optional base URL for Ollama service
        :param config_path: Path to the config.json file
        """
        self.model_name = model_name
        self.base_url = base_url
        self.image_processor = ImageProcessor()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize the base LLM
        self.llm = ChatOllama(model=model_name, base_url=base_url)
        
        # Create structured output versions for each page
        self.page_processors = {
            0: self.llm.with_structured_output(Page0Data),
            1: self.llm.with_structured_output(Page1Data),
            2: self.llm.with_structured_output(Page2Data),
            3: self.llm.with_structured_output(Page3Data),
            4: self.llm.with_structured_output(Page4Data),
            5: self.llm.with_structured_output(Page5Data),
            6: self.llm.with_structured_output(Page6Data),
            7: self.llm.with_structured_output(Page7Data),
            8: self.llm.with_structured_output(Page8Data),
        }
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        :param config_path: Path to config.json
        :return: Configuration dictionary
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            return {"pages": []}
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing config file: {e}")
            return {"pages": []}
    
    def process_page(self, page_number: int, image_b64: str, verbose: bool = True) -> Any:
        """
        Process a single page and return structured data
        
        :param page_number: Page number (0-8)
        :param image_b64: Base64 encoded image
        :param verbose: Whether to show progress messages
        :return: Structured PageData object
        """
        if page_number not in self.page_processors:
            raise ValueError(f"Page number {page_number} not supported. Must be 0-8.")
        
        if verbose:
            print(f"📄 Processing page {page_number}...")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Get the appropriate processor and prompt
            processor = self.page_processors[page_number]
            prompt = self._get_page_prompt(page_number)
            
            # Create message with image
            content_blocks = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
            ]
            
            message = HumanMessage(content=content_blocks)
            
            # Process with structured output
            if verbose:
                print(f"🧠 LLM analyzing page {page_number}...")
            
            start_time = time.time()
            result = processor.invoke([message])
            processing_time = time.time() - start_time
            
            if verbose:
                print(f"✅ Page {page_number} completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            if verbose:
                print(f"❌ Error processing page {page_number}: {str(e)}")
            raise
    
    def process_all_pages(self, images_b64: List[str], verbose: bool = True) -> PageBasedMedicalReportData:
        """
        Process all pages and return complete medical report data
        
        :param images_b64: List of base64 encoded images (one per page)
        :param verbose: Whether to show progress messages
        :return: Complete PageBasedMedicalReportData object
        """
        if len(images_b64) > 9:
            raise ValueError("Maximum 9 pages supported (0-8)")
        
        if verbose:
            print(f"📋 Processing {len(images_b64)} pages...")
            print(f"🏁 Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Initialize result object
        result = PageBasedMedicalReportData()
        
        # Process each page
        for page_num, image_b64 in enumerate(images_b64):
            try:
                page_data = self.process_page(page_num, image_b64, verbose)
                
                # Assign to appropriate page
                if page_num == 0:
                    result.page_0 = page_data
                elif page_num == 1:
                    result.page_1 = page_data
                elif page_num == 2:
                    result.page_2 = page_data
                elif page_num == 3:
                    result.page_3 = page_data
                elif page_num == 4:
                    result.page_4 = page_data
                elif page_num == 5:
                    result.page_5 = page_data
                elif page_num == 6:
                    result.page_6 = page_data
                elif page_num == 7:
                    result.page_7 = page_data
                elif page_num == 8:
                    result.page_8 = page_data
                    
            except Exception as e:
                if verbose:
                    print(f"⚠️  Warning: Failed to process page {page_num}: {str(e)}")
                continue
        
        if verbose:
            print(f"🎉 All pages processed successfully!")
        
        return result
    
    def _get_page_prompt(self, page_number: int) -> str:
        """
        Get extraction prompt for specific page using config.json
        
        :param page_number: Page number (0-8)
        :return: Extraction prompt
        """
        base_instruction = f"""
You are extracting fillable data from page {page_number} of a medical examination form.
Analyze the image carefully and extract all visible information.

IMPORTANT INSTRUCTIONS:
- Extract only the information that is clearly visible in the image
- For checkboxes, look for yes or no checkboxes
- For dates, extract in the format found (DD/MM/YYYY, MM/DD/YYYY, etc.)
- For measurements, include units if visible
- If text is unclear or illegible, leave the field empty rather than guessing 

"""
        
        # Find the page configuration
        page_config = None
        for page in self.config.get("pages", []):
            if page.get("page_number") == page_number:
                page_config = page
                break
        
        if not page_config:
            return base_instruction + f"PAGE {page_number}: Extract all visible information from this page."
        
        # Generate field list from config
        fields = page_config.get("fields", [])
        if not fields:
            return base_instruction + f"PAGE {page_number}: Extract all visible information from this page."
        
        field_instructions = f"PAGE {page_number} FIELDS TO EXTRACT:\n"
        for field in fields:
            field_instructions += f"- {field}: Extract the value for this field\n"
        
        # Add page-specific context based on page number
        context = self._get_page_context(page_number)
        
        return base_instruction + field_instructions + "\n" + context
    
    def _get_page_context(self, page_number: int) -> str:
        """
        Get page-specific context information
        
        :param page_number: Page number (0-8)
        :return: Context information for the page
        """
        contexts = {
            0: "This is typically the first page containing basic identification information like reference numbers and names.",
            1: "This page usually contains personal information and the first set of medical history questions (1-12). Look for numbered medical questions with Y/N answers.",
            2: "This page contains the continuation of medical history questions (13-27). Look for numbered questions with Y/N answers.",
            3: "This page contains confidential medical examination details, physical measurements, and family history information.",
            4: "This page contains additional measurements and respiratory/circulatory system findings.",
            5: "This page contains detailed circulatory system measurements (blood pressure readings) and digestive/endocrine/lymph system findings.",
            6: "This page contains genito-urinary findings, urine test results, and nervous system findings (vision, hearing).",
            7: "This page contains neurological findings and musculoskeletal/skin examination results.",
            8: "This page contains the summary, recommendations, and examiner details including signature and qualifications."
        }
        
        context = contexts.get(page_number, "Extract all visible information from this page.")
        return f"CONTEXT: {context}"
    
    def process_file(self, file_path: str, verbose: bool = True) -> PageBasedMedicalReportData:
        """
        Process a PDF file and return structured data
        
        :param file_path: Path to the PDF file
        :param verbose: Whether to show progress messages
        :return: PageBasedMedicalReportData object
        """
        if verbose:
            print(f"📁 Processing file: {file_path}")
        
        # Convert PDF to images - get all pages as base64 strings
        if file_path.lower().endswith('.pdf'):
            # For PDF, we need to process each page individually
            pdf_images = self.image_processor.pdf_to_images(file_path)
            images_b64 = []
            
            for i, img in enumerate(pdf_images):
                # Convert each PIL image to base64
                img_b64 = self.image_processor.convert_to_base64(img)
                images_b64.append(img_b64)
                
            if verbose:
                print(f"📄 Extracted {len(images_b64)} pages from PDF")
        else:
            # For single image files
            img_b64 = self.image_processor.process_file_to_base64(file_path, 0)
            images_b64 = [img_b64]
            
            if verbose:
                print(f"📄 Processed single image file")
        
        # Process all pages
        return self.process_all_pages(images_b64, verbose)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get processor statistics
        
        :return: Dictionary with processor stats
        """
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "supported_pages": list(self.page_processors.keys()),
            "total_page_types": len(self.page_processors),
            "config_loaded": len(self.config.get("pages", [])) > 0,
            "total_config_pages": len(self.config.get("pages", []))
        }
    
    def process_single_page_from_file(self, file_path: str, page_number: int, verbose: bool = True) -> Any:
        """
        Process only a specific page from a PDF file and return structured data
        
        :param file_path: Path to the PDF file
        :param page_number: Page number to process (0-8)
        :param verbose: Whether to show progress messages
        :return: Structured PageData object for the specific page
        """
        if page_number not in self.page_processors:
            raise ValueError(f"Page number {page_number} not supported. Must be 0-8.")
        
        if verbose:
            print(f"📁 Processing single page {page_number} from file: {file_path}")
        
        try:
            # Convert PDF to images - get all pages first
            if file_path.lower().endswith('.pdf'):
                pdf_images = self.image_processor.pdf_to_images(file_path)
                
                if page_number >= len(pdf_images):
                    raise ValueError(f"Page {page_number} not found. PDF has {len(pdf_images)} pages (0-{len(pdf_images)-1})")
                
                # Convert only the requested page to base64
                img_b64 = self.image_processor.convert_to_base64(pdf_images[page_number])
                
                if verbose:
                    print(f"📄 Extracted page {page_number} from PDF ({len(pdf_images)} total pages)")
            else:
                # For single image files, only process if page_number is 0
                if page_number != 0:
                    raise ValueError(f"Image files only have page 0, requested page {page_number}")
                
                img_b64 = self.image_processor.process_file_to_base64(file_path, 0)
                
                if verbose:
                    print(f"📄 Processed single image file as page 0")
            
            # Process the specific page
            return self.process_page(page_number, img_b64, verbose)
            
        except Exception as e:
            if verbose:
                print(f"❌ Error processing page {page_number} from file: {str(e)}")
            raise 