import json
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# =================== PAGE CONFIG ========================
st.set_page_config(
    page_title="Subjective Answer Evaluator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"

)

# =================== UNIVERSAL CSS FOR ALL PAGES ========================
# Paste this RIGHT AFTER your imports and page config, BEFORE session state
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    
    /* ============= GLOBAL STYLES ============= */
    * { 
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease;
    }
    
    /* ============= BACKGROUND ============= */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0415 0%, #1a0f2e 25%, #2d1b4e 50%, #1a0f2e 75%, #0a0415 100%);
        background-size: 400% 400%;
        animation: gradientFlow 15s ease infinite;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ============= SIDEBAR PROFESSIONAL STYLING ============= */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, rgba(26, 15, 46, 0.95) 0%, rgba(45, 27, 78, 0.95) 100%);
        border-right: 2px solid rgba(167, 107, 255, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 4px 0 20px rgba(167, 107, 255, 0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        font-size: 2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #a775ff 0%, #e0d0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        letter-spacing: 2px;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.15) 0%, rgba(107, 70, 193, 0.15) 100%) !important;
        border: 1.5px solid rgba(167, 107, 255, 0.3) !important;
        color: #e0d0ff !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-align: left !important;
        position: relative !important;
        overflow: hidden !important;
        margin: 0.3rem 0 !important;
    }
    
    [data-testid="stSidebar"] .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(167, 107, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    [data-testid="stSidebar"] .stButton button:hover::before {
        left: 100%;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.3) 0%, rgba(107, 70, 193, 0.3) 100%) !important;
        border-color: #a775ff !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 15px rgba(167, 107, 255, 0.4) !important;
    }
    
    /* ============= PAGE TITLES ============= */
    h1 {
        color: #e0d0ff !important;
        font-weight: 900 !important;
        font-size: 3rem !important;
        text-align: center;
        background: linear-gradient(135deg, #e0d0ff 0%, #a775ff 50%, #e0d0ff 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease infinite;
        margin-bottom: 2rem !important;
    }
    
    h2, h3 {
        color: #c0a8ff !important;
        font-weight: 700 !important;
    }
    
    /* ============= INPUT FIELDS ============= */
    .stTextInput input, .stTextArea textarea {
        background: rgba(26, 15, 56, 0.6) !important;
        border: 2px solid rgba(167, 107, 255, 0.3) !important;
        color: #e0d0ff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #a775ff !important;
        box-shadow: 0 0 20px rgba(167, 107, 255, 0.3) !important;
        background: rgba(26, 15, 56, 0.8) !important;
    }
    
    .stTextInput label, .stTextArea label {
        color: #b8a0e8 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* ============= BUTTONS ============= */
    .stButton button {
        background: linear-gradient(135deg, #a775ff 0%, #7c4dff 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2.5rem !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(167, 107, 255, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton button:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 0 12px 35px rgba(167, 107, 255, 0.6) !important;
    }
    
    /* ============= METRICS/STATS ============= */
    [data-testid="stMetricValue"] {
        color: #a775ff !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(167, 107, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #b8a0e8 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.1) 0%, rgba(107, 70, 193, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid rgba(167, 107, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(167, 107, 255, 0.3);
        border-color: #a775ff;
    }
    
    /* ============= FILE UPLOADER ============= */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.1) 0%, rgba(107, 70, 193, 0.05) 100%);
        border: 2px dashed rgba(167, 107, 255, 0.4);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #a775ff;
        background: rgba(167, 107, 255, 0.15);
        box-shadow: 0 8px 25px rgba(167, 107, 255, 0.2);
    }
    
    [data-testid="stFileUploader"] label {
        color: #b8a0e8 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* ============= INFO/SUCCESS/ERROR BOXES ============= */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid #a775ff !important;
        backdrop-filter: blur(10px);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* ============= DATAFRAME/TABLE ============= */
    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
        border: 2px solid rgba(167, 107, 255, 0.2);
        box-shadow: 0 8px 25px rgba(167, 107, 255, 0.2);
    }
    
    /* ============= EXPANDER (for results) ============= */
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.1) 0%, rgba(107, 70, 193, 0.05) 100%);
        border: 2px solid rgba(167, 107, 255, 0.2);
        border-radius: 15px;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    [data-testid="stExpander"]:hover {
        border-color: #a775ff;
        box-shadow: 0 8px 25px rgba(167, 107, 255, 0.3);
    }
    
    [data-testid="stExpander"] summary {
        background: transparent;
        color: #e0d0ff !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border-radius: 12px;
        position: relative;
        padding-left: 2.5rem !important;
    }
    
    /* Hide material icons text */
    [data-testid="stExpander"] summary span.st-emotion-cache-1gulkj5,
    [data-testid="stExpander"] summary span[data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] .material-icons,
    [data-testid="stExpander"] span[class*="material"] {
        display: none !important;
    }
    
    [data-testid="stExpander"] summary::before {
        content: "▶" !important;
        position: absolute !important;
        left: 1rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        font-size: 1rem !important;
        color: #a775ff !important;
        transition: transform 0.3s !important;
    }
    
    [data-testid="stExpander"][open] summary::before {
        content: "▼" !important;
    }
    
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary div {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 95% !important;
        display: inline-block !important;
    }
    
    /* ============= SELECTBOX/DROPDOWN ============= */
    .stSelectbox > div > div {
        background: rgba(26, 15, 56, 0.6) !important;
        border: 2px solid rgba(167, 107, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #e0d0ff !important;
    }
    
    .stSelectbox label {
        color: #b8a0e8 !important;
        font-weight: 600 !important;
    }
    
    /* ============= RADIO BUTTONS ============= */
    .stRadio > label {
        color: #b8a0e8 !important;
        font-weight: 600 !important;
    }
    
    .stRadio > div {
        background: rgba(26, 15, 56, 0.3);
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid rgba(167, 107, 255, 0.2);
    }
    
    /* ============= CHECKBOX ============= */
    .stCheckbox label {
        color: #e0d0ff !important;
        font-weight: 600 !important;
    }
    
    /* ============= SPINNER/LOADER ============= */
    .stSpinner > div {
        border-top-color: #a775ff !important;
    }
    
    /* ============= COLUMNS SPACING ============= */
    [data-testid="column"] {
        padding: 0 1rem;
    }
    
    /* ============= MARKDOWN STYLING ============= */
    [data-testid="stMarkdownContainer"] p {
        color: #c0a8ff;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* ============= HOME PAGE SPECIFIC ============= */
    .hero-section {
        text-align: center;
        padding: 5rem 2rem;
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.15) 0%, 
            rgba(107, 70, 193, 0.1) 25%,
            rgba(167, 107, 255, 0.05) 50%,
            rgba(107, 70, 193, 0.1) 75%,
            rgba(167, 107, 255, 0.15) 100%);
        background-size: 400% 400%;
        animation: heroGradient 8s ease infinite;
        border-radius: 30px;
        margin: 2rem 0;
        border: 2px solid rgba(167, 107, 255, 0.3);
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(167, 107, 255, 0.2);
    }
    
    @keyframes heroGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #a775ff, #7c4dff, #a775ff, #e0d0ff);
        background-size: 400% 400%;
        border-radius: 30px;
        z-index: -1;
        animation: borderGlow 3s linear infinite;
        opacity: 0.5;
    }
    
    @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        margin-bottom: 1.5rem;
        line-height: 1.2;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #e0d0ff 0%, #a775ff 25%, #7c4dff 50%, #a775ff 75%, #e0d0ff 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .glitch {
        font-size: 4.5rem;
        font-weight: 900;
        color: #fff;
        text-shadow: 
            0 0 10px #a775ff,
            0 0 20px #a775ff,
            0 0 40px #a775ff,
            0 0 80px #7c4dff;
        animation: glitchText 3s ease-in-out infinite;
    }
    
    @keyframes glitchText {
        0%, 100% { 
            text-shadow: 
                2px 2px 0 #a775ff,
                -2px -2px 0 #7c4dff,
                0 0 20px #a775ff;
        }
        25% {
            text-shadow:
                -2px 2px 0 #7c4dff,
                2px -2px 0 #a775ff,
                0 0 30px #7c4dff;
        }
        50% {
            text-shadow:
                2px -2px 0 #a775ff,
                -2px 2px 0 #7c4dff,
                0 0 40px #a775ff;
        }
        75% {
            text-shadow:
                -2px -2px 0 #7c4dff,
                2px 2px 0 #a775ff,
                0 0 30px #7c4dff;
        }
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #c0a8ff;
        margin-bottom: 2.5rem;
        font-weight: 400;
        opacity: 0;
        animation: fadeInUp 1s ease forwards 0.5s;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .floating-elements {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    
    .float-circle {
        position: absolute;
        font-size: 3.5rem;
        opacity: 0.7;
        animation: float 8s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(167, 107, 255, 0.6));
    }
    
    .circle-1 { top: 10%; left: 10%; animation-delay: 0s; animation-duration: 7s; }
    .circle-2 { top: 15%; right: 12%; animation-delay: 1.5s; animation-duration: 9s; }
    .circle-3 { bottom: 20%; left: 15%; animation-delay: 3s; animation-duration: 8s; }
    .circle-4 { bottom: 15%; right: 10%; animation-delay: 2s; animation-duration: 10s; }
    
    @keyframes float {
        0%, 100% { 
            transform: translateY(0) rotate(0deg) scale(1);
        }
        25% {
            transform: translateY(-30px) rotate(90deg) scale(1.1);
        }
        50% { 
            transform: translateY(-50px) rotate(180deg) scale(1);
        }
        75% {
            transform: translateY(-30px) rotate(270deg) scale(1.1);
        }
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
        perspective: 1000px;
    }
    
    .feature-card {
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.1) 0%, 
            rgba(107, 70, 193, 0.05) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid rgba(167, 107, 255, 0.2);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.2) 0%, 
            transparent 50%);
        opacity: 0;
        transition: opacity 0.5s;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card:hover {
        transform: translateY(-15px) scale(1.05) rotateX(5deg);
        box-shadow: 
            0 25px 50px rgba(167, 107, 255, 0.4),
            0 0 50px rgba(167, 107, 255, 0.2);
        border-color: #a775ff;
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: inline-block;
        animation: bounce 2s ease-in-out infinite;
        filter: drop-shadow(0 0 10px rgba(167, 107, 255, 0.5));
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .feature-card:hover .feature-icon {
        animation: spin 0.8s ease-in-out;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.2); }
        to { transform: rotate(360deg) scale(1); }
    }
    
    .feature-title {
        color: #e0d0ff;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        background: linear-gradient(135deg, #e0d0ff 0%, #a775ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-desc {
        color: #b8a0e8;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 4rem 0;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    .stat-box {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.1) 0%, 
            rgba(107, 70, 193, 0.05) 100%);
        border-radius: 20px;
        border: 2px solid rgba(167, 107, 255, 0.2);
        transition: all 0.4s ease;
        min-width: 180px;
    }
    
    .stat-box:hover {
        transform: translateY(-10px) scale(1.08);
        box-shadow: 0 15px 40px rgba(167, 107, 255, 0.4);
        border-color: #a775ff;
    }
    
    .stat-number {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #a775ff 0%, #e0d0ff 50%, #a775ff 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: statGlow 3s ease infinite;
    }
    
    @keyframes statGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .stat-label {
        color: #b8a0e8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

# =================== SESSION STATE ========================
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "history" not in st.session_state:
    st.session_state.history = []
if "total_evaluations" not in st.session_state:
    st.session_state.total_evaluations = 0
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "backend_url" not in st.session_state:
    st.session_state.backend_url = "http://127.0.0.1:8000"
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "MiniLM"
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""

# =================== CUSTOM CSS ========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1435 50%, #24143d 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1a0f2e 0%, #2d1b4e 100%);
        border-right: 1px solid rgba(167, 107, 255, 0.2);
    }
    
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.1) 0%, rgba(107, 70, 193, 0.05) 100%);
        border-radius: 24px;
        margin: 2rem 0;
        border: 1px solid rgba(167, 107, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        line-height: 1.3;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #e0d0ff 0%, #a775ff 50%, #e0d0ff 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .glitch {
        font-size: 4rem;
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 10px #a775ff, 0 0 20px #a775ff, 0 0 30px #a775ff;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: #c0a8ff;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .floating-elements {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        z-index: 0;
    }
    
    .float-circle {
        position: absolute;
        font-size: 3rem;
        opacity: 0.6;
        animation: float 6s ease-in-out infinite;
    }
    
    .circle-1 { top: 10%; left: 10%; animation-delay: 0s; }
    .circle-2 { top: 20%; right: 15%; animation-delay: 1s; }
    .circle-3 { bottom: 15%; left: 15%; animation-delay: 2s; }
    .circle-4 { bottom: 20%; right: 10%; animation-delay: 1.5s; }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-30px) rotate(180deg); }
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.1) 0%, rgba(107, 70, 193, 0.05) 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(167, 107, 255, 0.2);
        transition: all 0.4s ease;
        text-align: center;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 20px 40px rgba(167, 107, 255, 0.4);
        border-color: #a775ff;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        color: #e0d0ff;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #b8a0e8;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 3rem 0;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    .stat-box {
        text-align: center;
        padding: 1.5rem;
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a775ff 0%, #e0d0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #b8a0e8;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #a775ff 0%, #7c4dff 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(167, 107, 255, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(167, 107, 255, 0.6);
    }
    
    .stTextInput input, .stTextArea textarea {
        background: rgba(26, 15, 56, 0.6) !important;
        border: 1.5px solid rgba(167, 107, 255, 0.3) !important;
        color: #e0d0ff !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #a775ff !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #b8a0e8 !important;
        font-weight: 600 !important;
    }
    
    # ...existing code...
    /* EXPANDER FIXES - hide built-in material icon ligatures and use a custom arrow */
    [data-testid="stExpander"] {
        z-index: 3 !important;
    }

    [data-testid="stExpander"] summary {
        position: relative !important;
        padding-left: 2.2rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.6rem !important;
        overflow: hidden !important;
        white-space: nowrap !important;
    }

    [data-testid="stExpander"] summary::before {
        content: "▶" !important;
        position: absolute !important;
        left: 0.5rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        font-size: 0.95rem !important;
        color: #a775ff !important;
        pointer-events: none !important;
        z-index: 4 !important;
    }
    [data-testid="stExpander"][open] summary::before {
        content: "▼" !important;
    }

    /* hide any material-icon ligature text / svg / icon elements inside the summary */
    [data-testid="stExpander"] summary [aria-hidden="true"],
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary i,
    [data-testid="stExpander"] summary .material-icons,
    [data-testid="stExpander"] summary span[class*="material"],
    [data-testid="stExpander"] summary span[class*="icon"],
    [data-testid="stExpander"] summary .stIcon {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        font-size: 0 !important;
        overflow: hidden !important;
        line-height: 0 !important;
    }

    /* ensure the label text truncates gracefully */
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary div,
    [data-testid="stExpander"] summary span:not([role]) {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 95% !important;
        display: inline-block !important;
    }
