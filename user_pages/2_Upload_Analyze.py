import streamlit as st
import numpy as np
from PIL import Image
import os
import json
import sys

# Add root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.model import load_model, predict
from db.database import get_connection
from utils.helpers import require_login

# Ensure user is logged in
require_login()

# Initialize session state for analysis
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'uploaded_file_obj' not in st.session_state:
    st.session_state.uploaded_file_obj = None

# ------------------ PAGE CONFIG ------------------
# Page config handled in app.py

# ------------------ CUSTOM CSS & ICONS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap');

    /* Ensure Font Awesome loads */
    .fa, .fas, .far, .fal, .fab, .fa-solid {
        font-family: "Font Awesome 6 Free" !important;
        font-weight: 900 !important;
    }

    .stApp {
        background-color: #F8FAFC !important;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Typography */
    .header-title { font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 800; color: #1E293B; text-align: center; margin: 0; }
    .header-subtitle { font-family: 'DM Sans', sans-serif; font-size: 16px; color: #64748B; text-align: center; margin-top: 4px; }
    
    /* Global Button Styling - Premium Outline System */
    .stButton > button {
        background: white !important;
        color: #0D9488 !important;
        border: 2px solid #0D9488 !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background: #F0FDFA !important;
        color: #0D9488 !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.1) !important;
    }

    /* Primary Button Style (Solid) */
    .stButton > button[data-testid="baseButton-primary"] {
        background: #0D9488 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3) !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: #0F766E !important;
        box-shadow: 0 6px 18px rgba(13, 148, 136, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Container styling */
    .analysis-btn-container, .reanalyze-btn-container {
        display: inline-block;
        width: 100%;
        margin-top: 20px;
    }

    /* Cards */
    .custom-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #F1F5F9;
    }
    
    .card-title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
    .card-title { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: #334155; margin: 0; }
    .card-icon { color: #0D9488; font-size: 18px; }
    
    /* Result Section */
    .result-section {
        background: #F0FDFA;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        border: 1px solid #CCFBF1;
    }
    
    .diag-icon-circ {
        width: 80px; height: 80px; border-radius: 50%; background: #E0F2F1;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 24px; position: relative; border: 1px solid #B2DFDB;
    }
    
    .diag-label { font-size: 13px; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700; }
    .diag-value { font-family: 'Syne', sans-serif; font-size: 64px; font-weight: 800; color: #0D9488; margin: 0; line-height: 1; }
    
    .conf-pill { background: #CCFBF1; color: #0D9488; padding: 6px 16px; border-radius: 100px; font-size: 13px; font-weight: 700; margin: 20px 0 10px 0; }
    .conf-score { font-family: 'Syne', sans-serif; font-size: 48px; font-weight: 800; color: #1E293B; margin: 0; }
    .res-footer { font-size: 13px; color: #94A3B8; margin-top: 16px; max-width: 280px; line-height: 1.5; }
    
    /* Distribution Table */
    .dist-row { display: flex; align-items: center; margin-bottom: 12px; gap: 15px; }
    .dist-label { width: 70px; font-weight: 600; color: #475569; font-size: 13px; }
    .dist-bar-bg { flex: 1; height: 10px; background: #F1F5F9; border-radius: 10px; overflow: hidden; }
    .dist-bar-fill { height: 100%; border-radius: 10px; }
    .dist-val { width: 55px; text-align: right; font-weight: 700; font-size: 13px; }

    /* Modern Clickable Action Cards - Redesigned as Outline */
    .action-cards-container { margin: 30px 0 20px 0; }
    
    .action-card {
        background: white;
        border-radius: 24px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        height: 100%;
        position: relative;
        border: 2px solid #0D9488;
    }
    
    .action-card:hover {
        transform: translateY(-10px);
        background: #0D9488;
        box-shadow: 0 20px 40px rgba(13, 148, 136, 0.2);
    }
    
    .action-card-content {
        padding: 40px 28px;
        text-align: center;
        position: relative;
        z-index: 2;
    }
    
    .action-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto 24px auto;
        background: #F0FDFA;
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        color: #0D9488;
        transition: all 0.3s ease;
        border: 2px solid #CCFBF1;
    }
    
    .action-card:hover .action-icon {
        transform: scale(1.1) rotate(5deg);
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .action-title {
        font-family: 'Syne', sans-serif;
        font-size: 24px;
        font-weight: 800;
        color: #0D9488;
        margin: 0 0 12px 0;
        transition: all 0.3s ease;
    }
    
    .action-card:hover .action-title { color: white; }
    
    .action-description {
        font-family: 'DM Sans', sans-serif;
        font-size: 15px;
        color: #64748B;
        line-height: 1.6;
        margin: 0 0 24px 0;
        transition: all 0.3s ease;
    }
    
    .action-card:hover .action-description { color: rgba(255, 255, 255, 0.9); }
    
    .action-arrow {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        color: #0D9488;
        font-size: 15px;
        font-weight: 700;
        transition: all 0.3s ease;
        padding: 8px 20px;
        border-radius: 100px;
        background: #F0FDFA;
    }
    
    .action-card:hover .action-arrow {
        background: white;
        color: #0D9488;
        gap: 14px;
    }
    
    .action-arrow i { transition: transform 0.3s ease; }
    .action-card:hover .action-arrow i { transform: translateX(5px); }
    
    /* COMPLETELY HIDE OVERLAY BUTTONS */
    div[data-testid="column"]:has(.action-card-flex) .stButton {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 10 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div[data-testid="column"]:has(.action-card-flex) .stButton button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: transparent !important;
    }

    /* Premium File Uploader Styling */
    [data-testid="stFileUploader"] {
        width: 100%;
        padding: 0;
    }
    [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed #CBD5E1 !important;
        border-radius: 16px !important;
        padding: 30px 20px !important;
        background: white !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        min-height: 150px !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #0D9488 !important;
        background: #F0FDFA !important;
    }
    
    /* Hide default text */
    [data-testid="stFileUploaderDropzone"] > div:first-child { display: none !important; }
    
    /* Style the Browse files button */
    [data-testid="stFileUploaderDropzone"] button {
        background-color: #0D9488 !important;
        background: #0D9488 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 2px solid #0D9488 !important;
        padding: 0.4rem 1.2rem !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25) !important;
        transition: all 0.3s ease !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        margin-top: 10px !important;
    }
    
    [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #0F766E !important;
        background: #0F766E !important;
        border-color: #0F766E !important;
        box-shadow: 0 4px 10px rgba(13, 148, 136, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Custom uploader content */
    [data-testid="stFileUploaderDropzone"]::before {
        content: '\f0ee';
        font-family: 'Font Awesome 6 Free';
        font-weight: 900;
        font-size: 36px;
        color: #94A3B8;
        margin-bottom: 5px;
        display: block;
        text-align: center;
    }
    [data-testid="stFileUploaderDropzone"]::after {
        content: 'Drag and drop your OCT image here \A Support for PNG, JPG, JPEG (Max 10MB)';
        white-space: pre-wrap;
        text-align: center;
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: #334155;
        display: block;
    }

    /* Upload New Image Button */
    .new-img-btn-container {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        width: 100%;
        margin-top: 10px;
    }
    
    .new-img-btn-container button {
        background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        box-shadow: 0 6px 16px rgba(13, 148, 136, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .new-img-btn-container button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(13, 148, 136, 0.6) !important;
        background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%) !important;
    }
    
    .new-img-btn-container button p,
    .new-img-btn-container button span {
        font-size: 13px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
        color: white !important;
    }

    /* Section Header */
    .quick-actions-header {
        text-align: center;
        margin: 40px 0 20px 0;
    }
    
    .quick-actions-header h2 {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #1E293B;
        margin: 0;
    }
    
    .quick-actions-header p {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: #64748B;
        margin-top: 8px;
    }

    /* RESPONSIVE ADJUSTMENTS */
    @media (max-width: 768px) {
        .header-title { font-size: 24px !important; }
        .header-subtitle { font-size: 14px !important; }
        .result-section { padding: 20px !important; }
        .diag-value { font-size: 40px !important; }
        .conf-score { font-size: 32px !important; }
        .stButton > button { padding: 0.5rem 1rem !important; }
        [data-testid="stFileUploaderDropzone"]::after { font-size: 14px !important; }
        
        .action-card-content {
            padding: 24px 20px !important;
        }
        
        .action-icon {
            width: 55px !important;
            height: 55px !important;
            font-size: 26px !important;
            margin-bottom: 15px !important;
        }
        
        .action-title {
            font-size: 18px !important;
        }
        
        .action-description {
            font-size: 12px !important;
            margin-bottom: 15px !important;
        }
        
        .quick-actions-header h2 {
            font-size: 22px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
col_l, col_m, col_r = st.columns([1.5, 4, 1.5])

with col_l:
    pass

with col_m:
    st.markdown('<h1 class="header-title">Analysis Results</h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">AI-powered OCT image diagnosis</p>', unsafe_allow_html=True)

with col_r:
    st.markdown('<div class="new-img-btn-container">', unsafe_allow_html=True)
    if st.button("Upload New Image"):
        st.session_state.analysis_done = False
        st.session_state.current_analysis = None
        st.session_state.uploaded_file_obj = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ LOAD MODEL ------------------
model = load_model()

# ------------------ MAIN ROW ------------------
if not st.session_state.analysis_done:
    # File Uploader
    if st.session_state.uploaded_file_obj is None:
        uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if uploaded_file is not None:
            st.session_state.uploaded_file_obj = uploaded_file
            st.rerun()
    
    uploaded_file = st.session_state.uploaded_file_obj
    
    if uploaded_file is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        image = Image.open(uploaded_file)
        
        # Use the same layout as results for seamless transition
        m_col1, m_col2 = st.columns([1.2, 1.8], gap="large")
        
        with m_col1:
            st.markdown("""
            <div class="custom-card">
                <div class="card-title-row">
                    <i class="fa-solid fa-image card-icon"></i>
                    <h3 class="card-title">Uploaded OCT Image</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            
        with m_col2:
            st.markdown("""
            <div class="result-section" style="background: white; border-style: dashed;">
                <div class="diag-icon-circ" style="background: #F1F5F9; border-color: #CBD5E1;">
                    <i class="fa-solid fa-flask" style="font-size: 32px; color: #64748B;"></i>
                </div>
                <p class="diag-label">Ready for Analysis</p>
                <h1 class="diag-value" style="color: #64748B; font-size: 32px;">Image Loaded</h1>
                <p class="res-footer" style="margin-bottom: 24px;">Click the button below to start the AI diagnostic process.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-btn-container">', unsafe_allow_html=True)
            if st.button("🚀 Start Analysis", use_container_width=True, type="primary"):
                with st.spinner("Analyzing image with AI..."):
                    # 1. Predict
                    pred_class, confidence, probs_json = predict(image, model)
                    
                    # 2. Save file
                    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
                    os.makedirs(uploads_dir, exist_ok=True)
                    file_path = os.path.join(uploads_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 3. Save to DB
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO uploads (user_id, file_path) VALUES (?, ?)",
                        (st.session_state.user_id, file_path)
                    )
                    upload_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT INTO predictions (upload_id, user_id, predicted_class, confidence, probabilities_json) VALUES (?, ?, ?, ?, ?)",
                        (upload_id, st.session_state.user_id, pred_class, confidence, probs_json)
                    )
                    prediction_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    # 4. Update State
                    st.session_state.current_analysis = {
                        "prediction_id": prediction_id,
                        "image": image,
                        "class": pred_class,
                        "confidence": confidence,
                        "probabilities": json.loads(probs_json)
                    }
                    st.session_state.last_prediction = pred_class
                    st.session_state.last_prediction_id = prediction_id
                    st.session_state.analysis_done = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # ------------------ RESULTS VIEW ------------------
    res = st.session_state.current_analysis
    
    m_col1, m_col2 = st.columns([1.2, 1.8], gap="large")

    with m_col1:
        st.markdown("""
        <div class="custom-card">
            <div class="card-title-row">
                <i class="fa-solid fa-image card-icon"></i>
                <h3 class="card-title">Uploaded OCT Image</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.image(res["image"], use_container_width=True)
        
        # Re-Analyze Button
        st.markdown('<div class="reanalyze-btn-container">', unsafe_allow_html=True)
        if st.button("🔄 Re-Analyze Image", use_container_width=True):
            st.session_state.analysis_done = False
            st.session_state.current_analysis = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="result-section">
            <div class="diag-icon-circ"><i class="fa-solid fa-stethoscope" style="font-size: 32px; color: #0D9488;"></i></div>
            <p class="diag-label">Predicted Diagnosis</p>
            <h1 class="diag-value">{res["class"]}</h1>
            <div class="conf-pill">Confidence Score</div>
            <h2 class="conf-score">{res["confidence"]*100:.2f}%</h2>
            <p class="res-footer" style="margin-bottom: 24px;">Based on our AI model analysis of the uploaded OCT image.</p>
        </div>
        """, unsafe_allow_html=True)

        # Buttons directly below the result text
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("💬 Chat with AI", key="res_chat", use_container_width=True, type="primary"):
                st.session_state.last_prediction = res["class"]
                st.session_state.active_page = "Chatbot"
                st.switch_page("user_pages/4_Chatbot.py")
        with btn_col2:
            if st.button("📸 Analyze Another", key="res_new", use_container_width=True):
                st.session_state.analysis_done = False
                st.session_state.current_analysis = None
                st.session_state.uploaded_file_obj = None
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ DISTRIBUTION ROW ------------------
    st.markdown("""
    <div class="custom-card">
        <div class="card-title-row">
            <i class="fa-solid fa-chart-simple card-icon"></i>
            <h3 class="card-title">Confidence Distribution</h3>
        </div>
    """, unsafe_allow_html=True)

    colors = {"CNV": "#3B82F6", "DME": "#0D9488", "Drusen": "#F43F5E", "Normal": "#8B5CF6"}
    
    for label, val in res["probabilities"].items():
        val_pct = val * 100
        color = colors.get(label, "#64748B")
        st.markdown(f"""
        <div class="dist-row">
            <div class="dist-label">{label}</div>
            <div class="dist-bar-bg"><div class="dist-bar-fill" style="width: {val_pct}%; background: {color};"></div></div>
            <div class="dist-val" style="color: {color};">{val_pct:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------ FOOTER ------------------
# ------------------ DISEASE REFERENCE SECTION ------------------
st.markdown("<br><br><hr style='border-color: #E2E8F0; opacity: 0.5;'><br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h2 style="font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; color: #1E293B;">Diagnostic Reference Guide</h2>
    <p style="font-family: 'DM Sans', sans-serif; color: #64748B; font-size: 16px;">Understanding the retinal conditions analyzed by our AI system</p>
</div>

<style>
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 20px;
        margin-bottom: 50px;
    }
    .info-card {
        background: white;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #F1F5F9;
        transition: all 0.3s ease;
    }
    .info-card:hover {
        border-color: #CCFBF1;
        background: #F0FDFA;
        transform: translateY(-5px);
    }
    .info-icon {
        width: 45px;
        height: 45px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 16px;
    }
    .ic-cnv { background: #FEE2E2; color: #DC2626; }
    .ic-dme { background: #FEF3C7; color: #D97706; }
    .ic-drusen { background: #E0F2FE; color: #0284C7; }
    .ic-normal { background: #DCFCE7; color: #16A34A; }
    
    .info-title {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 16px;
        color: #1E293B;
        margin: 0 0 8px 0;
    }
    .info-text {
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
        color: #64748B;
        line-height: 1.5;
        margin: 0;
    }
</style>

<div class="info-grid">
    <div class="info-card">
        <div class="info-icon ic-cnv"><i class="fa-solid fa-vial-circle-check"></i></div>
        <h4 class="info-title">CNV</h4>
        <p class="info-text">Choroidal Neovascularization involves new blood vessel growth through the Bruch membrane. A major cause of visual loss.</p>
    </div>
    <div class="info-card">
        <div class="info-icon ic-dme"><i class="fa-solid fa-droplet"></i></div>
        <h4 class="info-title">DME</h4>
        <p class="info-text">Diabetic Macular Edema is fluid accumulation in the macula due to leaking blood vessels in diabetic patients.</p>
    </div>
    <div class="info-card">
        <div class="info-icon ic-drusen"><i class="fa-solid fa-circle-nodes"></i></div>
        <h4 class="info-title">Drusen</h4>
        <p class="info-text">Yellow deposits under the retina. While not causing AMD directly, they significantly increase the risk of development.</p>
    </div>
    <div class="info-card">
        <div class="info-icon ic-normal"><i class="fa-solid fa-eye"></i></div>
        <h4 class="info-title">Normal</h4>
        <p class="info-text">A healthy retinal structure with organized cellular layers and no fluid, swelling, or abnormal deposits present.</p>
    </div>
</div>

<div style="background: #F8FAFC; padding: 30px; border-radius: 20px; border: 1px solid #E2E8F0; text-align: center;">
    <p style="color: #64748B; font-size: 13px; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">Medical Disclaimer</p>
    <p style="color: #94A3B8; font-size: 14px; line-height: 1.6; max-width: 800px; margin: 0 auto;">
        This analysis is generated by an Artificial Intelligence model trained on medical image datasets. It is intended for educational and informational purposes only and is <b>not a substitute for professional medical advice, diagnosis, or treatment.</b> Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
    </p>
</div>
<br><br>
""", unsafe_allow_html=True)