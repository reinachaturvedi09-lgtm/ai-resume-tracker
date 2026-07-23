"""
Configuration module for AI-Powered Resume Tracker & ATS Optimizer.
Centralizes all configurable parameters for the application.
"""

# Application Settings
APP_TITLE = "AI-Powered Resume Tracker & ATS Optimizer"
APP_DESCRIPTION = "Analyze and optimize your resume against job descriptions using advanced NLP and machine learning."

# File Upload Settings
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_EXTENSIONS = ['.pdf', '.docx']
UPLOAD_DIRECTORY = 'uploads'

# NLP & Matching Algorithm Settings
MIN_KEYWORD_LENGTH = 3
TOP_N_SKILLS = 15
MATCH_SCORE_THRESHOLD = 0.5

# Scoring Thresholds
EXCELLENT_MATCH = 0.75
GOOD_MATCH = 0.50
POOR_MATCH = 0.0

SPACY_MODEL = 'en_core_web_sm'

# UI Settings
PAGE_ICON = "📄"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Color Scheme for Metrics
COLOR_EXCELLENT = "#2ecc71"
COLOR_GOOD = "#f39c12"
COLOR_POOR = "#e74c3c"
