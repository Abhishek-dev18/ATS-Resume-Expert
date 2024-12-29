# ATS Resume Expert Pro

ATS Resume Expert Pro is a powerful web application built with Streamlit that helps users optimize their resumes for Applicant Tracking Systems (ATS). The tool provides comprehensive resume analysis, skill matching, and recommendations by leveraging Google's Gemini AI model.

## Features

- **ATS Score Analysis**: Get a detailed match percentage and analysis of your resume against job descriptions
- **Skills Analysis**: Comprehensive breakdown of technical and soft skills matching
- **Keyword Analysis**: Visual representation of important keyword frequencies
- **Full Report Generation**: Downloadable PDF reports with detailed recommendations
- **Analysis History**: Track your previous analyses and improvements
- **Dark Mode Interface**: Easy-on-the-eyes UI for better user experience

## Prerequisites

- Python 3.7+
- Google Cloud API key with Gemini API access

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ats-resume-expert-pro
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Required Libraries

- streamlit
- python-dotenv
- PyPDF2
- google-generativeai
- pandas
- plotly
- reportlab
- sqlite3

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Access the web interface through your browser (typically http://localhost:8501)

3. Using the application:
   - Enter the job title
   - Paste the job description
   - Upload your resume in PDF format
   - Choose from various analysis options:
     - Calculate ATS Score
     - Analyze Skills
     - Analyze Keywords
     - Generate Full Report

## Analysis Features

### ATS Score
- Match percentage calculation
- Key matching keywords identification
- Missing keywords analysis
- Format analysis
- Specific improvement recommendations

### Skills Analysis
- Current skills inventory
- Required skills for the role
- Skills gap analysis
- Development recommendations

### Keyword Analysis
- Visual representation of keyword frequency
- Top 10 important technical keywords
- Detailed keyword occurrence breakdown

### Full Report
- Executive summary
- Technical skills match
- Experience alignment
- Education & certifications analysis
- Areas for improvement
- Specific recommendations
- Downloadable PDF format

## Database

The application uses SQLite to store analysis history, including:
- Analysis date
- Job title
- Match percentage
- Resume text
- Job description
- Analysis results

## Pro Tips

- Use industry-standard keywords from the job description
- Quantify achievements with metrics when possible
- Ensure PDF is ATS-friendly (text-searchable)
- Keep formatting clean and consistent
- Update skills section based on job requirements

