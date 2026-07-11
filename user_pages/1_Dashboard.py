import streamlit as st
import pandas as pd
import sys
import os
import base64
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import require_login
from db.database import get_connection

require_login()

# ------------------ CUSTOM CSS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap');
    
    .stApp { background-color: #F8FAFC !important; }
    
    .hero-container {
        position: relative;
        width: 100%;
        height: 220px;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 40px;
        background: linear-gradient(90deg, #F8FAFC 0%, #F0FDFA 100%);
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        border: 1px solid #E2E8F0;
        display: flex;
        align-items: center;
        padding: 0 50px;
    }
    
    .hero-bg {
        position: absolute;
        top: -50px; right: 0; 
        height: 320px; 
        object-fit: contain;
        object-position: right;
        z-index: 1;
        mask-image: linear-gradient(to left, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 100%);
        -webkit-mask-image: linear-gradient(to left, rgba(0,0,0,1) 50%, rgba(0,0,0,0) 100%);
    }
    
    .hero-overlay {
        display: none;
    }
    
    .hero-content {
        position: relative;
        z-index: 3;
        color: #0F172A;
        max-width: 550px;
    }
    
    .hero-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        font-size: 38px;
        margin: 0 0 10px 0;
        line-height: 1.1;
        color: #0D9488;
    }
    
    .hero-title span {
        color: #0D9488;
    }
    
    .hero-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        color: #64748B;
        margin: 0 0 25px 0;
        line-height: 1.6;
    }
    
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #F1F5F9;
        text-align: center;
        transition: transform 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(13, 148, 136, 0.15);
        border-color: #99F6E4;
    }
    
    .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #F0FDFA;
        color: #0D9488;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin-bottom: 15px;
    }
    
    .stat-value {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        font-size: 36px;
        color: #0F172A;
        margin: 0;
    }
    
    .stat-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        margin-top: 5px;
    }
    
    .recent-scans-header {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        font-size: 24px;
        color: #0F172A;
        margin-bottom: 20px;
        margin-top: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .badge-cnv { background: #FEE2E2; color: #DC2626; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;}
    .badge-dme { background: #FEF3C7; color: #D97706; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;}
    .badge-drusen { background: #E0F2FE; color: #0284C7; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;}
    .badge-normal { background: #DCFCE7; color: #16A34A; padding: 4px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;}
</style>
""", unsafe_allow_html=True)

# ------------------ IMAGE ENCODING ------------------
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        return ""

img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "dashboard_hero.png")
hero_b64 = get_base64_image(img_path)

# ------------------ HERO SECTION ------------------
st.markdown(f"""
<div class="hero-container">
    <img src="data:image/png;base64,{hero_b64}" class="hero-bg" alt="Eye Disease Detection Background">
    <div class="hero-content">
        <h1 class="hero-title">Welcome back, <span>{st.session_state.username}!</span></h1>
        <p class="hero-subtitle">Your AI-powered platform for accurate OCT scan analysis<br>and eye health monitoring.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------ DATA FETCHING ------------------
conn = get_connection()
cursor = conn.cursor()

user_id = st.session_state.user_id

# 1. Total Scans
cursor.execute("SELECT COUNT(*) as count FROM predictions WHERE user_id = ?", (user_id,))
total_scans = cursor.fetchone()['count']

# 2. Average Confidence
cursor.execute("SELECT AVG(confidence) as avg FROM predictions WHERE user_id = ?", (user_id,))
avg_conf_raw = cursor.fetchone()['avg']
avg_conf = f"{avg_conf_raw * 100:.1f}%" if avg_conf_raw else "0%"

# 3. Chat Messages
cursor.execute("SELECT COUNT(*) as count FROM chat_history WHERE user_id = ?", (user_id,))
total_chats = cursor.fetchone()['count']

# 4. Recent Activity
cursor.execute("SELECT p.predicted_class, p.confidence, p.timestamp FROM predictions p WHERE user_id = ? ORDER BY p.timestamp DESC LIMIT 3", (user_id,))
recent_scans = cursor.fetchall()

conn.close()

# ------------------ QUICK STATS ------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon"><i class="fa-solid fa-microscope"></i></div>
        <h3 class="stat-value">{total_scans}</h3>
        <p class="stat-label">Total OCT Scans</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon"><i class="fa-solid fa-bullseye"></i></div>
        <h3 class="stat-value">{avg_conf}</h3>
        <p class="stat-label">Avg. AI Confidence</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon"><i class="fa-solid fa-message"></i></div>
        <h3 class="stat-value">{total_chats}</h3>
        <p class="stat-label">AI Consultations</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------ RECENT SCANS & ACTIONS ------------------
sc1, sc2 = st.columns([2, 1])

with sc1:
    st.markdown('<div class="recent-scans-header">Recent Scans</div>', unsafe_allow_html=True)
    if recent_scans:
        for scan in recent_scans:
            cls_lower = scan['predicted_class'].lower()
            badge_class = f"badge-{cls_lower}" if cls_lower in ["cnv", "dme", "drusen", "normal"] else "badge-normal"
            date_str = pd.to_datetime(scan['timestamp']).strftime('%b %d, %Y • %I:%M %p')
            
            with st.container(border=True):
                colA, colB, colC = st.columns([2,1,1.5], vertical_alignment="center")
                with colA:
                    st.markdown(f'<span class="{badge_class}">{scan["predicted_class"]}</span>', unsafe_allow_html=True)
                with colB:
                    st.markdown(f"**{scan['confidence']*100:.1f}%**", unsafe_allow_html=True)
                with colC:
                    st.markdown(f"<span style='color: #64748B; font-size: 14px;'><i class='fa-regular fa-clock'></i> {date_str}</span>", unsafe_allow_html=True)
    else:
        st.info("You haven't performed any scans yet. Start a new scan to see your history here.")

with sc2:
    st.markdown('<div class="recent-scans-header">Quick Actions</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <i class="fa-solid fa-cloud-arrow-up" style="font-size: 40px; color: #0D9488; margin-bottom: 15px;"></i>
            <h4 style="font-family: 'DM Sans', sans-serif; font-weight: 700; color: #0F172A; margin:0 0 10px 0;">New OCT Scan</h4>
            <p style="font-family: 'DM Sans', sans-serif; font-size: 14px; color: #64748B; margin:0 0 20px 0;">Upload a new image for instant AI analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Scan", use_container_width=True, type="primary"):
            st.session_state.active_page = "Upload"
            st.switch_page("user_pages/2_Upload_Analyze.py")

st.markdown("<br><br>", unsafe_allow_html=True)
