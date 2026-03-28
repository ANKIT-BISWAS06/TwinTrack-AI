import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import time

# --- UI & CSS CONFIGURATION (The "Beast Mode" Visuals) ---
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;600&display=swap');

    /* --- GLOBAL STYLES --- */
    .stApp { 
        background-color: #0b0f19; 
        color: #e0e6ed; 
        font-family: 'Inter', sans-serif;
    }

    /* --- KEYFRAME ANIMATIONS --- */
    @keyframes glow {
        0% { text-shadow: 0 0 10px rgba(0, 210, 255, 0.5); }
        50% { text-shadow: 0 0 30px rgba(0, 210, 255, 0.9), 0 0 40px rgba(0, 114, 255, 0.6); }
        100% { text-shadow: 0 0 10px rgba(0, 210, 255, 0.5); }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    /* --- TITLES & HEADERS --- */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 70px !important;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 4s linear infinite, glow 3s infinite ease-in-out, slideUp 1s ease-out;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
    }

    /* --- BUTTONS (Pulse on Hover) --- */
    div.stButton > button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white; 
        border: none; 
        border-radius: 12px; 
        padding: 15px 30px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        font-weight: bold;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0px 4px 15px rgba(0, 114, 255, 0.3);
    }

    div.stButton > button:hover { 
        transform: scale(1.05);
        box-shadow: 0px 0px 25px rgba(0, 210, 255, 0.7);
        color: #ffffff;
    }

    /* --- CHAT MESSAGES & INPUTS --- */
    .stChatMessage {
        animation: slideUp 0.5s ease-out;
        border-radius: 15px;
        border: 1px solid #30363d;
        background: rgba(22, 27, 34, 0.5);
    }

    /* Clean Inputs */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #161b22;
        color: #00d2ff;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- API & BACKEND SETUP ---
# Ensure your Streamlit Secret is set to GROQ_API_KEY
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except:
    st.error("API Key missing! Please set GROQ_API_KEY in secrets.")

# --- STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def switch_page(page_name):
    st.session_state.page = page_name