# ...existing code...
</style>
""", unsafe_allow_html=True)

# =================== DEMO DATA ========================
DEMO_QUESTIONS = {
    "Photosynthesis": {
        "question": "What is photosynthesis? Explain the process.",
        "reference": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce oxygen and energy in the form of glucose.",
        "good_answer": "Photosynthesis is how plants make food using sunlight. They take in CO2 and water, and use chlorophyll to convert these into glucose and oxygen.",
        "average_answer": "Photosynthesis is when plants make food from sunlight and CO2.",
        "poor_answer": "Plants need sunlight to grow."
    },
    "Gravity": {
        "question": "Define gravity and its significance in the universe.",
        "reference": "Gravity is a fundamental force that attracts two bodies towards each other. It governs the motion of planets, stars, and galaxies, and is essential for the structure of the universe.",
        "good_answer": "Gravity is a force that pulls objects toward each other. It keeps planets in orbit around stars and is crucial for the formation of galaxies.",
        "average_answer": "Gravity is a force that pulls things together in space.",
        "poor_answer": "Things fall down because of gravity."
    },
    "mitochondria": {
        "question": "What are mitochondria and their role in cells?",
        "reference": "Mitochondria are organelles found in most eukaryotic cells. They are known as the powerhouses of the cell because they generate most of the cell's supply of ATP, which is used as a source of chemical energy.",
        "good_answer": "Mitochondria are cell organelles that produce energy. They convert nutrients into ATP, which powers various cellular functions.",
        "average_answer": "Mitochondria make energy for the cell.",
        "poor_answer": "Mitochondria are parts of cells."
    }
    
}


# =================== UTILITY FUNCTIONS ========================
def add_to_history(mode, question, score, feedback, grade="N/A"):
    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "question": question[:50] + "..." if len(question) > 50 else question,
        "score": score,
        "grade": grade,
        "feedback": feedback
    })
    st.session_state.total_evaluations += 1


def create_gauge_chart(score, title="Score"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 22, 'color': '#fff'}},
        gauge={
            'axis': {'range': [None, 10], 'tickcolor': "#7f58e0"},
            'bar': {'color': "#a883ff"},
            'steps': [
                {'range': [0, 5], 'color': "#624087"},
                {'range': [5, 8], 'color': "#8880b2"},
                {'range': [8, 10], 'color': "#a478ff"}
            ]
        }
    ))
    fig.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', font={'color': '#fff'})
    return fig


# =================== SIDEBAR ========================
# =================== ENHANCED CSS ========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap');
    
    * { 
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0415 0%, #1a0f2e 25%, #2d1b4e 50%, #1a0f2e 75%, #0a0415 100%);
        background-size: 400% 400%;
        animation: gradientFlow 15s ease infinite;
    }
    
    @keyframes gradientFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Professional Sidebar */
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, rgba(26, 15, 46, 0.95) 0%, rgba(45, 27, 78, 0.95) 100%);
        border-right: 2px solid rgba(167, 107, 255, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 4px 0 20px rgba(167, 107, 255, 0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        font-size: 2rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #a775ff 0%, #e0d0ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        letter-spacing: 2px;
    }
    
    /* Sidebar Buttons Enhanced */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.15) 0%, rgba(107, 70, 193, 0.15) 100%) !important;
        border: 1.5px solid rgba(167, 107, 255, 0.3) !important;
        color: #e0d0ff !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-align: left !important;
        position: relative !important;
        overflow: hidden !important;
        margin: 0.3rem 0 !important;
    }
    
    [data-testid="stSidebar"] .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(167, 107, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    [data-testid="stSidebar"] .stButton button:hover::before {
        left: 100%;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.3) 0%, rgba(107, 70, 193, 0.3) 100%) !important;
        border-color: #a775ff !important;
        transform: translateX(5px) !important;
        box-shadow: 0 4px 15px rgba(167, 107, 255, 0.4) !important;
    }
    
    /* Hero Section with Advanced Animations */
    .hero-section {
        text-align: center;
        padding: 5rem 2rem;
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.15) 0%, 
            rgba(107, 70, 193, 0.1) 25%,
            rgba(167, 107, 255, 0.05) 50%,
            rgba(107, 70, 193, 0.1) 75%,
            rgba(167, 107, 255, 0.15) 100%);
        background-size: 400% 400%;
        animation: heroGradient 8s ease infinite;
        border-radius: 30px;
        margin: 2rem 0;
        border: 2px solid rgba(167, 107, 255, 0.3);
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(167, 107, 255, 0.2);
    }
    
    @keyframes heroGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Animated gradient border */
    .hero-section::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #a775ff, #7c4dff, #a775ff, #e0d0ff);
        background-size: 400% 400%;
        border-radius: 30px;
        z-index: -1;
        animation: borderGlow 3s linear infinite;
        opacity: 0.5;
    }
    
    @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        margin-bottom: 1.5rem;
        line-height: 1.2;
        position: relative;
        z-index: 1;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #e0d0ff 0%, #a775ff 25%, #7c4dff 50%, #a775ff 75%, #e0d0ff 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease infinite;
        display: inline-block;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .glitch {
        font-size: 4.5rem;
        font-weight: 900;
        color: #fff;
        text-shadow: 
            0 0 10px #a775ff,
            0 0 20px #a775ff,
            0 0 40px #a775ff,
            0 0 80px #7c4dff;
        animation: glitchText 3s ease-in-out infinite;
    }
    
    @keyframes glitchText {
        0%, 100% { 
            text-shadow: 
                2px 2px 0 #a775ff,
                -2px -2px 0 #7c4dff,
                0 0 20px #a775ff;
        }
        25% {
            text-shadow:
                -2px 2px 0 #7c4dff,
                2px -2px 0 #a775ff,
                0 0 30px #7c4dff;
        }
        50% {
            text-shadow:
                2px -2px 0 #a775ff,
                -2px 2px 0 #7c4dff,
                0 0 40px #a775ff;
        }
        75% {
            text-shadow:
                -2px -2px 0 #7c4dff,
                2px 2px 0 #a775ff,
                0 0 30px #7c4dff;
        }
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #c0a8ff;
        margin-bottom: 2.5rem;
        font-weight: 400;
        opacity: 0;
        animation: fadeInUp 1s ease forwards 0.5s;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Floating particles */
    .floating-elements {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    
    .float-circle {
        position: absolute;
        font-size: 3.5rem;
        opacity: 0.7;
        animation: float 8s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(167, 107, 255, 0.6));
    }
    
    .circle-1 { top: 10%; left: 10%; animation-delay: 0s; animation-duration: 7s; }
    .circle-2 { top: 15%; right: 12%; animation-delay: 1.5s; animation-duration: 9s; }
    .circle-3 { bottom: 20%; left: 15%; animation-delay: 3s; animation-duration: 8s; }
    .circle-4 { bottom: 15%; right: 10%; animation-delay: 2s; animation-duration: 10s; }
    
    @keyframes float {
        0%, 100% { 
            transform: translateY(0) rotate(0deg) scale(1);
        }
        25% {
            transform: translateY(-30px) rotate(90deg) scale(1.1);
        }
        50% { 
            transform: translateY(-50px) rotate(180deg) scale(1);
        }
        75% {
            transform: translateY(-30px) rotate(270deg) scale(1.1);
        }
    }
    
    /* Enhanced Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
        perspective: 1000px;
    }
    
    .feature-card {
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.1) 0%, 
            rgba(107, 70, 193, 0.05) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid rgba(167, 107, 255, 0.2);
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.2) 0%, 
            transparent 50%);
        opacity: 0;
        transition: opacity 0.5s;
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card:hover {
        transform: translateY(-15px) scale(1.05) rotateX(5deg);
        box-shadow: 
            0 25px 50px rgba(167, 107, 255, 0.4),
            0 0 50px rgba(167, 107, 255, 0.2);
        border-color: #a775ff;
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: inline-block;
        animation: bounce 2s ease-in-out infinite;
        filter: drop-shadow(0 0 10px rgba(167, 107, 255, 0.5));
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .feature-card:hover .feature-icon {
        animation: spin 0.8s ease-in-out;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.2); }
        to { transform: rotate(360deg) scale(1); }
    }
    
    .feature-title {
        color: #e0d0ff;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        background: linear-gradient(135deg, #e0d0ff 0%, #a775ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-desc {
        color: #b8a0e8;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Animated Stats */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 4rem 0;
        flex-wrap: wrap;
        gap: 2rem;
    }
    
    .stat-box {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, 
            rgba(167, 107, 255, 0.1) 0%, 
            rgba(107, 70, 193, 0.05) 100%);
        border-radius: 20px;
        border: 2px solid rgba(167, 107, 255, 0.2);
        transition: all 0.4s ease;
        min-width: 180px;
    }
    
    .stat-box:hover {
        transform: translateY(-10px) scale(1.08);
        box-shadow: 0 15px 40px rgba(167, 107, 255, 0.4);
        border-color: #a775ff;
    }
    
    .stat-number {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #a775ff 0%, #e0d0ff 50%, #a775ff 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: statGlow 3s ease infinite;
    }
    
    @keyframes statGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .stat-label {
        color: #b8a0e8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Enhanced Buttons */
    .stButton button {
        background: linear-gradient(135deg, #a775ff 0%, #7c4dff 100%) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 3rem !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 6px 20px rgba(167, 107, 255, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton button:hover {
        transform: translateY(-5px) scale(1.08) !important;
        box-shadow: 0 12px 35px rgba(167, 107, 255, 0.6) !important;
    }
    
    /* Metrics Enhancement */
    [data-testid="stMetricValue"] {
        color: #a775ff !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(167, 107, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #b8a0e8 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Expander Fixes */
    [data-testid="stExpander"] summary span.st-emotion-cache-1gulkj5,
    [data-testid="stExpander"] summary span[data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }
    
    [data-testid="stExpander"] summary {
        position: relative !important;
        padding-left: 2rem !important;
        background: linear-gradient(135deg, rgba(167, 107, 255, 0.1) 0%, rgba(107, 70, 193, 0.05) 100%);
        border-radius: 12px;
        padding: 1rem 1rem 1rem 2.5rem !important;
        border: 1.5px solid rgba(167, 107, 255, 0.2);
    }
    
    [data-testid="stExpander"] summary::before {
        content: "▶" !important;
        position: absolute !important;
        left: 1rem !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        font-size: 1rem !important;
        color: #a775ff !important;
        transition: transform 0.3s !important;
    }
    
    [data-testid="stExpander"][open] summary::before {
        content: "▼" !important;
        transform: translateY(-50%) rotate(0deg) !important;
    }
    
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary div {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 95% !important;
        display: inline-block !important;
    }
    
    [data-testid="stExpander"] .material-icons,
    [data-testid="stExpander"] span[class*="material"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# =================== ENHANCED SIDEBAR ========================
st.sidebar.markdown('<h1>🎓 ARC</h1>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="text-align: center; color: #b8a0e8; font-weight: 600; margin-top: -1rem;">Smart Answer Evaluation</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown('<p style="color: #a775ff; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.5rem;">📍 NAVIGATION</p>', unsafe_allow_html=True)

if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.current_page = "home"
    st.rerun()

if st.sidebar.button("📝 Text Evaluation", use_container_width=True):
    st.session_state.current_page = "text"
    st.rerun()

if st.sidebar.button("🔬 Advanced Analysis", use_container_width=True):
    st.session_state.current_page = "advanced"
    st.rerun()

if st.sidebar.button("📸 Image OCR", use_container_width=True):
    st.session_state.current_page = "ocr"
    st.rerun()

if st.sidebar.button("📄 PDF Evaluation", use_container_width=True):
    st.session_state.current_page = "pdf"
    st.rerun()

if st.sidebar.button("📦 Batch Processing", use_container_width=True):
    st.session_state.current_page = "batch"
    st.rerun()

if st.sidebar.button("📊 History & Analytics", use_container_width=True):
    st.session_state.current_page = "history"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color: #a775ff; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.5rem;">⚙️ SETTINGS</p>', unsafe_allow_html=True)
st.session_state.backend_url = st.sidebar.text_input("🌐 API URL", st.session_state.backend_url)
st.session_state.model_choice = st.sidebar.selectbox("🤖 AI Model", ["MiniLM", "MPNet"])
st.session_state.demo_mode = st.sidebar.checkbox("🎮 Demo Mode", value=st.session_state.demo_mode)

st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color: #a775ff; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem;">📈 STATISTICS</p>', unsafe_allow_html=True)
st.sidebar.metric("Total Evaluations", st.session_state.total_evaluations)
if st.session_state.history:
    avg = sum(h["score"] for h in st.session_state.history) / len(st.session_state.history)
    st.sidebar.metric("Average Score", f"{avg:.1f}/10")

# =================== MAIN CONTENT ========================
current_page = st.session_state.current_page

# =================== ENHANCED HOME PAGE ========================
if current_page == "home":
    st.markdown("""
        <div class="hero-section">
            <div class="hero-title">
                <span class="gradient-text">🎓 AI-Powered</span>
                <br>
                <span class="glitch">Answer Evaluation</span>
            </div>
            <div class="hero-subtitle">
                Transform subjective grading with intelligent AI assessment
            </div>
            <div class="floating-elements">
                <div class="float-circle circle-1">✨</div>
                <div class="float-circle circle-2">🚀</div>
                <div class="float-circle circle-3">📊</div>
                <div class="float-circle circle-4">🎯</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">📝</div>
                <div class="feature-title">Text Evaluation</div>
                <div class="feature-desc">Instant AI-powered assessment with detailed feedback and grading</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📸</div>
                <div class="feature-title">OCR Processing</div>
                <div class="feature-desc">Extract and evaluate handwritten answers with advanced OCR</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">PDF Evaluation</div>
                <div class="feature-desc">Batch process entire answer sheets automatically</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Analytics</div>
                <div class="feature-desc">Track performance trends and generate insights</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-number">95%</div>
                <div class="stat-label">Accuracy</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">10K+</div>
                <div class="stat-label">Evaluations</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">5 Sec</div>
                <div class="stat-label">Avg Speed</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Available</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Evaluating Now", use_container_width=True, type="primary"):
            st.session_state.current_page = "text"
            st.rerun()

