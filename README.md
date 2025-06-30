# local-llm-OCR

A claim form processing system using local Vision LLM via Ollama. This project extracts structured information from claim forms (PDFs and images) using vision-enabled language models without traditional OCR tools.

## Features

- 🔍 **Direct Vision Processing**: Uses Vision LLM to understand both text and form structure
- 📄 **PDF & Image Support**: Processes both PDF documents and image files
- 🏥 **Specialized Form Types**: Optimized prompts for medical reports, consent forms, and generic documents
- 🏠 **Local Processing**: Runs entirely on your local machine using Ollama
- 📊 **Structured Output**: Extracts data into organized JSON format
- ⚡ **Batch Processing**: Handle multiple files efficiently

## Prerequisites

1. **Ollama Installation**: Install Ollama on your system
   ```bash
   # macOS
   brew install ollama
   
   # Or download from: https://ollama.ai
   ```

2. **Vision Model**: Pull a vision-capable model
   ```bash
   ollama pull bakllava
   # or
   ollama pull llava
   ```

## Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd local-llm-OCR
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Batch Processing
```bash
# Process all sample files
python main.py
```

### Programmatic Usage
```python
from src.llm_processor import ClaimFormProcessor

# Initialize processor
processor = ClaimFormProcessor(model_name="bakllava")

# Process a single file
result = processor.process_file("your_form.pdf", "medical_report")

# Check results
if result["status"] == "success":
    print(f"Extracted {len(result['extracted_fields'])} fields")
    for key, value in result["extracted_fields"].items():
        print(f"{key}: {value}")
```

## Form Types

The system supports specialized processing for different form types:

- **`generic`**: General form processing
- **`medical_report`**: Medical examination reports, diagnoses, patient info
- **`consent_form`**: Authorization forms, consent agreements
- **Custom types**: Easy to extend with new form-specific prompts

## Project Structure

```
local-llm-OCR/
├── src/
│   ├── __init__.py
│   ├── image_processor.py      # Image/PDF conversion and preprocessing
│   └── llm_processor.py        # Core LLM processing logic
├── output/                     # Generated results
├── main.py                     # Batch processing script
├── test_single_file.py         # Single file testing
├── requirements.txt            # Python dependencies
└── README.md
```

## Configuration

### Model Selection
You can use different vision models by changing the model name:

```python
# Use different models
processor = ClaimFormProcessor(model_name="llava")
processor = ClaimFormProcessor(model_name="bakllava")
```

### Image Quality
Adjust image processing settings in `ImageProcessor`:

```python
# Higher DPI for better quality (but larger files)
images = ImageProcessor.pdf_to_images("file.pdf", dpi=300)

# Custom max size for images
processor = ImageProcessor.preprocess_image(image, max_size=(4096, 4096))
```

## Tips for Better Results

1. **Ensure good image quality**: Higher DPI for complex forms
2. **Use appropriate form types**: Helps the LLM focus on relevant fields
3. **Check Ollama service**: Make sure Ollama is running (`ollama serve`)
4. **Model selection**: `bakllava` often works well for forms, `llava` for general images

## Troubleshooting

### Common Issues

**"Connection error"**: 
- Ensure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`

**"Model not found"**:
- Pull the model: `ollama pull bakllava`

**"Poor extraction quality"**:
- Try higher DPI for PDF conversion
- Use more specific form types
- Ensure image is clear and readable

## Sample Output

```json
{
  "form_type": "consent_form",
  "status": "success",
  "source_file": "consent_form.pdf",
  "extracted_fields": {
    "Patient Name": "John Doe",
    "Date of Birth": "01/15/1980",
    "Signature Date": "03/20/2024",
    "Authorized Party": "ABC Insurance Company"
  },
  "confidence": "medium"
}
```

## Next Steps

- 🔧 **Enhance prompts** for your specific form types
- 📈 **Add confidence scoring** based on field completeness
- 🎯 **Implement field validation** rules
- 🌐 **Build web interface** for easier usage
- 📊 **Export to multiple formats** (CSV, Excel, etc.)

