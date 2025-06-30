import base64
from io import BytesIO
from typing import List, Optional
import fitz  # PyMuPDF
from PIL import Image


class ImageProcessor:
    """Handle image conversion and processing for OCR with Vision LLM"""
    
    @staticmethod
    def convert_to_base64(pil_image: Image.Image, format: str = "JPEG") -> str:
        """
        Convert PIL images to Base64 encoded strings
        
        :param pil_image: PIL image object
        :param format: Image format (JPEG, PNG, etc.)
        :return: Base64 encoded string
        """
        buffered = BytesIO()
        pil_image.save(buffered, format=format)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str
    
    @staticmethod
    def pdf_to_images(pdf_path: str, dpi: int = 200) -> List[Image.Image]:
        """
        Convert PDF pages to PIL Image objects
        
        :param pdf_path: Path to the PDF file
        :param dpi: Resolution for conversion (higher = better quality but larger size)
        :return: List of PIL Image objects, one per page
        """
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Convert to pixmap with specified DPI
            mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(BytesIO(img_data))
            images.append(img)
        
        doc.close()
        return images
    
    @staticmethod
    def preprocess_image(image: Image.Image, max_size: tuple = (2048, 2048)) -> Image.Image:
        """
        Preprocess image for optimal LLM processing
        
        :param image: PIL Image object
        :param max_size: Maximum dimensions (width, height)
        :return: Preprocessed PIL Image
        """
        # Resize if image is too large
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (removes alpha channel)
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        return image
    
    @classmethod
    def process_file_to_base64(cls, file_path: str, page_index: int = 0) -> str:
        """
        Process a file (PDF or image) and return base64 encoded string
        
        :param file_path: Path to the file
        :param page_index: Page index for PDF files (0-based)
        :return: Base64 encoded string
        """
        if file_path.lower().endswith('.pdf'):
            images = cls.pdf_to_images(file_path)
            if page_index >= len(images):
                raise ValueError(f"Page index {page_index} exceeds PDF page count {len(images)}")
            image = images[page_index]
        else:
            # Assume it's an image file
            image = Image.open(file_path)
        
        # Preprocess the image
        processed_image = cls.preprocess_image(image)
        
        # Convert to base64
        return cls.convert_to_base64(processed_image) 
    