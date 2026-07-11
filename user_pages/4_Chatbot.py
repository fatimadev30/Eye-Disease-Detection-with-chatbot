import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import render_medical_disclaimer, require_login
from chatbot.bot import get_chatbot_response
from db.database import get_connection, save_chat_message

require_login()

st.title("💬 AI Chatbot Assistant")
render_medical_disclaimer()

# --- PREDICTION CONTEXT CARD ---
last_pred_id = st.session_state.get('last_prediction_id')
if st.session_state.get('last_prediction'):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.info(f"📍 **Current Context:** Chatting about your recent **{st.session_state.last_prediction}** diagnosis.")
    with col2:
        if st.button("🗑️ Clear", help="Clear analysis context"):
            st.session_state.last_prediction = None
            st.session_state.last_prediction_id = None
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()

st.write("Ask me anything about Eye Diseases (CNV, DME, Drusen), OCT scans, or this AI model.")

# Initialize chat history if not present or empty
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = []
    
    # If there's a recent prediction context but no messages, add a welcome message from the bot
    last_pred = st.session_state.get('last_prediction')
    if last_pred:
        welcome_msg = f"Hello! I see you want to discuss the **{last_pred}** analysis. I'm here to help you understand this result. What would you like to know about it?"
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        # Save welcome message to DB
        save_chat_message(st.session_state.user_id, "assistant", welcome_msg, prediction_id=last_pred_id)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is CNV?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Save user message to DB
    save_chat_message(st.session_state.user_id, "user", prompt, prediction_id=last_pred_id)
    
    # Get bot response
    last_pred = st.session_state.get('last_prediction')
    with st.spinner("AI is thinking..."):
        response = get_chatbot_response(prompt, current_prediction=last_pred)
    
    # Display bot response
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add bot response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    # Save assistant message to DB
    save_chat_message(st.session_state.user_id, "assistant", response, prediction_id=last_pred_id)
