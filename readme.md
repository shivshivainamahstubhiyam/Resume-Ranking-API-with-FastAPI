# Resume Ranking API

A FastAPI application that automates the process of ranking resumes based on job descriptions.

## Features

- **Extract Ranking Criteria**: Upload a job description (PDF/DOCX) and get key ranking criteria
- **Score Resumes**: Upload multiple resumes and score them against extracted criteria
- **Swagger UI Documentation**: Interactive API documentation
- **OpenAI Integration**: Uses GPT models for intelligent text analysis

## Architecture

The system consists of several components:

- **FastAPI Application**: Handles HTTP requests and responses
- **Document Processor**: Extracts text from PDF and DOCX files
- **LLM Processor**: Uses OpenAI to extract criteria and score resumes
- **Report Generator**: Creates Excel/CSV reports of resume rankings

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/resume-ranking-api.git
cd resume-ranking-api
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Running the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` and the Swagger UI documentation at `http://localhost:8000/docs`.

## API Endpoints

### 1. Extract Criteria

Extracts key ranking criteria from a job description file.

- **URL**: `/extract-criteria`
- **Method**: `POST`
- **Input**: 
  - Multipart form data with a file field containing the job description (PDF or DOCX)
- **Output**: 
  - JSON containing a list of extracted criteria

### 2. Score Resumes

Scores multiple resumes against provided criteria.

- **URL**: `/score-resumes`
- **Method**: `POST`
- **Input**: 
  - Multipart form data with:
    - `criteria`: List of criteria to score against
    - `files`: List of resume files (PDF or DOCX)
- **Output**: 
  - Excel file with candidate names, individual scores for each criterion, and total scores

## Usage Examples

### Using cURL

#### Extract Criteria
```bash
curl -X POST "http://localhost:8000/extract-criteria" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/job_description.pdf"
```

#### Score Resumes
```bash
curl -X POST "http://localhost:8000/score-resumes" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "criteria=Must have certification XYZ" \
  -F "criteria=5+ years of experience in Python development" \
  -F "criteria=Strong background in Machine Learning" \
  -F "files=@/path/to/resume1.pdf" \
  -F "files=@/path/to/resume2.pdf"
```

### Using Python Requests
```python
import requests

# Extract criteria
files = {'file': open('job_description.pdf', 'rb')}
response = requests.post('http://localhost:8000/extract-criteria', files=files)
criteria = response.json()['criteria']

# Score resumes
files = [
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.docx', 'rb'))
]
data = [('criteria', criterion) for criterion in criteria]
response = requests.post('http://localhost:8000/score-resumes', files=files, data=data)

# Save the Excel file
with open('resume_scores.xlsx', 'wb') as f:
    f.write(response.content)
```

## Project Structure

```
resume-ranking-api/
├── main.py                  # FastAPI application
├── utils/
│   ├── __init__.py
│   ├── document_processor.py  # Document text extraction
│   └── llm_processor.py       # LLM integration
├── requirements.txt         # Project dependencies
├── .env                     # Environment variables (not in repo)
└── README.md                # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
