import streamlit as st
from dotenv import load_dotenv
import os
import PyPDF2
import google.generativeai as genai
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

def init_db():
    """Initialize SQLite database for saving analysis history"""
    import sqlite3
    conn = sqlite3.connect('ats_analysis.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_history
                 (date TEXT, job_title TEXT, match_percentage INTEGER, 
                  resume_text TEXT, job_description TEXT, analysis TEXT)''')
    conn.commit()
    return conn

def save_analysis(conn, job_title, match_percentage, resume_text, job_description, analysis):
    """Save analysis results to database"""
    c = conn.cursor()
    c.execute('''INSERT INTO analysis_history VALUES (?, ?, ?, ?, ?, ?)''',
              (datetime.now().isoformat(), job_title, match_percentage,
               resume_text, job_description, analysis))
    conn.commit()

def get_keyword_analysis(text, keywords):
    """Analyze keyword presence and frequency"""
    text = text.lower()
    results = {}
    for keyword in keywords:
        count = text.count(keyword.lower())
        results[keyword] = count
    return results

def extract_match_percentage(text):
    """Extract match percentage from analysis text"""
    try:
        # Look for percentage patterns in the text
        import re
        matches = re.findall(r'(\d+(?:\.\d+)?)%', text)
        if matches:
            return float(matches[0])
        return None
    except:
        return None

def generate_report(resume_text, job_description, analysis_results):
    """Generate a detailed PDF report"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    # Create PDF
    doc = SimpleDocTemplate(
        "ats_analysis_report.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Build content
    styles = getSampleStyleSheet()
    content = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    content.append(Paragraph("ATS Analysis Report", title_style))
    content.append(Spacer(1, 12))
    
    # Add analysis results
    content.append(Paragraph("Analysis Results:", styles['Heading2']))
    content.append(Paragraph(analysis_results, styles['Normal']))
    
    # Build and save PDF
    doc.build(content)
    return "ats_analysis_report.pdf"

def get_gemini_response(input_prompt, resume_text, job_description, job_title=""):
    model = genai.GenerativeModel('gemini-pro')
    
    combined_prompt = f"""
    Job Title: {job_title}
    
    Job Description:
    {job_description}

    Resume:
    {resume_text}

    {input_prompt}
    """
    
    response = model.generate_content(combined_prompt)
    return response.text

def main():
    # Initialize database
    conn = init_db()
    
    # Page config with dark mode
    st.set_page_config(
        page_title="ATS Resume Expert Pro",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS with dark mode support
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #ffffff;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
        }
        .stat-card {
            background-color: #333333;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Basic", "Advanced", "Expert"]
        )
        
        st.markdown("### 📊 Analysis History")
        c = conn.cursor()
        history = c.execute('''SELECT date, job_title, match_percentage FROM analysis_history
                              ORDER BY date DESC LIMIT 5''').fetchall()
        if history:
            history_df = pd.DataFrame(history, columns=['Date', 'Job Title', 'Match %'])
            st.dataframe(history_df)

    # Main content
    st.title("🎯 ATS Resume Expert Pro")
    st.subheader("Advanced Resume Analysis & Optimization")

    # Input sections
    col1, col2 = st.columns([1, 1])

    with col1:
        job_title = st.text_input("Job Title", placeholder="Enter the job title")
        job_description = st.text_area(
            "Job Description:",
            height=300,
            placeholder="Paste the job description here..."
        )

    with col2:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            help="Upload your resume in PDF format"
        )
        
        if uploaded_file:
            resume_text = extract_text_from_pdf(uploaded_file)
            if resume_text:
                st.success("✅ Resume parsed successfully!")
                
                # Quick stats
                word_count = len(resume_text.split())
                st.markdown("### 📈 Quick Stats")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Word Count", word_count)
                with stats_col2:
                    st.metric("Pages", len(PyPDF2.PdfReader(uploaded_file).pages))
                with stats_col3:
                    st.metric("File Size", f"{uploaded_file.size/1024:.1f} KB")

    # Analysis options
    if uploaded_file and job_description:
        st.markdown("### 🔍 Analysis Options")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 ATS Score", 
            "💡 Skills Analysis",
            "📈 Keyword Analysis",
            "📑 Full Report"
        ])

        with tab1:
            if st.button("Calculate ATS Score"):
                with st.spinner('Analyzing resume...'):
                    match_prompt = """
                    Analyze this resume against the job description as an ATS scanner.
                    Provide:
                    1. A specific match percentage (e.g., 75%)
                    2. Key matching keywords found
                    3. Missing important keywords
                    4. Detailed format analysis
                    5. Specific recommendations for improvement
                    
                    Start the response with the match percentage on its own line.
                    """
                    analysis = get_gemini_response(match_prompt, resume_text, job_description, job_title)
                    match_percentage = extract_match_percentage(analysis)
                    
                    if match_percentage:
                        st.markdown(f"### Match Score: {match_percentage}%")
                        
                        # Create gauge chart
                        fig = px.pie(values=[match_percentage, 100-match_percentage],
                                   names=['Match', 'Gap'],
                                   hole=0.7,
                                   color_discrete_sequence=['#4CAF50', '#ff0000'])
                        fig.update_layout(
                            annotations=[dict(text=f"{match_percentage}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
                        )
                        st.plotly_chart(fig)
                    
                    st.markdown("### Detailed Analysis")
                    st.write(analysis)
                    
                    # Save analysis
                    save_analysis(conn, job_title, match_percentage or 0,
                                resume_text, job_description, analysis)

        with tab2:
            if st.button("Analyze Skills"):
                with st.spinner('Analyzing skills...'):
                    skills_prompt = """
                    Provide a detailed skills analysis:
                    1. Current skills inventory (technical & soft)
                    2. Required skills for the role
                    3. Skills gap analysis
                    4. Recommendations for skill development
                    
                    Format the response in clear sections with bullet points.
                    """
                    analysis = get_gemini_response(skills_prompt, resume_text, job_description, job_title)
                    st.write(analysis)

        with tab3:
            if st.button("Analyze Keywords"):
                with st.spinner('Analyzing keywords...'):
                    # Extract important keywords from job description
                    keyword_prompt = """
                    Extract and list the top 10 most important technical keywords
                    from this job description. Return only the keywords,
                    one per line, no numbers or bullets.
                    """
                    keywords = get_gemini_response(keyword_prompt, "", job_description).split('\n')
                    keywords = [k.strip() for k in keywords if k.strip()]
                    
                    # Analyze keyword presence
                    keyword_analysis = get_keyword_analysis(resume_text, keywords)
                    
                    # Create bar chart
                    df = pd.DataFrame(list(keyword_analysis.items()),
                                    columns=['Keyword', 'Count'])
                    fig = px.bar(df, x='Keyword', y='Count',
                                title='Keyword Frequency Analysis')
                    st.plotly_chart(fig)
                    
                    # Show detailed breakdown
                    st.markdown("### Keyword Details")
                    for keyword, count in keyword_analysis.items():
                        st.markdown(f"- **{keyword}**: {count} occurrences")

        with tab4:
            if st.button("Generate Full Report"):
                with st.spinner('Generating comprehensive report...'):
                    # Generate comprehensive analysis
                    full_prompt = """
                    Provide a comprehensive analysis of this resume for the specified role:
                    1. Executive Summary
                    2. Technical Skills Match
                    3. Experience Alignment
                    4. Education & Certifications
                    5. Areas of Improvement
                    6. Specific Recommendations
                    
                    Format the response in clear sections with detailed explanations.
                    """
                    analysis = get_gemini_response(full_prompt, resume_text, job_description, job_title)
                    
                    # Generate and provide download link for PDF report
                    report_path = generate_report(resume_text, job_description, analysis)
                    
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="Download Full Report",
                            data=file,
                            file_name="ats_analysis_report.pdf",
                            mime="application/pdf"
                        )
                    
                    st.markdown("### Report Preview")
                    st.write(analysis)

    # Footer
    st.markdown("---")
    st.markdown("### 📌 Pro Tips")
    st.info("""
    - Use industry-standard keywords from the job description
    - Quantify achievements with metrics when possible
    - Ensure PDF is ATS-friendly (text-searchable)
    - Keep formatting clean and consistent
    - Update skills section based on job requirements
    """)

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded PDF file
    """
    if uploaded_file is not None:
        try:
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = ""
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            # Basic text cleaning
            text_content = text_content.strip()
            # Remove multiple newlines
            import re
            text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
            
            return text_content
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None
    return None

if __name__ == "__main__":
    main()