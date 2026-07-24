"""
Streamlit web application for AI-Powered Resume Tracker & ATS Optimizer.
Provides an interactive dashboard for resume analysis and optimization.
"""

# Initialize spaCy model on startup
import subprocess
import sys

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Model not found, download it
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    import spacy
    nlp = spacy.load("en_core_web_sm")

import streamlit as st
import tempfile
from pathlib import Path
import logging
from typing import Optional

from utils import ResumeParser, full_analysis
from config import (
    APP_TITLE, APP_DESCRIPTION, MAX_FILE_SIZE_MB, ALLOWED_FILE_EXTENSIONS,
    TOP_N_SKILLS, PAGE_ICON, LAYOUT, INITIAL_SIDEBAR_STATE,
    EXCELLENT_MATCH, GOOD_MATCH, COLOR_EXCELLENT, COLOR_GOOD, COLOR_POOR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .matched-keyword {
        display: inline-block;
        background-color: #90EE90;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .missing-keyword {
        display: inline-block;
        background-color: #FFB6C6;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .recommendation-box {
        background-color: #FFF3CD;
        padding: 1rem;
        border-left: 4px solid #FFC107;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def get_score_color(score: float) -> str:
    if score >= (EXCELLENT_MATCH * 100):
        return COLOR_EXCELLENT
    elif score >= (GOOD_MATCH * 100):
        return COLOR_GOOD
    else:
        return COLOR_POOR


def display_header():
    st.title(f"{PAGE_ICON} {APP_TITLE}")
    st.markdown(f"**{APP_DESCRIPTION}**")
    st.markdown("---")


def display_instructions():
    with st.expander("📋 Instructions", expanded=True):
        st.markdown("""
        ### How to use this tool:
        
        1. **Paste Job Description**: Copy the entire job description into the text area.
        2. **Upload Resume**: Upload your resume in PDF or DOCX format.
        3. **Analyze**: Click the "Analyze Resume" button to get detailed insights.
        4. **Review Results**: 
           - Check your match percentage
           - Review matched skills (keywords present in both documents)
           - Identify missing skills (keywords in JD but not in resume)
           - Follow recommendations to improve your resume
        
        ### Tips for Best Results:
        - Use a well-formatted, text-based resume (avoid scanned images)
        - Include relevant skills and keywords from the job description
        - Keep your resume clear and organized
        - Update your resume for different job applications
        """)


def validate_file(uploaded_file) -> bool:
    if uploaded_file is None:
        st.error("❌ Please upload a resume file.")
        return False
    
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ File size exceeds {MAX_FILE_SIZE_MB}MB limit.")
        return False
    
    file_extension = Path(uploaded_file.name).suffix.lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        st.error(f"❌ Unsupported file format. Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}")
        return False
    
    return True


def validate_job_description(job_description: str) -> bool:
    if not job_description or len(job_description.strip()) < 50:
        st.error("❌ Job description must be at least 50 characters long.")
        return False
    return True


def display_analysis_results(analysis_results: dict):
    match_score = analysis_results['match_percentage']
    matched_keywords = analysis_results['matched_keywords']
    missing_keywords = analysis_results['missing_keywords']
    recommendations = analysis_results['recommendations']
    
    st.markdown("### 📊 Match Score")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score_color = get_score_color(match_score)
        st.metric(
            "Overall Match",
            f"{match_score}%",
            delta=None
        )
        st.markdown(
            f"<div style='background-color: {score_color}; padding: 1rem; border-radius: 0.5rem; text-align: center;'>"
            f"<span style='color: white; font-weight: bold; font-size: 1.5rem;'>{match_score}%</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col2:
        keyword_coverage = recommendations['keyword_coverage']
        st.metric(
            "Keyword Coverage",
            f"{keyword_coverage:.1f}%",
            delta=None
        )
    
    with col3:
        total_keywords = len(matched_keywords) + len(missing_keywords)
        st.metric(
            "Total Relevant Keywords",
            total_keywords,
            delta=None
        )
    
    st.markdown("### 💡 Overall Feedback")
    feedback_color = "#d4edda" if match_score >= 50 else "#f8d7da"
    st.markdown(
        f"<div style='background-color: {feedback_color}; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #666;'>"
        f"{recommendations['overall_feedback']}"
        f"</div>",
        unsafe_allow_html=True
    )
    
    st.markdown("### ✅ Matched Keywords (Found in Resume)")
    if matched_keywords:
        keywords_html = ""
        for keyword in matched_keywords:
            keywords_html += f"<span class='matched-keyword'>{keyword}</span>"
        st.markdown(keywords_html, unsafe_allow_html=True)
    else:
        st.info("No matched keywords found. Consider reviewing the job description.")
    
    st.markdown("### ❌ Missing Keywords (Not in Resume)")
    if missing_keywords:
        keywords_html = ""
        for keyword in missing_keywords:
            keywords_html += f"<span class='missing-keyword'>{keyword}</span>"
        st.markdown(keywords_html, unsafe_allow_html=True)
        st.markdown(
            "**💬 Tip**: Consider incorporating these keywords naturally into your resume "
            "if they are relevant to your experience."
        )
    else:
        st.success("🎉 Great! All keywords from the job description are present in your resume.")
    
    st.markdown("### 🎯 Recommended Actions")
    for i, action in enumerate(recommendations['priority_actions'], 1):
        st.markdown(
            f"<div class='recommendation-box'>"
            f"<strong>{i}.</strong> {action}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with st.expander("📈 Detailed Statistics"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Resume Length (words)", f"{analysis_results['resume_length']:,}")
        with col2:
            st.metric("Job Description Length (words)", f"{analysis_results['job_desc_length']:,}")


def main():
    display_header()
    display_instructions()
    
    st.markdown("### 📝 Input Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Paste Job Description")
        job_description = st.text_area(
            "Job Description",
            height=250,
            placeholder="Paste the complete job description here...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("#### 2. Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Resume Upload",
            type=ALLOWED_FILE_EXTENSIONS,
            help=f"Upload PDF or DOCX file (Max {MAX_FILE_SIZE_MB}MB)",
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        analyze_button = st.button(
            "🔍 Analyze Resume",
            use_container_width=True,
            type="primary"
        )
    
    if analyze_button:
        if not validate_job_description(job_description):
            return
        
        if not validate_file(uploaded_file):
            return
        
        with st.spinner("📄 Parsing resume..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    tmp_file_path = tmp_file.name
                
                file_type = Path(uploaded_file.name).suffix
                resume_text = ResumeParser.parse_resume(tmp_file_path, file_type)
                
                if not resume_text or len(resume_text.strip()) < 50:
                    st.error("❌ Could not extract text from resume. Please check the file format.")
                    return
                
                Path(tmp_file_path).unlink()
                
            except Exception as e:
                st.error(f"❌ Error parsing resume: {str(e)}")
                logger.error(f"Resume parsing error: {str(e)}")
                return
        
        with st.spinner("🤖 Analyzing resume against job description..."):
            try:
                analysis_results = full_analysis(
                    resume_text,
                    job_description,
                    top_n_keywords=TOP_N_SKILLS
                )
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Analysis error: {str(e)}")
                return
        
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")
        display_analysis_results(analysis_results)
        
        st.success("✅ Analysis complete!")
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📚 About This Tool")
        st.markdown("""
        This AI-powered tool analyzes how well your resume matches a job description using:
        
        - **TF-IDF Vectorization**: Extracts important terms and their relevance
        - **Cosine Similarity**: Measures text similarity between documents
        - **Keyword Extraction**: Identifies skills and competencies
        
        **Why it matters:**
        - ATS (Applicant Tracking Systems) scan for keyword matches
        - This tool helps you optimize your resume for ATS
        - Increase your chances of getting past automated screening
        """)
        
        st.markdown("---")
        st.markdown("### 🚀 Tips for Better Results")
        st.markdown("""
        1. **Format**: Use a clean, text-based resume
        2. **Keywords**: Mirror language from job description
        3. **Specificity**: Include relevant skills and experience
        4. **Length**: Optimize for your experience level
        5. **Testing**: Test against multiple job descriptions
        """)
        
        st.markdown("---")
        st.markdown("### 📞 Support")
        st.markdown("""
        - 📧 Email: support@resumetracker.com
        - 🐛 Report Issues: [GitHub Issues](https://github.com)
        - 💡 Feature Requests: [GitHub Discussions](https://github.com)
        """)
        
        st.markdown("---")
        st.markdown("<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
                   "Made with ❤️ using Streamlit & Machine Learning"
                   "</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
