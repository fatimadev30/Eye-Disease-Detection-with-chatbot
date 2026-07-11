import streamlit as st
import pandas as pd
import sys
import os
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import render_medical_disclaimer, require_login, check_admin_access
from db.database import get_connection
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
if not check_admin_access():
    st.error("Access Denied. Administrator privileges required.")
    st.stop()

# ------------------ CUSTOM CSS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap');

    .stApp { background-color: #F8FAFC !important; }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:not(:first-of-type) {
        background: white;
        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #F1F5F9 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:not(:first-of-type):hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(13, 148, 136, 0.1);
        border-color: #99F6E4 !important;
    }
    .img-container {
        width: 180px;
        height: 180px;
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid #F1F5F9;
        flex-shrink: 0;
    }
    .img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .data-container {
        flex-grow: 1;
    }
    .diag-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 100px;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-cnv { background: #FEE2E2; color: #DC2626; }
    .badge-dme { background: #FEF3C7; color: #D97706; }
    .badge-drusen { background: #E0F2FE; color: #0284C7; }
    .badge-normal { background: #DCFCE7; color: #16A34A; }
    
    .date-text {
        font-family: 'DM Sans', sans-serif;
        color: #64748B;
        font-size: 14px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .user-text {
        font-family: 'DM Sans', sans-serif;
        color: #0D9488;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .diag-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 24px;
        color: #1E293B;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .conf-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 12px;
    }
    .conf-bar-bg {
        width: 200px;
        height: 8px;
        background: #F1F5F9;
        border-radius: 100px;
        overflow: hidden;
    }
    .conf-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #0D9488, #2DD4BF);
        border-radius: 100px;
    }
    .conf-val {
        font-size: 14px;
        font-weight: 700;
        color: #0D9488;
    }
    
    .delete-btn-container {
        flex-shrink: 0;
    }
    
    .header-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 700;
        font-size: 42px;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .header-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 18px;
        color: #64748B;
        margin-bottom: 48px;
    }

    /* RESPONSIVE ADJUSTMENTS */
    @media (max-width: 768px) {
        .history-card {
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 16px !important;
            padding: 16px !important;
        }
        .img-container {
            width: 100% !important;
            height: 220px !important;
        }
        .diag-title { font-size: 20px !important; }
        .conf-bar-bg { width: 100% !important; }
        .header-title { font-size: 32px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ------------------ DATA FETCH ------------------
conn = get_connection()
query = '''
    SELECT p.id, p.timestamp, p.predicted_class, p.confidence, u.file_path, us.username, us.name
    FROM predictions p
    JOIN uploads u ON p.upload_id = u.id
    JOIN users us ON p.user_id = us.id
    ORDER BY p.timestamp DESC
'''
df = pd.read_sql_query(query, conn)
conn.close()

# ------------------ HEADER ------------------
st.markdown('<h1 class="header-title">All Users Scan History</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Review and manage past OCT scan analyses of all users</p>', unsafe_allow_html=True)

if df.empty:
    st.info("No predictions found in the database.")
else:
    for idx, row in df.iterrows():
        # Get class specific badge class
        cls_lower = row['predicted_class'].lower()
        badge_class = f"badge-{cls_lower}" if cls_lower in ["cnv", "dme", "drusen", "normal"] else "badge-normal"
        
        # Formatting
        date_str = pd.to_datetime(row['timestamp']).strftime('%B %d, %Y • %I:%M %p')
        conf_pct = row['confidence'] * 100
        user_display = row['name'] if row['name'] else row['username']
        
        # UI Card Wrapper
        with st.container(border=True):
            c1, c2, c3 = st.columns([1.2, 3, 0.5], vertical_alignment="center")
            
            with c1:
                b64 = get_image_base64(row['file_path'])
                if b64:
                    st.markdown(f'<div class="img-container"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)
                else:
                    st.error("Image Missing")
            
            with c2:
                st.markdown(f"""
                <div class="data-container">
                    <div class="user-text"><i class="fa-solid fa-user"></i> User: {user_display}</div>
                    <div class="date-text"><i class="fa-solid fa-calendar-day"></i> {date_str}</div>
                    <div class="diag-badge {badge_class}">{row['predicted_class']}</div>
                    <div class="diag-title">{row['predicted_class']} Detected</div>
                    <div class="conf-row">
                        <div class="conf-val">{conf_pct:.2f}% Confidence</div>
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill" style="width: {conf_pct}%;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Fetch chat history for this specific prediction
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT role, message, timestamp FROM chat_history WHERE prediction_id = ? ORDER BY timestamp ASC", (row['id'],))
                chats = cursor.fetchall()
                conn.close()
                
                # Chat History Popover
                if chats:
                    with st.popover("💬 View Chat Consultation"):
                        st.markdown(f'<h4 style="color: #0d9488; font-family: Syne, sans-serif;">Consultation for {row["predicted_class"]}</h4>', unsafe_allow_html=True)
                        st.markdown('<div style="background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; max-height: 550px; overflow-y: auto;">', unsafe_allow_html=True)
                        for chat in chats:
                            color = "#0d9488" if chat['role'] == "assistant" else "#1e293b"
                            role_name = "AI ASSISTANT" if chat['role'] == "assistant" else f"USER ({user_display.upper()})"
                            st.markdown(f"""
                            <div style="margin-bottom: 12px; border-left: 3px solid {color}; padding-left: 10px;">
                                <p style="font-size: 11px; font-weight: 800; color: {color}; margin: 0;">{role_name}</p>
                                <p style="font-size: 14px; color: #334155; margin: 4px 0;">{chat['message']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color: #94A3B8; font-size: 12px; margin-top: 10px; font-style: italic;">No chat consultation for this scan.</p>', unsafe_allow_html=True)
            
            with c3:
                st.markdown('<div class="delete-btn-container">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete this entry"):
                    if delete_prediction(row['id']):
                        st.success("Deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete.")
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
