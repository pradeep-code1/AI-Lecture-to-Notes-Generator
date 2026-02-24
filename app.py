import streamlit as st
import google.generativeai as genai
import tempfile
import os

# ==========================================
# STEP 1: AI CONFIGURATION
# ==========================================
try:
    # Accessing the secure key from Streamlit Cloud Secrets
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API Key not found. Please set GEMINI_API_KEY in Streamlit Secrets.")

# Utilizing Gemini 3 Flash for high-speed academic processing
model = genai.GenerativeModel('gemini-3-flash-preview')

# ==========================================
# STEP 2: PROFESSIONAL UI & ADVANCED CSS
# ==========================================
st.set_page_config(page_title="Lecture AI Master", page_icon="🎙️", layout="wide")

st.markdown("""
    <style>
    /* 1. Main App Background */
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
    }

    /* 2. Professional Sidebar - Deep Navy */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    /* 3. Sidebar Tip/Info text to WHITE */
    [data-testid="stSidebar"] div[data-testid="stNotification"] div {
        color: white !important;
    }

    /* 4. FIX: Header Labels (1. Upload & 2. Process) to BLACK */
    /* Hum specific headings aur normal text ko target kar rahe hain */
    [data-testid="stVerticalBlock"] h3 {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stVerticalBlock"] p, [data-testid="stVerticalBlock"] label {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* 5. Generated Notes Styling (Keep as is, Dark Blue-Grey) */
    .stMarkdown div p, .stMarkdown div h1, .stMarkdown div h2, .stMarkdown div h3, .stMarkdown div li {
        color: #1e293b !important;
    }

    /* 6. Sidebar Labels and Titles to White */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }

    /* 7. Primary Action Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #3b82f6 0%, #2563eb 100%);
        color: white !important;
        height: 3.5em;
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        border: none;
    }

    /* 8. Content Cards */
    [data-testid="stVerticalBlock"] > div:has(div.stFileUploader) {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Main Header Section
st.markdown("""
    <div style="text-align: center; padding-bottom: 20px;">
        <h1 style="color: #1e3a8a; margin-bottom: 0;">🎙️ AI Lecture-to-Notes Generator</h1>
        <p style="color: #334155; font-size: 1.2rem; font-weight: 500;">Convert your spoken lectures into professional study notes</p>
    </div>
""", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("📝 Lecture Details")
    lecture_topic = st.text_input("Topic Name", "New Lecture")
    
    st.header("⚙️ Output Settings")
    output_type = st.selectbox(
        "Generate Content As:",
        ["Study Notes", "Flashcards", "Multiple Choice Quiz"]
    )
    st.markdown("---")
    st.info("💡 Tip: This system uses a high-speed multimodal model optimized for processing long academic lectures with high accuracy.")

# --- MAIN INTERFACE LAYOUT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Upload Audio")
    uploaded_file = st.file_uploader("Select recording (MP3, WAV, M4A)", type=["mp3", "wav", "m4a"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/mp3')

with col2:
    st.subheader("2. Process & Results")
    st.write("Click below to start the AI transformation.")
    generate_button = st.button("✨ Generate " + output_type)

# ==========================================
# STEP 3: CORE LOGIC & AI GENERATION
# ==========================================
if uploaded_file is not None and generate_button:
    with st.spinner("Analyzing lecture content..."):
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(uploaded_file.read())
            temp_audio_path = temp_audio.name

        try:
            # Uploading to Gemini File API
            audio_file = genai.upload_file(path=temp_audio_path)
            
            if output_type == "Study Notes":
                prompt = f"Summarize this lecture on {lecture_topic} into structured study notes with headings and bold key terms."
            elif output_type == "Flashcards":
                prompt = f"Identify key terms from this lecture on {lecture_topic} and create Q&A flashcards. Format: **Front:** [Question] **Back:** [Answer]."
            else:
                prompt = f"Create a 5-question multiple choice quiz with correct answers and explanations based on this {lecture_topic} lecture."

            # Generating response using Gemini 3 Flash
            response = model.generate_content([prompt, audio_file])
            
            st.success("Analysis Complete!")
            st.markdown(f"### Results for: {lecture_topic}")
            st.markdown(response.text)
            
            # Download Feature
            st.download_button(
                label="📥 Save Results as Markdown",
                data=response.text,
                file_name=f"{lecture_topic.replace(' ', '_')}_{output_type.lower()}.md",
                mime="text/markdown"
            )

        except Exception as e:
            st.error(f"Processing Error: {e}")
            
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)