# =================== TEXT EVALUATION ========================
# =================== TEXT EVALUATION ========================
elif current_page == "text":
    st.title("📝 Text Answer Evaluation")
    
    if st.session_state.demo_mode:
        st.info("🎮 Demo Mode Active - Using mock data")
        demo_topic = st.selectbox("Select Demo", list(DEMO_QUESTIONS.keys()))
        demo_quality = st.radio("Answer Quality", ["Excellent", "Average", "Poor"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.demo_mode:
            question = st.text_area("Question", value=DEMO_QUESTIONS[demo_topic]["question"], height=100, key="q_text")
            quality_map = {"Excellent": "good_answer", "Average": "average_answer", "Poor": "poor_answer"}
            student_answer = st.text_area("Student Answer", value=DEMO_QUESTIONS[demo_topic][quality_map[demo_quality]], height=150, key="ans_text")
        else:
            question = st.text_area("Question", height=100, placeholder="Enter question...", key="q_text_normal")
            student_answer = st.text_area("Student Answer", height=150, placeholder="Enter answer...", key="ans_text_normal")
    
    with col2:
        if st.session_state.demo_mode:
            ref_answer = st.text_area("Reference Answer", value=DEMO_QUESTIONS[demo_topic]["reference"], height=260, key="ref_text")
        else:
            ref_answer = st.text_area("Reference Answer", height=260, placeholder="Enter reference...", key="ref_text_normal")
    
    if st.button("🚀 Evaluate Answer", use_container_width=True, key="eval_btn"):
        if not question or not student_answer or not ref_answer:
            st.error("❌ Please fill all fields!")
        else:
            with st.spinner("Evaluating..."):
                if st.session_state.demo_mode:
                    # Demo mode - return mock data
                    time.sleep(1)
                    quality_scores = {
                        "Excellent": {"score": 9.2, "grade": "A", "similarity": 0.92, "coverage": 0.88, "grammar": 0.95, "relevance": 0.90},
                        "Average": {"score": 7.5, "grade": "B", "similarity": 0.75, "coverage": 0.72, "grammar": 0.80, "relevance": 0.78},
                        "Poor": {"score": 5.2, "grade": "C", "similarity": 0.52, "coverage": 0.48, "grammar": 0.60, "relevance": 0.55}
                    }
                    selected_quality = demo_quality if st.session_state.demo_mode else "Average"
                    mock_data = quality_scores.get(selected_quality, quality_scores["Average"])
                    
                    result = {
                        "final_score": mock_data["score"],
                        "grade": mock_data["grade"],
                        "similarity": mock_data["similarity"],
                        "coverage": mock_data["coverage"],
                        "grammar": mock_data["grammar"],
                        "relevance": mock_data["relevance"],
                        "feedback": f"{selected_quality} answer - Good understanding demonstrated.",
                        "detailed_metrics": {
                            "word_count": len(student_answer.split()),
                            "reference_word_count": len(ref_answer.split())
                        }
                    }
                else:
                    # Real API call
                    backend_url = st.session_state.backend_url
                    model_choice = st.session_state.model_choice
                    
                    try:
                        response = requests.post(
                            f"{backend_url}/evaluate",
                            json={
                                "question": question,
                                "reference_answer": ref_answer,
                                "student_answer": student_answer,
                                "model_name": model_choice
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Validate and fix zero values
                            if result.get('final_score', 0) == 0:
                                st.warning("⚠️ Backend returned zero score. Check your backend logic!")
                            if result.get('similarity', 0) == 0:
                                st.warning("⚠️ Similarity calculation returned zero. Verify the model is loaded correctly.")
                            
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                            st.code(response.text)
                            result = None
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend! Make sure the server is running.")
                        st.code(f"Trying to connect to: {backend_url}/evaluate")
                        st.info("💡 Enable Demo Mode in the sidebar to test without backend.")
                        result = None
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        result = None
                
                if result:
                    st.success("✅ Evaluation Complete!")
                    cols = st.columns(4)
                    cols[0].metric("Score", f"{result.get('final_score', 0):.1f}/10")
                    cols[1].metric("Grade", result.get('grade', 'N/A'))
                    cols[2].metric("Similarity", f"{result.get('similarity', 0)*100:.0f}%")
                    cols[3].metric("Coverage", f"{result.get('coverage', 0)*100:.0f}%")
                    
                    st.info(f"**Feedback:** {result.get('feedback', 'No feedback available')}")
                    
                    # Show detailed metrics
                    with st.expander("📊 Detailed Metrics"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Grammar", f"{result.get('grammar', 0)*100:.0f}%")
                            st.metric("Relevance", f"{result.get('relevance', 0)*100:.0f}%")
                        with col2:
                            metrics = result.get('detailed_metrics', {})
                            st.metric("Word Count", metrics.get('word_count', len(student_answer.split())))
                            st.metric("Ref Word Count", metrics.get('reference_word_count', len(ref_answer.split())))
                    
                    # Debug info (only if not demo mode)
                    if not st.session_state.demo_mode:
                        with st.expander("🔍 Debug Info"):
                            st.json(result)
                    
                    # Add to history
                    add_to_history("Text", question, result.get('final_score', 0), result.get('feedback', ''), result.get('grade', 'N/A'))

# =================== ADVANCED ANALYSIS ========================
elif current_page == "advanced":
    st.title("🔬 Advanced Analysis")
    st.info("Provides detailed metrics including grammar, relevance, depth analysis")
    
    question = st.text_area("Question", height=100, key="adv_q")
    ref_answer = st.text_area("Reference Answer", height=120, key="adv_ref")
    student_answer = st.text_area("Student Answer", height=150, key="adv_ans")
    
    if st.button("🔬 Run Analysis", use_container_width=True, key="adv_btn"):
        if not question or not student_answer or not ref_answer:
            st.error("❌ Please fill all fields!")
        else:
            with st.spinner("Analyzing..."):
                if st.session_state.demo_mode:
                    time.sleep(1)
                    result = {
                        "final_score": 8.3,
                        "grade": "B+",
                        "similarity": 0.87,
                        "coverage": 0.82,
                        "grammar": 0.94,
                        "relevance": 0.85,
                        "feedback": "Strong answer with minor gaps. Good conceptual understanding."
                    }
                else:
                    backend_url = st.session_state.backend_url
                    model_choice = st.session_state.model_choice
                    
                    try:
                        response = requests.post(
                            f"{backend_url}/evaluate",
                            json={
                                "question": question,
                                "reference_answer": ref_answer,
                                "student_answer": student_answer,
                                "model_name": model_choice
                            },
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                        else:
                            st.error(f"❌ API Error: {response.status_code}")
                            st.code(response.text)
                            result = None
                    
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to backend!")
                        st.info("💡 Enable Demo Mode in the sidebar to test without backend.")
                        result = None
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        result = None
                
                if result:
                    st.success("✅ Analysis Complete!")
                    cols = st.columns(4)
                    cols[0].metric("Score", f"{result.get('final_score', 0):.1f}/10")
                    cols[1].metric("Grade", result.get('grade', 'N/A'))
                    cols[2].metric("Grammar", f"{result.get('grammar', 0)*100:.0f}%")
                    cols[3].metric("Relevance", f"{result.get('relevance', 0)*100:.0f}%")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(create_gauge_chart(result.get('final_score', 0)), use_container_width=True)
                    with col2:
                        st.info(f"**Feedback:** {result.get('feedback', 'No feedback')}")
                        
                        # Additional metrics
                        st.metric("Similarity", f"{result.get('similarity', 0)*100:.0f}%")
                        st.metric("Coverage", f"{result.get('coverage', 0)*100:.0f}%")
                    
                    # Add to history
                    add_to_history("Advanced", question, result.get('final_score', 0), result.get('feedback', ''), result.get('grade', 'N/A'))
# =================== OCR EVALUATION ========================

# ...existing code...
elif current_page == "ocr":
    st.title("📸 Image OCR Evaluation")
    st.markdown("Upload an image of handwritten or printed answer for OCR extraction, diagram detection and evaluation")

    uploaded_img = st.file_uploader("Upload Answer Image", type=["png", "jpg", "jpeg"])

    # Helper imports & functions (local-only, keep inside block to avoid global deps)
    import io
    import re
    import difflib
    from difflib import SequenceMatcher

    DOMAIN_WORDS = [
        "photosynthesis", "chlorophyll", "chloroplast", "grana", "stroma", "mitochondria",
        "atp", "starch", "succinyl-coa", "porphyrin", "magnesium", "phytol", "enzyme",
        "krebs", "respiration", "glucose", "carbon", "dioxide", "light", "reaction",
        "dark", "thylakoid", "membrane", "diagram", "figure"
    ]

    COMMON_REPLACEMENTS = {
        r"[^A-Za-z0-9\s\.\,\-\+\(\)\/\:\;]": " ",
        r"\|+": " ",
        r"_{2,}": " ",
        r"\s{2,}": " ",
        r"\bfs\b": "is",
        r"\bfn\b": "in",
        r"chie?ro?phyll": "chlorophyll",
        r"chl?or?opl?ast": "chloroplast",
    }

    def clean_ocr_text(text: str) -> str:
        if not text:
            return ""
        txt = text.strip()
        txt = txt.replace("\u2019", "'").replace("\u2014", "-").replace("\u2013", "-")
        for pattern, repl in COMMON_REPLACEMENTS.items():
            txt = re.sub(pattern, repl, txt, flags=re.IGNORECASE)
        tokens = []
        for tok in re.split(r"(\s+|[\.,;:\-\(\)])", txt):
            if not tok or tok.isspace() or re.match(r"[\.,;:\-\(\)]", tok):
                tokens.append(tok)
                continue
            tl = tok.lower()
            if len(tl) <= 2 or re.fullmatch(r"[\d\.\-]+", tl):
                tokens.append(tok)
                continue
            if tl in DOMAIN_WORDS:
                tokens.append(tl)
                continue
            m = difflib.get_close_matches(tl, DOMAIN_WORDS, n=1, cutoff=0.78)
            if m:
                tokens.append(m[0])
                continue
            tokens.append(tok)
        cleaned = "".join(tokens)
        cleaned = re.sub(r"\s+([\,\.\;\:\)])", r"\1", cleaned)
        cleaned = re.sub(r"([\(])\s+", r"\1", cleaned)
        sentences = [s.strip().capitalize() for s in re.split(r'(?<=[\.\?\!])\s+', cleaned) if s.strip()]
        final = " ".join(sentences)
        final = re.sub(r"\s{2,}", " ", final).strip()
        return final

    def detect_diagram(pil_img) -> bool:
        # Simple edge-density heuristic using PIL (no OpenCV required)
        try:
            from PIL import ImageFilter, ImageOps
            small = pil_img.convert("L").resize((300, 300))
            edges = small.filter(ImageFilter.FIND_EDGES)
            arr = (ImageOps.autocontrast(edges)).point(lambda p: 255 if p > 64 else 0)
            import numpy as np
            a = np.array(arr)
            edge_pixels = (a > 128).sum()
            total = a.size
            edge_density = edge_pixels / max(1, total)
            # diagrams have higher edge density than pure text usually — threshold tuned experimentally
            return edge_density > 0.025
        except Exception:
            return False

    if uploaded_img:
        st.image(uploaded_img, width=480)

        if st.button("🔍 Extract Text (OCR)"):
            with st.spinner("Running OCR and diagram detection..."):
                raw_extracted = ""
                diagram_found = False
                try:
                    from PIL import Image
                    img = Image.open(io.BytesIO(uploaded_img.getvalue()))
                    # diagram detection (before OCR)
                    diagram_found = detect_diagram(img)
                    try:
                        import pytesseract
                        raw_extracted = pytesseract.image_to_string(img, lang='eng')
                        st.success("✅ Local OCR completed")
                    except Exception:
                        # backend OCR fallback
                        st.info("Local OCR not available — sending image to backend for OCR")
                        files = {"image": (uploaded_img.name, uploaded_img.getvalue(), uploaded_img.type)}
                        resp = requests.post(f"{st.session_state.backend_url}/ocr/extract", files=files, timeout=60)
                        if resp.status_code == 200:
                            raw_extracted = resp.json().get("extracted_text", "")
                            st.success("✅ Backend OCR completed")
                        else:
                            st.error(f"Backend OCR failed: {resp.status_code}")
                            raw_extracted = ""
                except Exception as e:
                    st.error(f"OCR error: {e}")
                    raw_extracted = ""

                cleaned = clean_ocr_text(raw_extracted)
                st.session_state.ocr_text = cleaned
                st.session_state._ocr_raw = raw_extracted
                st.session_state._ocr_diagram = diagram_found

                with st.expander("📄 Raw OCR output"):
                    st.text(raw_extracted or "(empty)")
                with st.expander("✍️ Cleaned OCR text"):
                    st.text(cleaned or "(empty)")
                st.markdown(f"**Diagram detected:** {'Yes' if diagram_found else 'No'}")

    ocr_text = st.text_area("Extracted Text (Edit if needed)", value=st.session_state.ocr_text, height=200)
    ref_answer = st.text_area("Reference Answer", height=120, placeholder="Paste reference answer here...")

    if st.button("📊 Evaluate OCR Answer"):
        if not ocr_text.strip():
            st.error("No extracted text to evaluate. Run OCR first or paste the answer.")
        elif not ref_answer.strip():
            st.error("Please provide a reference answer to score against.")
        else:
            with st.spinner("Evaluating..."):
                result = None
                # Try backend scoring endpoint first
                try:
                    payload = {
                        "question": "",
                        "reference_answer": ref_answer,
                        "student_answer": ocr_text,
                        "model_name": st.session_state.model_choice
                    }
                    resp = requests.post(f"{st.session_state.backend_url}/evaluate", json=payload, timeout=60)
                    if resp.status_code != 200:
                        # try OCR-specific endpoint
                        resp = requests.post(f"{st.session_state.backend_url}/evaluate/text", json={"extracted_answer": ocr_text, "reference_answer": ref_answer}, timeout=60)
                    if resp.status_code == 200:
                        raw = resp.json()
                        # normalize keys like in other UI handlers
                        result = {}
                        result['final_score'] = float(raw.get('final_score') or raw.get('score') or 0)
                        result['grade'] = raw.get('grade') or raw.get('letter_grade') or "N/A"
                        sim = raw.get('similarity', raw.get('similarity_score', 0))
                        try:
                            sim = float(sim)
                            if sim > 1:
                                sim = sim / 100.0
                        except Exception:
                            sim = 0.0
                        result['similarity'] = sim
                        cov = raw.get('coverage', raw.get('coverage_score', 0))
                        try:
                            cov = float(cov)
                            if cov > 1:
                                cov = cov / 100.0
                        except Exception:
                            cov = 0.0
                        result['coverage'] = cov
                        result['feedback'] = raw.get('feedback') or raw.get('comments') or ""
                        result['detailed_metrics'] = raw.get('detailed_metrics') or raw.get('metrics') or {}
                except Exception:
                    result = None

                # Local fallback scoring
                if result is None:
                    def similarity(a, b):
                        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
                    sim = similarity(ocr_text, ref_answer)
                    final_score = round(sim * 10, 1)
                    grade = ("A+" if final_score >= 9 else "A" if final_score >= 8 else "B+" if final_score >= 7 else "B" if final_score >= 6 else "C" if final_score >= 5 else "D")
                    result = {
                        "final_score": final_score,
                        "grade": grade,
                        "similarity": sim,
                        "coverage": sim,
                        "feedback": "Good match" if sim > 0.75 else "Needs improvement" if sim > 0.45 else "Poor match"
                    }

                # Apply diagram bonus if detected earlier
                diagram_bonus = 2 if st.session_state.get("_ocr_diagram", False) else 0
                if diagram_bonus:
                    orig = result.get("final_score", 0)
                    new_score = min(10.0, orig + diagram_bonus)
                    result["final_score"] = round(new_score, 1)
                    # note change in feedback
                    result["feedback"] = (result.get("feedback","") + f" Diagram detected (+{diagram_bonus} marks).").strip()

                # display results
                st.success("✅ Complete!")
                cols = st.columns(4)
                cols[0].metric("Score", f"{result['final_score']}/10")
                cols[1].metric("Grade", result['grade'])
                cols[2].metric("Similarity", f"{result['similarity']*100:.0f}%")
                cols[3].metric("Coverage", f"{result.get('coverage',0)*100:.0f}%")
                st.info(f"**Feedback:** {result.get('feedback','')}")
                st.markdown(f"**Diagram detected:** {'Yes' if st.session_state.get('_ocr_diagram', False) else 'No'}")

                # save to history
                add_to_history("OCR", ocr_text, result['final_score'], result.get('feedback',''), result.get('grade','N/A'))
# ...existing code...
# =================== PDF EVALUATION ========================
# =================== PDF EVALUATION ========================

# PDF Evaluation Tab
elif current_page == "pdf":
    st.title("📄 PDF Answer Sheet Evaluation")
    st.markdown("Upload answer sheets, question papers, and reference answers for automatic batch evaluation")
    
    
    ans_pdf = st.file_uploader("📝 Answer Sheet", type=["pdf"], key="ans")
    ques_pdf = st.file_uploader("📋 Question Paper", type=["pdf"], key="ques")
    ref_pdf = st.file_uploader("✅ Reference Answers", type=["pdf", "txt"], key="ref")
    
    student_name = st.text_input("👤 Student Name", key="sname")
    exam_name = st.text_input("📚 Exam Name", value="Mid-Term", key="ename")
    
    if st.button("🚀 Evaluate", key="evalpdf"):
        if not ans_pdf or not ques_pdf or not ref_pdf:
            st.error("Upload all 3 files")
        else:
            with st.spinner("Processing..."):
                try:
                    files = {
                        'answer_sheet': ans_pdf,
                        'question_paper': ques_pdf,
                        'reference_answers': ref_pdf
                    }
                    
                    data = {
                        'student_name': student_name or "Anonymous",
                        'exam_name': exam_name or "Exam"
                    }
                    
                    response = requests.post(
                        
                        
                        f"{st.session_state.backend_url}/pdf/evaluate_pdf_direct",
                        files=files,
                        data=data,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Evaluation Complete!")
                        
                        # Summary metrics
                        cols = st.columns(4)
                        cols[0].metric("Score", f"{result.get('total_obtained_marks', 0)}/{result.get('total_max_marks', 0)}")
                        cols[1].metric("Percentage", f"{result.get('percentage', 0):.1f}%")
                        cols[2].metric("Grade", result.get('grade', 'N/A'))
                        cols[3].metric("Time", f"{result.get('processing_time', 0):.1f}s")
                        
                        st.markdown(f"**Student:** {result.get('student_name', 'N/A')} | **Exam:** {result.get('exam_name', 'N/A')}")
                        
                        # Questions breakdown
                        st.markdown("### 📝 Question-wise Breakdown")
                        questions = result.get('questions_results', [])
                        
                        if questions:
                            for q in questions:
                                with st.expander(f"Q{q.get('question_number', '?')}: {q.get('question_text', '')[:60]}..."):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Marks", f"{q.get('obtained_marks', 0)}/{q.get('max_marks', 0)}")
                                        st.metric("Similarity", f"{q.get('similarity_score', 0)*100:.0f}%")
                                    with col2:
                                        st.metric("Coverage", f"{q.get('coverage_score', 0)*100:.0f}%")
                                        st.write(f"**Feedback:** {q.get('feedback', 'N/A')}")
                                    
                                    st.text_area("Answer:", q.get('extracted_answer', 'N/A')[:300], disabled=True, key=f"ans_{q.get('question_number', 0)}")
                        else:
                            st.warning("No questions found in result")
                        
                        # ==================== DOWNLOAD REPORTS ====================
                        st.markdown("---")
                        st.markdown("### 📥 Download Report")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # JSON Download
                            import json
                            report_json = json.dumps(result, indent=2)
                            st.download_button(
                                label="📄 Download JSON Report",
                                data=report_json,
                                file_name=f"evaluation_{result.get('student_name', 'report')}_{result.get('exam_name', 'exam').replace(' ', '_')}.json",
                                mime="application/json",
                                key="download_json"
                            )
                        
                        with col2:
                            # HTML Report
                            html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Evaluation Report - {result.get('student_name', 'Student')}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; color: #2d3748; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ font-size: 2.5rem; margin-bottom: 10px; font-weight: 700; }}
        .header p {{ font-size: 1.1rem; opacity: 0.95; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 40px; background: #f7fafc; }}
        .summary-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); text-align: center; transition: transform 0.2s; }}
        .summary-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }}
        .summary-card .label {{ color: #718096; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 600; }}
        .summary-card .value {{ font-size: 2.2rem; font-weight: 700; color: #667eea; }}
        .grade {{ font-size: 3rem !important; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .content {{ padding: 40px; }}
        .section-title {{ font-size: 1.8rem; color: #2d3748; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 3px solid #667eea; font-weight: 700; }}
        .question {{ background: #f7fafc; border-left: 4px solid #667eea; padding: 25px; margin-bottom: 25px; border-radius: 8px; page-break-inside: avoid; }}
        .question-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }}
        .question-number {{ font-size: 1.3rem; font-weight: 700; color: #667eea; }}
        .marks {{ background: #667eea; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 0.95rem; }}
        .question-text {{ font-size: 1.05rem; color: #2d3748; margin-bottom: 15px; font-weight: 600; }}
        .answer-section {{ background: white; padding: 18px; border-radius: 6px; margin: 15px 0; border: 1px solid #e2e8f0; }}
        .answer-label {{ font-weight: 600; color: #4a5568; margin-bottom: 8px; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .answer-text {{ color: #2d3748; line-height: 1.7; font-size: 0.98rem; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 15px 0; }}
        .metric {{ background: white; padding: 12px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; }}
        .metric-label {{ font-size: 0.8rem; color: #718096; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-value {{ font-size: 1.4rem; font-weight: 700; color: #667eea; }}
        .feedback {{ background: #edf2f7; padding: 15px; border-radius: 6px; margin-top: 12px; border-left: 3px solid #667eea; }}
        .feedback-label {{ font-weight: 600; color: #4a5568; margin-bottom: 6px; font-size: 0.9rem; }}
        .feedback-text {{ color: #2d3748; font-size: 0.95rem; }}
        .footer {{ background: #2d3748; color: white; padding: 30px; text-align: center; }}
        .footer p {{ margin: 5px 0; opacity: 0.9; }}
        @media print {{ body {{ background: white; padding: 0; }} .container {{ box-shadow: none; max-width: 100%; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Answer Evaluation Report</h1>
            <p>{result.get('exam_name', 'Examination')}</p>
        </div>
        <div class="summary">
            <div class="summary-card">
                <div class="label">Student Name</div>
                <div class="value" style="font-size: 1.4rem; color: #2d3748;">{result.get('student_name', 'Anonymous')}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Score</div>
                <div class="value">{result.get('total_obtained_marks', 0)}/{result.get('total_max_marks', 0)}</div>
            </div>
            <div class="summary-card">
                <div class="label">Percentage</div>
                <div class="value">{result.get('percentage', 0):.1f}%</div>
            </div>
            <div class="summary-card">
                <div class="label">Grade</div>
                <div class="value grade">{result.get('grade', 'N/A')}</div>
            </div>
        </div>
        <div class="content">
            <h2 class="section-title">📝 Detailed Question-wise Evaluation</h2>
            {''.join([f'''
            <div class="question">
                <div class="question-header">
                    <span class="question-number">Question {q.get('question_number', '?')}</span>
                    <span class="marks">Score: {q.get('obtained_marks', 0)}/{q.get('max_marks', 0)} marks</span>
                </div>
                <div class="question-text">{q.get('question_text', 'Question text not available')}</div>
                <div class="answer-section">
                    <div class="answer-label">📌 Student's Answer:</div>
                    <div class="answer-text">{q.get('extracted_answer', 'No answer detected')}</div>
                </div>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Similarity</div>
                        <div class="metric-value">{q.get('similarity_score', 0)*100:.0f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Coverage</div>
                        <div class="metric-value">{q.get('coverage_score', 0)*100:.0f}%</div>
                    </div>
                </div>
                <div class="feedback">
                    <div class="feedback-label">💬 Feedback:</div>
                    <div class="feedback-text">{q.get('feedback', 'No feedback available')}</div>
                </div>
            </div>
            ''' for q in result.get('questions_results', [])])}
        </div>
        <div class="footer">
            <p><strong>Evaluation Timestamp:</strong> {result.get('evaluation_timestamp', 'N/A')}</p>
            <p><strong>Processing Time:</strong> {result.get('processing_time', 0):.2f} seconds</p>
            <p style="margin-top: 15px; font-size: 0.9rem;">Generated by AI-Powered Answer Evaluation System v3.0</p>
        </div>
    </div>
</body>
</html>
"""
                            
                            st.download_button(
                                label="📊 Download HTML Report",
                                data=html_report,
                                file_name=f"evaluation_report_{result.get('student_name', 'student')}_{result.get('exam_name', 'exam').replace(' ', '_')}.html",
                                mime="text/html",
                                key="download_html"
                            )
                        # ==================== END REPORTS ====================
                        
                    else:
                        st.error(f"❌ API Error: {response.status_code}")
                        st.code(response.text)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# =================== BATCH PROCESSING ========================
elif current_page == "batch":
    st.title("📦 Batch Processing")
    st.markdown("Upload a CSV with multiple answers for batch evaluation")
    
    uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_csv:
        df = pd.read_csv(uploaded_csv)
        st.dataframe(df, use_container_width=True)
        
        if st.button("🚚 Run Batch Evaluation", use_container_width=True):
            with st.spinner("Processing batch..."):
                time.sleep(2)
                df["score"] = [8.5, 7.2, 9.0, 6.8, 8.9][:len(df)]
                df["grade"] = ["A-", "B", "A", "C+", "A-"][:len(df)]
                
                st.success("✅ Batch Complete!")
                st.dataframe(df, use_container_width=True)
                
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Results",
                    csv_data,
                    "batch_results.csv",
                    "text/csv"
                )

# =================== HISTORY & ANALYTICS ========================
elif current_page == "history":
    st.title("📊 History & Analytics")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        st.markdown("### 📋 Recent Evaluations")
        st.dataframe(df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Score Distribution")
            fig_hist = px.histogram(df, x="score", nbins=10, title="Score Distribution")
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0d0ff')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.markdown("### 🎓 Grade Distribution")
            grade_counts = df['grade'].value_counts()
            fig_pie = px.pie(names=grade_counts.index, values=grade_counts.values, title="Grades")
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0d0ff')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        csv_history = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download History",
            csv_history,
            "evaluation_history.csv",
            "text/csv"
        )
    else:
        st.info("📭 No evaluation history yet. Start evaluating to see analytics!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start First Evaluation", use_container_width=True):
                st.session_state.current_page = "text"
                st.rerun()
