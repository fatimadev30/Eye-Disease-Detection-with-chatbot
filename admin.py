import streamlit as st
import os
import sys

# Ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import load_css
from auth.security import init_session_state, authenticate_user, login, logout
from db.database import init_db

# Page config MUST be the first Streamlit command
st.set_page_config(page_title="EDD Admin Portal", page_icon="🛡️", layout="wide")

# Initialize database tables if they don't exist
init_db()

# Load global CSS
load_css()

# Initialize session state
init_session_state()

# ----------------- GLOBAL SIDEBAR HIDING -----------------
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        section[data-testid="stSidebar"] {display: none !important;}
        .stApp > header { display: none !important; }
        
        /* Fix padding for main content since sidebar is hidden */
        .main .block-container { padding-top: 2rem !important; }
    </style>
""", unsafe_allow_html=True)

def admin_login_page():
    # Use columns to center the card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #0F172A; font-family: DM Sans, sans-serif; font-weight: 800;'>🛡️ Admin Portal</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #DC2626; font-weight: bold;'>Authorized Personnel Only.</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.form("admin_login_form"):
                l_user = st.text_input("Admin Username")
                l_pass = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Secure Login", use_container_width=True)
                if submitted:
                    user_data = authenticate_user(l_user, l_pass)
                    if user_data:
                        if 'error' in user_data:
                            st.error(user_data['error'])
                        elif user_data['role'] != 'admin':
                            st.error("Access Denied. You do not have administrator privileges.")
                        else:
                            login(user_data)
                            st.success("Admin access granted!")
                            st.rerun()
                    else:
                        st.error("Invalid username or password.")

if not st.session_state.logged_in:
    admin_login_page()
else:
    # Ensure role is admin, otherwise block.
    if st.session_state.role != 'admin':
        st.error("Access Denied. You do not have administrator privileges.")
        if st.button("Logout"):
            logout()
            st.rerun()
        st.stop()

    if 'popover_key' not in st.session_state:
        st.session_state.popover_key = 0

    # Apply ULTRA STABLE styling for the navbar
    st.markdown("""
    <style>
        /* Base Navbar Block Styling (Desktop & Mobile) */
        div[data-testid="stHorizontalBlock"]:has(#desktop-nav-id),
        div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) {
            position: fixed;
            top: 10px !important;
            left: 0 !important;
            right: 0 !important;
            height: 70px;
            z-index: 999999;
            background: linear-gradient(135deg, #0D9488, #0F172A) !important;
            padding: 0 30px;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            border-radius: 15px !important;
            width: 100vw !important;
            margin: 0 !important;
        }
        
        .main .block-container { padding-top: 100px !important; }
        
        /* Navbar Buttons */
        div[data-testid="stHorizontalBlock"]:has(#desktop-nav-id) button,
        div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) button {
            background: transparent !important;
            color: white !important;
            border: none !important;
            box-shadow: none !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stHorizontalBlock"]:has(#desktop-nav-id) button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
        }
        
        div[data-testid="column"]:has(#active-btn) button {
            background: rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
        }

        button div p, button * {
            font-size: 15px !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
        }

        /* Visibility Logic */
        div[data-testid="stHorizontalBlock"]:has(#desktop-nav-id) { display: flex !important; }
        div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) { display: none !important; }

        @media (max-width: 1100px) {
            div[data-testid="stHorizontalBlock"]:has(#desktop-nav-id) { display: none !important; }
            div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) { display: flex !important; }
            
            div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) [data-testid="stPopover"] {
                position: absolute !important;
                right: 20px !important;
                top: 50% !important;
                transform: translateY(-50%) !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    pages = [
        st.Page("admin_pages/1_Admin_Dashboard.py", title="Dashboard"),
        st.Page("admin_pages/2_User_Management.py", title="Users"),
        st.Page("admin_pages/4_All_User_History.py", title="History"),
        st.Page("admin_pages/3_Audit_Logs.py", title="Audit Logs"),
    ]

    pg = st.navigation(pages, position="hidden")

    # ---------------- NAVBAR ---------------- #
    pages_titles = ["Dashboard", "Users", "History", "Audit Logs"]
    current_page_title = st.session_state.get('active_admin_page', 'Dashboard')

    with st.container():
        # 1. MOBILE NAVBAR
        m_cols = st.columns([9, 1], vertical_alignment="center")
        with m_cols[0]:
            st.markdown('<div id="mobile-nav-id"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="height: 100%; display: flex; align-items: center; padding-left: 10px;">
                <span style="font-size:1.7rem;">🛡️</span>
                <span style="color:white; font-weight:800; font-size:1.3rem; margin-left: 10px;">EDD Admin</span>
            </div>
            """, unsafe_allow_html=True)
        with m_cols[1]:
            with st.popover("☰", key=f"nav_popover_{st.session_state.popover_key}"):
                for i, title in enumerate(pages_titles):
                    if st.button(title, key=f"m_nav_{title}", use_container_width=True):
                        st.session_state.active_admin_page = title
                        st.session_state.popover_key += 1
                        st.switch_page(pages[i])
                st.markdown("<hr>", unsafe_allow_html=True)
                if st.button("Logout", key="m_nav_logout", use_container_width=True):
                    logout()
                    st.rerun()

        # 2. DESKTOP NAVBAR
        d_cols = st.columns([2.5, 1.2, 1.2, 1.2, 1.2, 1], vertical_alignment="center")
        with d_cols[0]:
            st.markdown('<div id="desktop-nav-id"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="display:flex; align-items:center; margin-top: -27px;">
                <span style="font-size:1.1rem; margin-right: 10px;">🛡️</span>
                <span style="color:white; font-size:1.7rem; font-weight:800; white-space: nowrap;">EDD Admin</span>
            </div>
            """, unsafe_allow_html=True)
        
        for i, title in enumerate(pages_titles):
            with d_cols[i+1]:
                if current_page_title == title:
                    st.markdown('<div id="active-btn"></div>', unsafe_allow_html=True)
                if st.button(title, key=f"nav_{title}", use_container_width=True):
                    st.session_state.active_admin_page = title
                    st.switch_page(pages[i])
        
        with d_cols[5]:
            if st.button("Logout", key="nav_logout", use_container_width=True):
                logout()
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    pg.run()
