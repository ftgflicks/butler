import streamlit as st
import google.generativeai as genai
import time
import streamlit.components.v1 as components

# --- Styles ---
st.markdown("""
    <style>
        .user-bubble {
            background-color: #cede9e;
            color: black;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 80%;
            margin-left: auto;
            margin-bottom: 10px;
            display: inline-block;
            font-family: Arial, sans-serif;
        }
        .alfred-bubble {
            background-color: #EDE8D0;
            color: black;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 80%;
            margin-right: auto;
            margin-bottom: 10px;
            display: inline-block;
            font-family: Arial, sans-serif;
        }
        .bubble-header {
            font-size: 0.85rem;
            font-weight: bold;
            margin: 2px 0 3px;
            color: #555;
        }
        textarea {
            border-radius: 1rem !important;
            padding: 0.75rem !important;
            border: 1px solid #ccc !important;
            background-color: #ffffff !important;
            color: #000000 !important;
            font-size: 1rem !important;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
            transition: all 0.2s ease-in-out;
        }
        textarea:focus {
            border: 1px solid #5b9bd5 !important;
            box-shadow: 0 0 8px rgba(91, 155, 213, 0.3) !important;
        }
        textarea::placeholder {
            color: #888 !important;
        }
        .background-logo {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 300px;
            opacity: 0.09;
            z-index: 0;
            pointer-events: none;
        }
    </style>
    <img class="background-logo" src="https://i.postimg.cc/5NK7LT0s/download.jpg">
""", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(page_title="Alfred - Your AI Butler", page_icon="🦇")

# --- Mode Toggles ---
col1, col2 = st.columns(2)
with col1:
    st.toggle("🎨 Creative Mode", key="creative_mode")
with col2:
    st.toggle("🧮 Maths Help", key="math_mode")

# --- Gemini Configuration ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- Dynamic generation_config ---
generation_config = {
    "temperature": 1.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Adjust based on toggles
def get_model():
    if st.session_state.get("creative_mode"):
        generation_config["temperature"] = 1.4
        generation_config["top_p"] = 0.95
        sys_inst = """
            You are Alfred, a creative assistant skilled in brainstorming, idea generation,
            and offering unique perspectives. You help users explore ideas for writing, research,
            or any kind of creative or strategic thinking.
            Your tone is curious, imaginative, and encouraging.
        """
    elif st.session_state.get("math_mode"):
        generation_config["temperature"] = 0.2
        generation_config["top_p"] = 0.7
        sys_inst = """
            You are Alfred, a helpful and patient mathematics tutor.
            You assist users by breaking down complex problems, explaining step-by-step,
            and helping them understand key math concepts.
            Speak in a calm, clear, and supportive tone.
        """
    else:
        sys_inst = """
            You are Alfred Pennyworth, the loyal and intelligent butler … (default instruction)
        """
    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
        system_instruction=sys_inst
    )

# Initialize model and session
model = get_model()
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=st.session_state.history)

# --- Title & Header ---
st.title("🦇 Alfred - Your Ai Butler")
st.markdown("_Designed To Assist My CatWoman(non)._ ")
# --- Voice Toggle ---
enable_voice = st.checkbox("🎧 Enable Alfred's voice (British accent)")
# --- Reset Chat ---
if st.button("🗑️ Reset Chat"):
    st.session_state.history = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.experimental_rerun()

# --- Text-to-Speech ---
def browser_tts(text):
    import html
    escaped = html.escape(text).replace("\n", " ")
    components.html(f"""
        <script>
        const msg = new SpeechSynthesisUtterance(\"{escaped}\");
        msg.lang = 'en-GB';
        msg.rate = 1;
        msg.pitch = 1.2;
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)

# --- Chat Display ---
chat_container = st.container()
with chat_container:
    for msg in st.session_state.history:
        header = 'You:' if msg['role']=='user' else 'Alfred:'
        bubble_cls = 'user-bubble' if msg['role']=='user' else 'alfred-bubble'
        st.markdown(f'<div class="bubble-header">{header}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="{bubble_cls}">{msg['parts'][0]}</div>', unsafe_allow_html=True)

# --- Use st.chat_input for fixed input ---
user_input = st.chat_input("Ask Alfred something...")
if user_input:
    st.session_state.history.append({'role':'user','parts':[user_input]})
    with chat_container:
        st.markdown(f'<div class="bubble-header">You:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)
    response = st.session_state.chat_session.send_message(user_input)
    model_response = response.text
    display=""
    with chat_container:
        st.markdown(f'<div class="bubble-header">Alfred:</div>', unsafe_allow_html=True)
        bubble = st.empty()
        for c in model_response:
            display+=c
            bubble.markdown(f'<div class="alfred-bubble">{display}</div>', unsafe_allow_html=True)
            time.sleep(0.015)
    st.session_state.history.append({'role':'model','parts':[model_response]})
    if enable_voice:
        browser_tts(model_response)
    st.experimental_rerun()

# Bottom padding
st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
