# app.py
import streamlit as st
import os
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from llm_handler import rewrite_text
from tts_handler import text_to_speech
import io
import wave # Import the wave library
import base64
import requests
from streamlit_lottie import st_lottie

def get_base64_bg(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
bg_base64 = get_base64_bg("222.jpg")

st.markdown("""
<style>
/* Background image and layout styling */
body {{
    background-image: url("data:image/webp;base64,{bg_base64}");
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
    background-position: center;
    animation: pulsebg 15s infinite ease-in-out;
}}

 @keyframes pulsebg {{
        0% {{ filter: brightness(0.95); }}
        50% {{ filter: brightness(1.05); }}
        100% {{ filter: brightness(0.95); }}
    }}


section.main > div {{
    background-color: rgba(255, 255, 255, 0.90);
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
}}

/* Stylish sidebar */
.css-1d391kg {{  /* Sidebar background */
    background: linear-gradient(135deg, #dbeafe, #eff6ff);
    padding: 1rem;
    border-radius: 15px;
    backdrop-filter: blur(8px);
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
}}

/* Buttons */
.stTextInput > div > input,
.stTextArea > div > textarea {{
    border-radius: 10px;
    border: 1px solid #cbd5e0;
    padding: 0.5rem;
    background-color: #ffffffdd;
}}

.stButton > button {{
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1.2rem;
    font-weight: bold;
    transition: background 0.3s ease;
}}

.stButton > button:hover {{
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    color: #f0f0f0;
}}

/* File uploader */
.stFileUploader {{
    background-color: #ffffffdd;
    padding: 1rem;
    border-radius: 10px;
    border: 1px dashed #0072ff;
}}

/* Sidebar enhancement */
.css-1d391kg {{
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(8px);
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
}}
</style>
""", unsafe_allow_html=True)
def gradient_title(text):
    st.markdown(f"""
    <h2 style="
        background: -webkit-linear-gradient(left, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2em;
        font-weight: bold;
        text-align: center;
    ">{text}</h2>
    """, unsafe_allow_html=True)

def transcribe_audio_from_wav(audio_bytes, sample_rate, sample_width):
    """
    Takes raw audio bytes, wraps them in a WAV header, and transcribes the audio.
    """
    r = sr.Recognizer()
    
    # Create a valid WAV file in memory from the raw audio data
    wav_in_memory = io.BytesIO()
    with wave.open(wav_in_memory, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)
    
    # Rewind the in-memory file to the beginning
    wav_in_memory.seek(0)
    
    try:
        # Use the in-memory WAV file as the source
        with sr.AudioFile(wav_in_memory) as source:
            audio_data = r.record(source)
        
        st.info("Transcribing...")
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand the audio. Please speak clearly.")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results from the speech recognition service; {e}")
        return ""

def main():
    """
    Main function to run the EchoVerse Streamlit application.
    """
    st.set_page_config(page_title="EchoVerse", page_icon="🎙️", layout="wide")
    
    st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <img src="https://img.icons8.com/ios-filled/100/ffffff/audio-wave.png" width="70" style="margin-bottom: 10px;" />
    <h1 style="
        background: -webkit-linear-gradient(left, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3em;
        margin: 0;
        font-weight: 700;
    ">EchoVerse</h1>
    <p style="font-size: 1.1em; color: #cccccc; margin-top: 0.5rem;">
        Your AI-Powered Audiobook Creator
    </p>
</div>
""", unsafe_allow_html=True)

    gradient_title("EchoVerse: AI-Powered Audiobook Creation 🎙")
    lottie_url = "https://assets10.lottiefiles.com/packages/lf20_jcikwtux.json"  # Audiobook-style animation
    lottie_json = load_lottieurl(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=250)

    # --- Check for Hugging Face Token in Streamlit Secrets ---
    try:
        hf_token = st.secrets["HUGGINGFACE_TOKEN"]
        os.environ['HUGGING_FACE_HUB_TOKEN'] = hf_token
    except (KeyError, FileNotFoundError):
        st.error("Hugging Face token not found! Please add it to your secrets file.")
        st.info("Create a file at `.streamlit/secrets.toml` and add your token: \n\nHUGGINGFACE_TOKEN = 'hf_YourTokenGoesHere'")
        st.stop()

    with st.sidebar:
        st.header("Controls")
        st.success("Hugging Face token loaded!")
        st.write("---")
        
        st.write("Provide your text in the main area.")
        tone = st.radio(
            "Step 1: Choose a Tone",
            ('Neutral', 'Suspenseful', 'Inspiring'),
            help="Select the emotional tone for the narration."
        )
        voice = st.selectbox(
            "Step 2: Choose a Voice",
            ('Lisa (Female)', 'Michael (Male)', 'Allison (Female)'),
            help="Select the voice for the audio narration."
        )
        generate_button = st.button("Generate Audiobook", type="primary")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    gradient_title("Your Text Content")
    
    if 'text_input' not in st.session_state:
        st.session_state.text_input = ""

    st.write("Record your voice manually:")
    audio_info = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        just_once=True,
        key='recorder'
    )

    if audio_info and audio_info['bytes']:
        with st.spinner("Processing recorded audio..."):
            audio_bytes = audio_info['bytes']
            sample_rate = audio_info['sample_rate']
            sample_width = audio_info['sample_width'] // 8 # Convert bits to bytes
            
            # **FIX:** Pass all necessary info to the new WAV-based transcription function
            transcribed_text = transcribe_audio_from_wav(audio_bytes, sample_rate, sample_width)
            if transcribed_text:
                st.session_state.text_input = transcribed_text

    uploaded_file = st.file_uploader("Upload a .txt file", type="txt")
    text_input_area = st.text_area("Or paste your text here", value=st.session_state.text_input, height=250, key="text_area_input")

    if text_input_area:
        st.session_state.text_input = text_input_area

    original_text = ""
    if uploaded_file is not None:
        original_text = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Uploaded Text", original_text, height=250, disabled=True)
        st.session_state.text_input = original_text
    else:
        original_text = st.session_state.text_input
    st.markdown('</div>', unsafe_allow_html=True)

    if generate_button and original_text:
        rewritten_text = ""
        with st.spinner(f"Rewriting text in a {tone.lower()} tone... This may take a moment."):
            rewritten_text = rewrite_text(original_text, tone)
            st.success("Text rewriting complete!")

        audio_file_path = None
        if rewritten_text and "Failed" not in rewritten_text:
            with st.spinner("Generating audio..."):
                audio_file_path = text_to_speech(rewritten_text, voice)
                st.success("Audio generation complete!")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        gradient_title("Text Comparison")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.info("Original Text")
            st.write(original_text)
        with res_col2:
            st.success(f"Rewritten Text ({tone})")
            st.write(rewritten_text)

        st.subheader("Listen and Download")
        if audio_file_path:
            audio_bytes = open(audio_file_path, "rb").read()
            st.audio(audio_bytes, format='audio/mp3')
            
            st.download_button(
                label="Download MP3",
                data=audio_bytes,
                file_name=f"echoverse_{tone.lower()}.mp3",
                mime="audio/mp3"
            )
        else:
            st.error("Could not generate audio. Please check the text and try again.")

    elif generate_button and not original_text:
        st.error("Please provide some text first.")

if __name__ == "__main__":
    main()
