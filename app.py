import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from groq import Groq
import PyPDF2
import time
import os

# --- 1. UI & CSS CONFIGURATION (Must be the first Streamlit command) ---
st.set_page_config(page_title="TwinTrack AI | Royal Bengal Coders", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Inter:wght@300;600&display=swap');
    
    .stApp { background-color: #0b0f19; color: #e0e6ed; font-family: 'Inter', sans-serif; }
    
    /* Glowing Animated Title */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(40px, 8vw, 70px) !important;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00d2ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 4s linear infinite, glow 3s infinite ease-in-out;
    }

    @keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
    @keyframes glow { 0%, 100% { text-shadow: 0 0 10px rgba(0, 210, 255, 0.3); } 50% { text-shadow: 0 0 30px rgba(0, 210, 255, 0.7); } }

    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white; border: none; border-radius: 12px; padding: 12px 24px;
        font-family: 'Orbitron', sans-serif; font-weight: bold; width: 100%;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0px 10px 20px rgba(0, 114, 255, 0.5); }
    
    /* Input Styling */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #161b22 !important; color: #00d2ff !important; border: 1px solid #30363d !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API INITIALIZATION ---
def initialize_groq():
    # Priority: Streamlit Secrets > Environment Variables
    api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.warning("🔑 API Key Missing: Please set GROQ_API_KEY in Streamlit Secrets.")
        st.stop()
    return Groq(api_key=api_key)

client = initialize_groq()

# --- 3. STATE MANAGEMENT ---
if "page" not in st.session_state: st.session_state.page = "landing"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "user_data" not in st.session_state: st.session_state.user_data = {}

def navigate_to(page):
    st.session_state.page = page
    # In newer Streamlit versions, st.rerun() is the standard
    st.rerun()

# --- 4. PDF PARSER ---
def extract_text_from_pdf(file):
    try:
        file.seek(0)
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text: full_text += text + "\n"
        return full_text[:20000] # Increased context window
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return None

# --- 5. PAGE ROUTING ---

# PAGE: LANDING
if st.session_state.page == "landing":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TwinTrack AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#8b949e; letter-spacing:2px;'>THE ACADEMIC DIGITAL TWIN</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.write("")
        if st.button("⚡ INITIALIZE SYSTEM"): navigate_to("intake")

# PAGE: INTAKE (CALIBRATION)
elif st.session_state.page == "intake":
    st.markdown("## 📝 Calibration Matrix")
    with st.container():
        name = st.text_input("Student Name:", value="Anubhab Roy")
        col1, col2 = st.columns(2)
        with col1:
            course = st.selectbox("Program:", ["B.Tech", "BCA", "BBA", "BSC"])
            sem = st.selectbox("Semester:", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"])
        with col2:
            subject = st.text_input("Target Subject (e.g., Operating Systems):")
        
        if st.button("Generate Trajectory ➡️"):
            if not subject:
                st.error("Please specify a target subject.")
            else:
                st.session_state.user_data.update({"name": name, "course": course, "sem": sem, "subject": subject})
                navigate_to("analysis")

# PAGE: ANALYSIS & PDF UPLOAD
elif st.session_state.page == "analysis":
    st.markdown("## 🌌 Performance Projection")
    d = st.session_state.user_data
    
    col1, col2 = st.columns(2)
    with col1:
        att = st.slider("Attendance %", 0, 100, 75)
        cgpa = st.number_input("Current CGPA", 0.0, 10.0, 7.5, step=0.1)
    with col2:
        days = st.number_input("Days to Exam", 1, 100, 30)
        hrs = st.number_input("Daily Study Hours", 1, 18, 4)

    st.divider()
    st.markdown("### 📂 Knowledge Injection")
    file = st.file_uploader("Upload Syllabus PDF", type=["pdf"])

    if st.button("🔥 SYNC DIGITAL TWIN"):
        if file:
            with st.spinner("Analyzing Syllabus Matrix..."):
                text = extract_text_from_pdf(file)
                if text:
                    st.session_state.user_data.update({
                        "att": att, "cgpa": cgpa, "days": days, "hrs": hrs, "syllabus": text
                    })
                    navigate_to("chat")
        else:
            st.error("Upload a syllabus to proceed.")

# PAGE: CHAT (THE BEAST)
elif st.session_state.page == "chat":
    d = st.session_state.user_data
    
    with st.sidebar:
        st.markdown(f"### 🛡️ Twin Stats")
        st.info(f"**Subject:** {d['subject']}\n\n**Days Left:** {d['days']}\n\n**Status:** {'Stable' if d['att'] >= 75 else 'Critical'}")
        if st.button("🔄 System Reset"):
            st.session_state.chat_history = []
            navigate_to("landing")

    st.markdown(f"<h2 style='color:#00d2ff;'>🤖 Virtual Strategist: {d['subject']}</h2>", unsafe_allow_html=True)

    # Render History
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about specific topics..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # AI Instruction Matrix
        sys_prompt = f"""
        You are TwinTrack AI, a strict academic strategist. 
        USER: {d['name']} | SUBJECT: {d['subject']} | SEM: {d['sem']}
        STATS: {d['att']}% Attendance, {d['days']} days left.
        
        SYLLABUS DATA:
        {d.get('syllabus', 'No syllabus found.')}
        
        RULES:
        1. Find "{d['subject']}" in the syllabus and ONLY teach those topics.
        2. If attendance is < 75%, warn that they risk being barred from exams.
        3. Be highly structured with bold headings and bullet points.
        4. If the user asks for topics, list them directly from the provided text.
        """

        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": sys_prompt}] + st.session_state.chat_history
                )
                output = response.choices[0].message.content
                st.markdown(output)
                st.session_state.chat_history.append({"role": "assistant", "content": output})
            except Exception as e:
                st.error("Neural Link timed out. Please try again.")
