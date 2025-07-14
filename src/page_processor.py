from typing import Dict, List, Any, Optional
import time
import json
from datetime import datetime
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from .image_processor import ImageProcessor
from .data import (
    Page0Data, Page1Data, Page2Data, Page3Data, Page4Data, 
    Page5Data, Page6Data, Page7Data, Page8Data, 
    PageBasedMedicalReportData
)

import os
from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()

# Now you can access variables as usual
api_key = os.environ.get("GEMINI_API_KEY")
base_url = os.environ.get("BASE_URL")

class PageProcessor:
    """Process medical forms page by page using ChatOllama with structured output"""
    
    def __init__(self, model_name: str = "unsloth/Llama-3.2-90B-Vision-Instruct-bnb-4bit", base_url: Optional[str] = None, config_path: str = "src/config.json"):
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
        self.local_llm = ChatOpenAI(
            base_url=f"{self.base_url}/v1",
            api_key="dummy-key",
            model=model_name
        )
        self.gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

        # Create structured output versions for each page
        self.local_page_processors = {
            0: self.local_llm.with_structured_output(Page0Data),
            1: self.local_llm.with_structured_output(Page1Data),
            2: self.local_llm.with_structured_output(Page2Data),
            3: self.local_llm.with_structured_output(Page3Data),
            4: self.local_llm.with_structured_output(Page4Data),
            5: self.local_llm.with_structured_output(Page5Data),
            6: self.local_llm.with_structured_output(Page6Data),
            7: self.local_llm.with_structured_output(Page7Data),
            8: self.local_llm.with_structured_output(Page8Data),
        }
        self.gemini_page_processors = {
            0: self.gemini_llm.with_structured_output(Page0Data),
            1: self.gemini_llm.with_structured_output(Page1Data),
            2: self.gemini_llm.with_structured_output(Page2Data),
            3: self.gemini_llm.with_structured_output(Page3Data),
            4: self.gemini_llm.with_structured_output(Page4Data),
            5: self.gemini_llm.with_structured_output(Page5Data),
            6: self.gemini_llm.with_structured_output(Page6Data),
            7: self.gemini_llm.with_structured_output(Page7Data),
            8: self.gemini_llm.with_structured_output(Page8Data),
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
    
    def process_page(self, page_number: int, image_b64: str, verbose: bool = True, model_type: str = "local") -> Any:
        """
        Process a single page and return structured data
        
        :param page_number: Page number (0-8)
        :param image_b64: Base64 encoded image
        :param verbose: Whether to show progress messages
        :param model_type: Type of model to use ("local" or "gemini")
        :return: Structured PageData object
        """ 
        if model_type == "local":
            page_processors = self.local_page_processors
        elif model_type == "gemini":
            page_processors = self.gemini_page_processors
        else:
            raise ValueError(f"Invalid model type: {model_type}")
        
        if verbose:
            print(f"📄 Processing page {page_number}...")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Get the appropriate processor and prompt
        processor = page_processors[page_number]
        prompt = self._get_page_prompt(page_number)
        
        # Create message with image
        content_blocks = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/png;base64,{image_b64}"
                }
            }
        ]
        
        message = HumanMessage(content=content_blocks)
        
        # Process with structured output using retry mechanism
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if verbose:
                    if retry_count > 0:
                        print(f"🔄 Retry {retry_count}/{max_retries} for page {page_number}...")
                    else:
                        print(f"🧠 LLM analyzing page {page_number}...")
                
                start_time = time.time()
                result = processor.invoke([message])
                processing_time = time.time() - start_time
                
                if verbose:
                    if retry_count > 0:
                        print(f"✅ Page {page_number} completed in {processing_time:.2f}s after {retry_count} retries")
                    else:
                        print(f"✅ Page {page_number} completed in {processing_time:.2f}s")
                
                return result
                
            except Exception as e:
                retry_count += 1
                if verbose:
                    print(f"⚠️  Error processing page {page_number} (attempt {retry_count}/{max_retries}): {str(e)}")
                
                if retry_count >= max_retries:
                    if verbose:
                        print(f"❌ Failed to process page {page_number} after {max_retries} attempts")
                    raise
                
                # Add delay before retry (exponential backoff)
                delay = 2 ** retry_count  # 2s, 4s, 8s
                if verbose:
                    print(f"⏳ Waiting {delay}s before retry...")
                time.sleep(delay)
    
    def process_all_pages(self, images_b64: List[str], verbose: bool = True, model_type: str = "local") -> PageBasedMedicalReportData:
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
                page_data = self.process_page(page_num, image_b64, verbose, model_type)
                
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
                
        return base_instruction + field_instructions 

    
    def process_file(self, file_path: str, verbose: bool = True, model_type: str = "local") -> PageBasedMedicalReportData:
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
        return self.process_all_pages(images_b64, verbose, model_type)
    
    
    def process_single_page_from_file(self, file_path: str, page_number: int, verbose: bool = True, model_type: str = "local") -> Any:
        """
        Process only a specific page from a PDF file and return structured data
        
        :param file_path: Path to the PDF file
        :param page_number: Page number to process (0-8)
        :param verbose: Whether to show progress messages
        :return: Structured PageData object for the specific page
        """
        if model_type == "local":
            page_processors = self.local_page_processors
        elif model_type == "gemini":
            page_processors = self.gemini_page_processors
        else:
            raise ValueError(f"Invalid model type: {model_type}")
        
        if page_number not in page_processors:
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