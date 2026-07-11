import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import require_login
from db.database import get_connection

require_login()

# ------------------ PAGE CONFIG ------------------
# Page config handled in app.py

# ------------------ CUSTOM CSS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

    .stApp { background-color: #F8FAFC !important; }
    
    .profile-hero {
        background: linear-gradient(135deg, #0D9488, #2DD4BF);
        padding: 60px 40px;
        border-radius: 24px;
        color: white;
        text-align: center;
        margin-bottom: -60px;
        position: relative;
        z-index: 1;
    }
    .profile-avatar {
        width: 120px;
        height: 120px;
        background: white;
        border-radius: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        color: #0D9488;
        margin: 0 auto 16px;
        border: 4px solid rgba(255,255,255,0.3);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .profile-name {
        font-family: 'DM Sans', sans-serif;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .profile-badge {
        background: rgba(255,255,255,0.2);
        padding: 4px 16px;
        border-radius: 100px;
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stats-container {
        display: flex;
        gap: 20px;
        margin: 0 20px 20px;
        position: relative;
        z-index: 2;
    }
    .stat-card {
        flex: 1;
        background: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #F1F5F9;
    }
    .stat-val {
        font-family: 'DM Sans', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
    }
    .stat-label {
        color: #64748B;
        font-size: 14px;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .details-card {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin: 0 40px;
        border: 1px solid #F1F5F9;
    }
    .details-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 1px solid #F1F5F9;
    }
    .info-row:last-child { border-bottom: none; }
    .info-label { color: #64748B; font-weight: 500; }
    .info-value { color: #1E293B; font-weight: 700; }

    /* RESPONSIVE ADJUSTMENTS */
    @media (max-width: 768px) {
        .profile-hero { padding: 40px 20px !important; }
        .profile-name { font-size: 24px !important; }
        .stats-container { flex-direction: column !important; margin: 0 10px 10px !important; }
        .stat-card { padding: 16px !important; }
        .details-card { margin: 0 10px !important; padding: 20px !important; }
        .info-row { flex-direction: column !important; gap: 4px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ------------------ DATA FETCH ------------------
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name, username, email, role, created_at FROM users WHERE id = ?", (st.session_state.user_id,))
user_info = cursor.fetchone()

# Get total uploads
cursor.execute("SELECT COUNT(*) as count FROM uploads WHERE user_id = ?", (st.session_state.user_id,))
uploads_count = cursor.fetchone()['count']

# Get last analysis date
cursor.execute("SELECT timestamp FROM predictions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (st.session_state.user_id,))
last_analysis = cursor.fetchone()
last_analysis_date = pd.to_datetime(last_analysis['timestamp']).strftime('%b %d, %Y') if last_analysis else "Never"

conn.close()

if user_info:
    display_name = user_info['name'] if user_info['name'] else user_info['username']
    
    # Hero Section
    st.markdown(f"""
    <div class="profile-hero">
        <div class="profile-avatar"><i class="fa-solid fa-user-doctor"></i></div>
        <div class="profile-name">{display_name}</div>
        <div class="profile-badge">{user_info['role']} Account</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-val">{uploads_count}</div>
            <div class="stat-label">Total Scans</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{last_analysis_date}</div>
            <div class="stat-label">Last Analysis</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{pd.to_datetime(user_info['created_at']).strftime('%b %Y')}</div>
            <div class="stat-label">Member Since</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Details Section
    with st.container():
        st.markdown(f"""
        <div class="details-card">
            <div class="details-title"><i class="fa-solid fa-id-card"></i> Account Details</div>
            <div class="info-row">
                <div class="info-label">Full Name</div>
                <div class="info-value">{user_info['name'] if user_info['name'] else 'Not Set'}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Username</div>
                <div class="info-value">@{user_info['username']}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Email Address</div>
                <div class="info-value">{user_info['email']}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Account Security</div>
                <div class="info-value">Verified</div>
            </div>
            <div style="margin-top: 32px;">
                <p style="color:#64748B; font-size: 14px;">
                    <i class="fa-solid fa-circle-info"></i> To update your account information, please contact the administrator.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