# --- IMPROVED PDF SMART SCANNER ---
def parse_entire_syllabus(file):
    """Extracts all text from the PDF to allow AI-based subject mapping."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in pdf_reader.pages:
            p_text = page.extract_text()
            if p_text:
                full_text += p_text + "\n"
        return full_text[:15000] # Increased cap for detailed syllabi
    except Exception as e:
        return f"Syllabus extraction failed: {e}"

# ==========================================
# PHASE 1: LANDING PAGE
# ==========================================
if st.session_state.page == "landing":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <p class="main-title">TwinTrack AI</p>
            <h3 style="color: #a3b8cc; letter-spacing: 4px;">THE ACADEMIC DIGITAL TWIN</h3>
            <p style="color: #58a6ff; font-family: monospace; font-weight: bold;">DEVELOPED BY THE ROYAL BENGAL CODERS</p>
            <br>
            <div style="background: rgba(0, 210, 255, 0.05); padding: 20px; border-radius: 15px; border-left: 5px solid #00d2ff; max-width: 700px; margin: auto;">
                <h5 style="font-style: italic; color: #8b949e; line-height: 1.6;">
                    "Stop guessing your trajectory. Upload your syllabus, visualize your future, and let LLaMA 3.1 calculate your exact survival path."
                </h5>
            </div>
        </div>
        <br><br>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("⚡ INITIALIZE SYSTEM", use_container_width=True, on_click=switch_page, args=("login",))

# ==========================================
# PHASE 1.5: AUTHENTICATION
# ==========================================
elif st.session_state.page == "login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #00d2ff;'>Access Portal</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        with tab1:
            st.text_input("Email ID", value="anubhab@narula.edu")
            st.text_input("Password", type="password", value="********")
            st.button("Secure Login", use_container_width=True, on_click=switch_page, args=("intake",))
        with tab2:
            st.text_input("Full Name")
            st.text_input("Email ID", key="register_email")
            st.button("Create Account", use_container_width=True, on_click=switch_page, args=("intake",))

# ==========================================
# PHASE 2: INTAKE
# ==========================================
elif st.session_state.page == "intake":
    st.markdown("<h2 style='color: #00d2ff;'>📝 Calibration Matrix</h2>", unsafe_allow_html=True)
    
    u_name = st.text_input("Student Designation:", value=st.session_state.user_data.get("name", "Anubhab Roy"))
    col1, col2 = st.columns(2)
    with col1:
        course = st.selectbox("Program:", ["B.Tech", "BBA", "BCA", "Select"], index=0)
        year = st.selectbox("Year:", ["1st", "2nd", "3rd", "4th", "Select"], index=1)
    with col2:
        sem = st.selectbox("Semester:", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "Select"], index=2)
    
    if st.button("Generate Trajectory ➡️", use_container_width=True):
        st.session_state.user_data.update({"name": u_name, "course": course, "year": year, "sem": sem})
        switch_page("analysis")

# ==========================================
# PHASE 3: THE 3D DIGITAL TWIN & PDF SCAN
# ==========================================
elif st.session_state.page == "analysis":
    d = st.session_state.user_data
    st.toast(f"Profile Synced: {d['name']}", icon="✅")
    
    col_a, col_b = st.columns(2)
    with col_a:
        att = st.number_input("Current Attendance (%):", min_value=0, max_value=100, value=70)
        cgpa = st.number_input("Current CGPA:", min_value=0.0, max_value=10.0, value=7.5)
    with col_b:
        days = st.number_input("Days to Exam:", min_value=0, value=30)
        hrs = st.number_input("Daily Study Hours:", min_value=0, value=2)

    st.divider()
    st.markdown("<h3 style='color: #00d2ff;'>🌌 3D Digital Twin Projection</h3>", unsafe_allow_html=True)
    
    study_mesh = np.linspace(0, 10, 20)
    att_mesh = np.linspace(0, 100, 20)
    study_grid, att_grid = np.meshgrid(study_mesh, att_mesh)
    cgpa_grid = np.clip(cgpa + (study_grid * 0.15) + ((att_grid - 75) * 0.01), 0, 10)

    fig = go.Figure(data=[go.Surface(z=cgpa_grid, x=study_grid, y=att_grid, colorscale='Tealgrn', opacity=0.8)])
    current_predicted_cgpa = np.clip(cgpa + (hrs * 0.15) + ((att - 75) * 0.01), 0, 10)
    fig.add_trace(go.Scatter3d(x=[hrs], y=[att], z=[current_predicted_cgpa], mode='markers', marker=dict(size=8, color='red')))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h3 style='color: #00d2ff;'>📂 Inject Syllabus Data</h3>", unsafe_allow_html=True)
    file = st.file_uploader("Upload University Syllabus (PDF)", type=['pdf'])

    if file:
        subjects = ["Data Structures & Algorithms", "Computer Organization", "Digital Logic", "Mathematics", "Microprocessors"]
        sub = st.selectbox("Target Subject for Strategy:", subjects, index=0)
        
        if st.button("🔥 INITIALIZE BEAST MODE", use_container_width=True):
            progress_bar = st.progress(0, text="Mapping Neural Pathways...")
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # PARSE ENTIRE PDF
            raw_content = parse_entire_syllabus(file)
            st.session_state.user_data.update({
                "att": att, "days": days, "cgpa": cgpa, 
                "hrs": hrs, "subject": sub, "syllabus_full": raw_content
            })
            st.balloons()
            switch_page("chat")

# ==========================================
# PHASE 4: THE BEAST (LLaMA 3.1 Chat)
# ==========================================
elif st.session_state.page == "chat":
    d = st.session_state.user_data
    
    with st.sidebar:
        st.markdown("<h2 style='color: #00d2ff;'>Twin Controls</h2>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Analysis"): switch_page("analysis")
        if st.button("🔄 System Reset"): 
            st.session_state.chat_history = []
            switch_page("intake")
        st.divider()
        st.markdown(f"**Target:** `{d['subject']}`")
        st.markdown(f"**Attendance:** `{d['att']}%`")
        st.markdown(f"**Deadline:** `{d['days']} Days`")

    st.markdown(f"<h2 style='color: #00d2ff;'>🤖 Virtual Educator: {d['subject']}</h2>", unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        initial_msg = f"System Synced. {d['name']}, I have analyzed the entire syllabus. Even without you asking, I am locked onto **{d['subject']}**. What specific topic from the syllabus shall we master first?"
        st.session_state.chat_history.append({"role": "assistant", "content": initial_msg})

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Command your TwinTrack Strategist..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # SYSTEM PROMPT: Forces focus on the selected subject regardless of chat context
        sys_prompt = f"""
        You are 'TwinTrack AI', a high-performance strategist. 
        USER PROFILE: {d['name']}, studying {d['subject']} (Sem {d['sem']}).
        CONTEXT: {d['days']} days left, {d['hrs']} hrs study/day.
        
        RAW SYLLABUS DATA FROM PDF:
        {d.get('syllabus_full', 'No data provided.')}
        
        CORE RULES:
        1. THE USER HAS SELECTED THE SUBJECT: {d['subject']}. You MUST base all academic answers on the topics found under this subject heading in the RAW SYLLABUS DATA.
        2. Do not ask for the semester or year; you already have that data.
        3. If the user asks "What are the topics?", look through the text for "{d['subject']}" and list every module/unit found.
        4. If Attendance ({d['att']}%) is under 75%, start your first response with a warning about debarment.
        5. Be strict: redirect any off-topic talk back to {d['subject']}.
        """
        
        with st.chat_message("assistant"):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_prompt}] + st.session_state.chat_history,
                    model="llama-3.1-8b-instant",
                )
                bot_response = chat_completion.choices[0].message.content
                st.write(bot_response)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                st.error("Neural Link Overloaded. Retry in 10s.")
