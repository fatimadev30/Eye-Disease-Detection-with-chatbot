import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
# Get API key from environment variable or streamlit secrets
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')

else:
    model = None

def get_chatbot_response(user_input: str, current_prediction: str = None) -> str:
    """Generates an AI response using Gemini, aware of the current diagnosis context."""
    
    if not API_KEY or not model:
        return "⚠️ Gemini API key is missing. Please add your GEMINI_API_KEY to the .env file to enable the AI Chatbot."

    # Construct the context-aware prompt
    context = ""
    if current_prediction:
        context = f"The user has recently performed an OCT scan analysis which resulted in a diagnosis of: **{current_prediction}**. "
    
    system_prompt = (
        "You are a strictly bounded professional medical assistant for an Eye Disease Detection application. "
        "YOUR SCOPE IS LIMITED TO: Eye diseases (specifically CNV, DME, Drusen, and Normal retina), OCT (Optical Coherence Tomography) imaging, eye anatomy, and this specific AI model's functionality. "
        "\n\nSTRICT BOUNDARIES:\n"
        "1. If a user asks about anything OUTSIDE of the eye health or OCT imaging scope (e.g., politics, other medical fields like cardiology, general knowledge, programming, etc.), you MUST politely decline to answer. "
        "Example response for off-topic: 'I apologize, but I am specifically trained to assist with OCT analysis and eye health information. I cannot answer questions outside of this scope.' "
        "2. Do not engage in casual 'chit-chat' beyond professional greetings. "
        "3. Keep your answers concise, accurate, and professional. "
        "4. Always include a disclaimer that you are an AI and the user should consult a human ophthalmologist for definitive diagnosis. "
        f"\n\nCurrent Analysis Context: {context}"
    )

    full_prompt = f"{system_prompt}\n\nUser Question: {user_input}\n\nAI Response:"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error while processing your request: {str(e)}"
