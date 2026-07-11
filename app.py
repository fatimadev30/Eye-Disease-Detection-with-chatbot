import streamlit as st
import os

# Set Legacy Keras for compatibility with TF 2.16+
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import load_css
from auth.security import init_session_state, authenticate_user, register_user, login, logout
from db.database import init_db

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Eye Disease Detection", page_icon="👁️", layout="wide")

init_db()
load_css()
init_session_state()

# ----------------- GLOBAL UI FIXES (SIDEBAR & TABS & BUTTONS) -----------------
st.markdown("""
    <style>
        /* Hide sidebar and header globally */
        [data-testid="collapsedControl"] {display: none;}
        section[data-testid="stSidebar"] {display: none !important;}
        .stApp > header { display: none !important; }
        
        /* Fix padding for main content */
        .main .block-container { padding-top: 2rem !important; }

        /* Login/Register Tabs Styling - REINFORCED */
        div[data-baseweb="tab-list"] {
            gap: 15px !important;
            background-color: transparent !important;
            border-bottom: none !important;
        }
        
        button[data-baseweb="tab"] {
            border: 2px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 10px 30px !important;
            background-color: transparent !important;
            color: #64748B !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            border-color: #0D9488 !important;
            color: #0D9488 !important;
            background-color: transparent !important;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.1) !important;
        }
        
        div[data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* OUTLINED SUBMIT BUTTONS for Login/Register - REINFORCED */
        div[data-testid="stForm"] button,
        div[data-testid="stFormSubmitButton"] button {
            background: transparent !important;
            background-color: transparent !important;
            color: #0D9488 !important;
            border: 2px solid #0D9488 !important;
            border-radius: 12px !important;
            font-weight: 800 !important;
            padding: 12px 24px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
            box-shadow: none !important;
        }

        div[data-testid="stForm"] button:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #0D9488 !important;
            color: white !important;
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.2) !important;
            transform: translateY(-2px) !important;
        }
    </style>
""", unsafe_allow_html=True)

if 'popover_key' not in st.session_state:
    st.session_state.popover_key = 0

# ---------------- LOGIN ---------------- #
def login_register_page():
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        with st.container(border=True):
            st.markdown(
                "<h2 style='text-align:center; color:#0F172A; font-family: DM Sans, sans-serif; font-weight: 800;'>👁️ Eye Detection</h2>",
                unsafe_allow_html=True
            )

            tab1, tab2 = st.tabs(["Login","Register"])

            # LOGIN
            with tab1:
                with st.form("login"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")

                    if st.form_submit_button("Login", use_container_width=True):
                        data = authenticate_user(u, p)
                        if data:
                            login(data)
                            st.rerun()
                        else:
                            st.error("Invalid login")

            # REGISTER
            with tab2:
                with st.form("register"):
                    name = st.text_input("Full Name")
                    user = st.text_input("Username")
                    email = st.text_input("Email")
                    pw = st.text_input("Password", type="password")
                    cpw = st.text_input("Confirm Password", type="password")

                    if st.form_submit_button("Register", use_container_width=True):
                        if pw != cpw:
                            st.error("Passwords mismatch")
                        else:
                            if register_user(user, email, pw, role='user', name=name):
                                st.success("Registered")
                            else:
                                st.error("User exists")

# ---------------- MAIN ---------------- #
if not st.session_state.logged_in:
    login_register_page()

else:
    # ADMIN
    if st.session_state.role == 'admin':
        st.error("Admins use Admin Portal")
        if st.button("Logout"):
            logout()
            st.rerun()
        st.stop()

    # ---------------- NAVBAR STYLE (ULTRA STABLE) ---------------- #
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
    
    /* Navbar Buttons (Desktop & Mobile) */
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
        div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) { 
            display: flex !important;
        }

        /* ABSOLUTE POSITIONING FOR HAMBURGER */
        div[data-testid="stHorizontalBlock"]:has(#mobile-nav-id) [data-testid="stPopover"] {
            position: absolute !important;
            right: -200px !important; 
            top: 50% !important;
            transform: translateY(-50%) !important;
        }
    }

    /* INCREASE WIDTH OF MOBILE NAV POPOVER */
    div[data-testid="stPopoverBody"] {
        width: calc(100vw - 40px) !important;
        min-width: 320px !important;
        max-width: 500px !important;
        margin-left: auto !important;
        margin-right: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(13, 148, 136, 0.1) !important;
    }

    div[data-testid="stPopoverBody"] button {
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 20px !important;
        height: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- PAGES ---------------- #
    pages = [
        st.Page("user_pages/1_Dashboard.py", title="Dashboard"),
        st.Page("user_pages/2_Upload_Analyze.py", title="Upload"),
        st.Page("user_pages/3_History.py", title="History"),
        st.Page("user_pages/4_Chatbot.py", title="Chatbot"),
        st.Page("user_pages/6_Profile.py", title="Profile"),
    ]
    pg = st.navigation(pages, position="hidden")

    # ---------------- NAVBAR ---------------- #
    pages_titles = ["Dashboard", "Upload", "History", "Chatbot", "Profile"]
    current_page_title = st.session_state.get('active_page', 'Dashboard')

    with st.container():
        # 1. MOBILE/TABLET NAVBAR
        m_cols = st.columns([9, 1], vertical_alignment="center")
        with m_cols[0]:
            st.markdown('<div id="mobile-nav-id"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="height: 100%; display: flex; align-items: center; padding-left: 10px;">
                <span style="font-size:1.7rem;">👁️</span>
                <span style="color:white; font-weight:800; font-size:1.3rem; margin-left: 10px;">Eye Detection</span>
            </div>
            """, unsafe_allow_html=True)
        with m_cols[1]:
            with st.popover("☰", key=f"nav_popover_{st.session_state.popover_key}"):
                for i, title in enumerate(pages_titles):
                    if st.button(title, key=f"m_nav_{title}", use_container_width=True):
                        st.session_state.active_page = title
                        st.session_state.popover_key += 1
                        st.switch_page(pages[i])
                st.markdown("<hr>", unsafe_allow_html=True)
                if st.button("Logout", key="m_nav_logout", use_container_width=True):
                    logout()
                    st.rerun()

        # 2. DESKTOP NAVBAR
        d_cols = st.columns([2.5, 1.2, 1.2, 1.2, 1.2, 1.2, 1], vertical_alignment="center")
        with d_cols[0]:
            st.markdown('<div id="desktop-nav-id"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="display:flex; align-items:center; margin-top: -27px;">
                <span style="font-size:1.8rem; margin-right: 10px;">👁️</span>
                <span style="color:white; font-size:1.4rem; font-weight:800;">Eye Detection</span>
            </div>
            """, unsafe_allow_html=True)
        
        for i, title in enumerate(pages_titles):
            with d_cols[i+1]:
                if current_page_title == title:
                    st.markdown('<div id="active-btn"></div>', unsafe_allow_html=True)
                if st.button(title, key=f"nav_{title}", use_container_width=True):
                    st.session_state.active_page = title
                    st.switch_page(pages[i])
        
        with d_cols[6]:
            if st.button("Logout", key="nav_logout", use_container_width=True):
                logout()
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    pg.run()