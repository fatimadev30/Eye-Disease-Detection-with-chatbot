import streamlit as st
import os

def load_css():
    """Loads custom CSS."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def render_medical_disclaimer():
    """Renders the standard medical disclaimer."""
    st.markdown('''
        <div class="medical-disclaimer">
            <strong>⚠️ MEDICAL DISCLAIMER:</strong><br>
            This system is for educational purposes only and does not replace professional medical advice. 
            Always consult with a qualified healthcare provider for diagnosis and treatment.
        </div>
    ''', unsafe_allow_html=True)

def check_admin_access():
    """Returns True if the current user is an admin."""
    return st.session_state.get('role') == 'admin'

def require_login():
    """Redirects or stops execution if not logged in."""
    if not st.session_state.get('logged_in'):
        st.warning("Please log in to access this page.")
        st.stop()
