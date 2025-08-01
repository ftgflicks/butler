import os
import streamlit as st
import google.generativeai as genai
import json
import time
import pyttsx3

# Set page config
st.set_page_config(page_title="Alfred - Your AI Butler", page_icon="🦇")

# Configure API key
api_key = os.environ.get("GOOGLE_CLOUD_PROJECT")
genai.configure(api_key=api_key)

# Create the model
generation_config = {
    "temperature": 1.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="""You are My Personal Assistantor Butler who goes by the name Alfred. 
    You will refer to you as Catwoman or Tros non. Respond with intelligence, warmth, and efficiency.
    You will guide me as a butler in to fight against crime(helping with academics) and protect the Gotham city(my grades), Right now you will refer to me as catwoman"""
)

# Initialize session state
if "history" not in st.session_state:
    history_file = "history.txt"
    if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
        with open(history_file, "r") as f:
            st.session_state.history = json.load(f)
    else:
        st.session_state.history = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=st.session_state.history)

# Title
st.title("🦇 Alfred - Your Ai Butler (designed to assisst my catwoman(non))")
st.markdown("_Talk to Alfred, your academic, fitness, and relationship assistant._")

# Voice output toggle
enable_voice = st.checkbox("🔊 Enable Alfred's voice (British accent)")

# Set up TTS
def speak_text(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Try to find a British voice
    for voice in voices:
        if 'english' in voice.name.lower() and 'uk' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.say(text)
    engine.runAndWait()

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        role = "Batman" if msg["role"] == "user" else "Alfred"
        st.markdown(f"**{role}:** {msg['parts'][0]}")

# Input field
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("You (Batman):", key="user_input", label_visibility="collapsed")
    submitted = st.form_submit_button("Send")

# Handle submission
if submitted and user_input.strip():
    try:
        st.session_state.history.append({'role': 'user', 'parts': [user_input]})
        response = st.session_state.chat_session.send_message(user_input)
        model_response = response.text

        # Typing animation
        with chat_container:
            st.markdown(f"**Batman:** {user_input}")
            display_text = ""
            response_container = st.empty()
            for char in model_response:
                display_text += char
                response_container.markdown(f"**Alfred:** {display_text}")
                time.sleep(0.015)

        # Speak response
        if enable_voice:
            speak_text(model_response)

        st.session_state.history.append({'role': 'model', 'parts': [model_response]})

        with open("history.txt", "w") as f:
            json.dump(st.session_state.history, f, indent=4)

        st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {e}")
