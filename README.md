# Medical Form OCR Processor

Extract structured data from medical examination forms using Vision LLM.

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Local LLM (Ollama)
BASE_URL=http://localhost:11434

# Database (optional)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medical_reports_db
DB_USER=root
DB_PASSWORD=your_password
```

3. **Start Ollama (for local model):**
```bash
ollama serve
```

## Usage

### Basic Processing
```python
from src.page_processor import PageProcessor

# Initialize processor
processor = PageProcessor()

# Process file with local model
results = processor.process_file("medical_form.pdf", verbose=True, model_type="local")

# Process file with Gemini model
results = processor.process_file("medical_form.pdf", verbose=True, model_type="gemini")
```

### Export to Database
```python
# Export to single table
results.to_mysql_db(
    host="localhost",
    database="medical_reports_db", 
    username="root",
    password="your_password"
)

# Export to grouped tables (recommended)
results.to_mysql_db_grouped(
    host="localhost",
    database="medical_reports_db",
    username="root", 
    password="your_password"
)
```

### Export to CSV
```python
# Get CSV records
csv_records = results.to_csv_records_list()

# Save to file
import pandas as pd
df = pd.DataFrame(csv_records)
df.to_csv("results.csv", index=False)
```

## Command Line Usage
```bash
# Process single file
python main.py "medical_form.pdf"

# Process with Gemini
python main.py "medical_form.pdf" --model gemini

# Export to database
python main.py "medical_form.pdf" --export-db --use-grouped-tables
```

## Models
- **Local**: Uses Ollama with Llama-3.2-Vision (faster, offline)
- **Gemini**: Uses Google Gemini 2.5 Flash (more accurate, requires API key) 