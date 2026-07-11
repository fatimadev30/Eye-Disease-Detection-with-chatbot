import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import require_login, check_admin_access
from db.database import get_connection

require_login()
if not check_admin_access():
    st.error("Access Denied. Administrator privileges required.")
    st.stop()

# ------------------ CUSTOM CSS ------------------
st.markdown(r"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    
    .header-title {
        font-family: 'DM Sans', sans-serif;
        font-weight: 800;
        font-size: 36px;
        color: #0F172A;
        margin-bottom: 8px;
    }
    .header-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        color: #64748B;
        margin-bottom: 30px;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:not(:first-of-type) {
        background: white;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:not(:first-of-type):hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(13, 148, 136, 0.15);
        border-color: #99F6E4 !important;
    }
    
    .avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0D9488, #2DD4BF);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .user-info {
        flex-grow: 1;
    }
    .user-name {
        font-family: 'DM Sans', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #1E293B;
        margin: 0 0 4px 0;
    }
    .user-email {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: #64748B;
        margin: 0 0 8px 0;
    }
    .user-meta {
        font-family: 'DM Sans', sans-serif;
        font-size: 12px;
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-active { background: #DCFCE7; color: #16A34A; }
    .status-inactive { background: #FEE2E2; color: #DC2626; }
    .status-admin { background: #E0F2FE; color: #0284C7; }

    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        font-family: 'DM Sans', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: #64748B;
        border-bottom: 3px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #0D9488 !important;
        border-bottom: 3px solid #0D9488 !important;
        background: rgba(13, 148, 136, 0.05) !important;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<h1 class="header-title">👥 User Management</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">View, activate, and deactivate user accounts</p>', unsafe_allow_html=True)

conn = get_connection()

# ------------------ ACTIONS ------------------
def toggle_user_status(user_id, current_status):
    if user_id == st.session_state.user_id:
        st.error("You cannot deactivate your own account.")
        return
        
    new_status = 0 if current_status == 1 else 1
    action = 'activate' if new_status == 1 else 'deactivate'
    
    c = conn.cursor()
    c.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
    
    action_text = f"{action.capitalize()}d user {user_id}"
    c.execute(
        "INSERT INTO audit_logs (admin_id, action, target_user_id) VALUES (?, ?, ?)",
        (st.session_state.user_id, action_text, user_id)
    )
    conn.commit()
    st.toast(f"Successfully {action}d user!", icon="✅")

# ------------------ DATA FETCH ------------------
try:
    users_df = pd.read_sql_query("SELECT id, name, username, email, role, is_active, created_at FROM users ORDER BY created_at DESC", conn)
except:
    # Fallback if name column is somehow missing
    users_df = pd.read_sql_query("SELECT id, username, email, role, is_active, created_at FROM users ORDER BY created_at DESC", conn)
    users_df['name'] = users_df['username']

# ------------------ RENDER USERS ------------------
def render_user_card(row):
    # Prepare Data
    initial = row['name'][0].upper() if pd.notnull(row['name']) and len(row['name']) > 0 else row['username'][0].upper()
    display_name = row['name'] if pd.notnull(row['name']) and len(row['name']) > 0 else row['username']
    date_str = pd.to_datetime(row['created_at']).strftime('%b %d, %Y')
    
    is_active = row['is_active'] == 1
    status_text = "Active" if is_active else "Inactive"
    status_class = "status-active" if is_active else "status-inactive"
    if row['role'] == 'admin':
        status_class = "status-admin"
        status_text = "Admin"
        
    # Create Card
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 4, 1.5], vertical_alignment="center")
        
        with c1:
            st.markdown(f'<div class="avatar">{initial}</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="user-info">
                <p class="user-name">{display_name} <span style="font-size: 14px; font-weight: normal; color: #64748B;">(@{row['username']})</span></p>
                <p class="user-email"><i class="fa-solid fa-envelope"></i> {row['email']}</p>
                <div class="user-meta">
                    <span><i class="fa-solid fa-calendar"></i> Joined: {date_str}</span>
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c3:
            if row['role'] != 'admin':
                if is_active:
                    if st.button("🚫 Deactivate", key=f"btn_{row['id']}", use_container_width=True):
                        toggle_user_status(row['id'], 1)
                        st.rerun()
                else:
                    if st.button("✅ Activate", key=f"btn_{row['id']}", type="primary", use_container_width=True):
                        toggle_user_status(row['id'], 0)
                        st.rerun()
            else:
                st.markdown("<div style='text-align: center; color: #94A3B8; font-size: 14px; padding-top: 10px;'>Protected</div>", unsafe_allow_html=True)


if users_df.empty:
    st.info("No users found.")
else:
    tab1, tab2 = st.tabs(["👥 Registered Users", "🛡️ Administrators"])
    
    with tab1:
        user_rows = users_df[users_df['role'] == 'user']
        if user_rows.empty:
            st.info("No registered users found.")
        else:
            for _, row in user_rows.iterrows():
                render_user_card(row)
                
    with tab2:
        admin_rows = users_df[users_df['role'] == 'admin']
        if admin_rows.empty:
            st.info("No administrators found.")
        else:
            for _, row in admin_rows.iterrows():
                render_user_card(row)

conn.close()
st.markdown("<br><br>", unsafe_allow_html=True)
