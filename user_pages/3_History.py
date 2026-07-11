import streamlit as st
import pandas as pd
import sys
import os
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import render_medical_disclaimer, require_login
from db.database import get_connection, get_chat_history
import base64
from io import BytesIO

def get_image_base64(image_path):
    try:
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        return None

# FOOLPROOF DELETE FUNCTION (Bypasses Import Errors)
def delete_prediction(prediction_id):
    """Deletes a prediction record and its associated upload entry."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get upload_id first
        cursor.execute("SELECT upload_id FROM predictions WHERE id = ?", (prediction_id,))
        res = cursor.fetchone()
        if res:
            upload_id = res['upload_id']
            # Delete prediction
            cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
            # Delete upload
            cursor.execute("DELETE FROM uploads WHERE id = ?", (upload_id,))
            conn.commit()
            return True
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return False
    finally:
        conn.close()
    return False

require_login()

# ------------------ PAGE CONFIG ------------------
# Page config handled in app.py

# ------------------ CUSTOM CSS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap');

    .stApp { background-color: #F8FAFC !important; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.3s ease !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px) !important;
        border-color: #0D9488 !important;
        box-shadow: 0 12px 30px rgba(13, 148, 136, 0.1) !important;
    }

    /* THE FIX: TARGETING THE POPOVER BUTTON SPECIFICALLY */
    button[data-testid="stBaseButton-secondary"]:has(div p:contains("View Chat Consultation")),
    div[data-testid="stPopover"] > button {
        background-color: transparent !important;
        background: transparent !important;
        border: 2px solid #0D9488 !important;
        color: #0D9488 !important;
        border-radius: 12px !important;
        padding: 8px 24px !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
        margin-top: 15px !important;
        width: fit-content !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #0D9488 !important;
        background: #0D9488 !important;
        color: white !important;
    }

    div[data-testid="stPopover"] > button div p {
        color: #0D9488 !important;
        font-weight: 800 !important;
    }

    div[data-testid="stPopover"] > button:hover div p {
        color: white !important;
    }

    /* All buttons in the card should be outlined */
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        background-color: transparent !important;
        border: 2px solid #0D9488 !important;
        color: #0D9488 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        background-color: #0D9488 !important;
        color: white !important;
    }

    /* Date and Title Styles */
    .date-text { color: #64748B; font-size: 14px; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; font-weight: 500; }
    .diag-title { font-size: 24px; color: #1E293B; font-weight: 700; margin-bottom: 8px; font-family: 'Syne', sans-serif; }
    
    .conf-row { display: flex; align-items: center; gap: 12px; margin-top: 12px; }
    .conf-bar-bg { width: 200px; height: 8px; background: #F1F5F9; border-radius: 100px; overflow: hidden; }
    .conf-bar-fill { height: 100%; background: linear-gradient(90deg, #0D9488, #2DD4BF); border-radius: 100px; }
    .conf-val { font-size: 14px; font-weight: 700; color: #0D9488; }
    
    .header-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 42px; color: #0F172A; margin-bottom: 8px; }
    .header-subtitle { font-family: 'DM Sans', sans-serif; font-size: 18px; color: #64748B; margin-bottom: 48px; }

    .img-container {
        width: 180px; height: 180px; border-radius: 16px; overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    .img-container img { width: 100%; height: 100%; object-fit: cover; }
    
    .diag-badge {
        display: inline-block; padding: 4px 12px; border-radius: 100px;
        font-size: 12px; font-weight: 800; margin-bottom: 10px;
        text-transform: uppercase; border: 1.5px solid currentColor;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ DATA FETCH ------------------
conn = get_connection()
query = '''
    SELECT p.id, p.timestamp, p.predicted_class, p.confidence, u.file_path
    FROM predictions p
    JOIN uploads u ON p.upload_id = u.id
    WHERE p.user_id = ?
    ORDER BY p.timestamp DESC
'''
df = pd.read_sql_query(query, conn, params=(st.session_state.user_id,))
conn.close()

# ------------------ HEADER ------------------
st.markdown('<h1 class="header-title">Scan History</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Review and manage your past OCT scan analyses</p>', unsafe_allow_html=True)

render_medical_disclaimer()

if df.empty:
    st.info("No predictions found. Go to 'Upload & Analyze' to get started.")
else:
    for idx, row in df.iterrows():
        cls_lower = row['predicted_class'].lower()
        badge_colors = {"cnv": "#DC2626", "dme": "#D97706", "drusen": "#0284C7", "normal": "#16A34A"}
        color = badge_colors.get(cls_lower, "#16A34A")
        
        date_str = pd.to_datetime(row['timestamp']).strftime('%B %d, %Y • %I:%M %p')
        conf_pct = row['confidence'] * 100
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([1.2, 3, 0.5], vertical_alignment="center")
            
            with c1:
                b64 = get_image_base64(row['file_path'])
                if b64:
                    st.markdown(f'<div class="img-container"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown(f"""
                <div class="data-container">
                    <div class="date-text"><i class="fa-solid fa-calendar-day"></i> {date_str}</div>
                    <div class="diag-badge" style="color: {color}; border-color: {color};">{row['predicted_class']}</div>
                    <div class="diag-title">{row['predicted_class']} Detected</div>
                    <div class="conf-row">
                        <div class="conf-val">{conf_pct:.2f}% Confidence</div>
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill" style="width: {conf_pct}%;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                chats = get_chat_history(st.session_state.user_id, row['id'])
                if chats:
                    with st.popover("💬 View Chat Consultation"):
                        st.markdown(f'<h4 style="color: #0d9488; font-family: Syne, sans-serif;">Consultation for {row["predicted_class"]}</h4>', unsafe_allow_html=True)
                        st.markdown('<div style="background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
                        for chat in chats:
                            c = "#0d9488" if chat['role'] == "assistant" else "#1e293b"
                            st.markdown(f"""
                            <div style="margin-bottom: 12px; border-left: 3px solid {c}; padding-left: 10px;">
                                <p style="font-size: 11px; font-weight: 800; color: {c}; margin: 0;">{chat['role'].upper()}</p>
                                <p style="font-size: 14px; color: #334155; margin: 4px 0;">{chat['message']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if st.button("🔄 Continue Consultation", key=f"cont_{row['id']}", use_container_width=True):
                            st.session_state.last_prediction_id = row['id']
                            st.session_state.last_prediction = row['predicted_class']
                            st.session_state.active_page = "Chatbot"
                            st.session_state.messages = [{"role": c['role'], "content": c['message']} for c in chats]
                            st.switch_page("user_pages/4_Chatbot.py")
                else:
                    st.markdown('<p style="color: #94A3B8; font-size: 12px; margin-top: 10px; font-style: italic;">No chat consultation.</p>', unsafe_allow_html=True)
                    if st.button("💬 Start Consultation", key=f"start_{row['id']}"):
                        st.session_state.last_prediction_id = row['id']
                        st.session_state.last_prediction = row['predicted_class']
                        st.session_state.active_page = "Chatbot"
                        st.session_state.messages = []
                        st.switch_page("user_pages/4_Chatbot.py")
            
            with c3:
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete"):
                    if delete_prediction(row['id']):
                        st.success("Deleted!")
                        st.rerun()

st.markdown("<br><br>", unsafe_allow_html=True)
