import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from fpdf import FPDF

# 1. Configuration & Persona Setup
load_dotenv()
st.set_page_config(page_title="PRD AI Pro", page_icon="🕵️‍♂️", layout="wide")

SYSTEM_PROMPT = """
### ROLE
You are a Staff Product Manager at a Tier-1 tech company (Google, Amazon, Meta). Your task is to produce a final, elite-level, execution-ready PRD. You are the "Skeptic-in-Chief."

### CORE PRINCIPLES
1. NO MAGIC | 2. API REALISM | 3. EDGE CASE OBSESSION | 4. UNIT ECONOMICS | 5. BEHAVIORAL DESIGN | 6. LEARNING LOOP SPECIFICS | 7. STAFF PM INSIGHTS

### OUTPUT REQUIREMENTS
Produce a PRD using the 10-section skeleton:
1. Product Overview | 2. Problem Statement | 3. Goals & SMART Objectives | 4. MoSCoW Prioritization | 5. AI / ML Logic | 6. Core User Flow | 7. Technical & Integration | 8. Risks & Mitigation | 9. Launch Criteria | 10. Assumptions & Open Questions

> After generating each section, insert **Insights** in a blockquote explaining trade-offs.
"""

# 2. PDF Generation Logic
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in text.split('\n'):
        clean_line = line.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_line, align='L')
    return pdf.output(dest='S').encode('latin-1')

# 3. Sidebar Settings
with st.sidebar:
    st.title("⚙️ Workspace Settings")
    
    # SAFETY: User enters their own key here
    user_api_key = st.text_input("Enter your OpenAI API Key", type="password", help="Get your key at platform.openai.com")
    
    selected_model = st.selectbox("Intelligence Level", ["gpt-4o", "gpt-4o-mini"], index=0)
    st.divider()
    
    if st.button("🗑️ Clear Workspace"):
        st.session_state.messages = []
        st.rerun()

# 4. Centered Hero Section
st.markdown("<h1 style='text-align: center;'>🚀 PRD AI Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #808495;'>AI-powered PRD generator for high-execution product teams.</p>", unsafe_allow_html=True)
st.divider()

# 5. Initialize Memory
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I'm ready. What product concept are we building today?"}]

# 6. Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Chat Logic
user_input = st.chat_input("Enter your product concept (e.g., A B2B automated billing engine)...")

if user_input:
    if not user_api_key:
        st.error("Please enter your OpenAI API Key in the sidebar to begin.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        client = OpenAI(api_key=user_api_key)
        context = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        stream = client.chat.completions.create(model=selected_model, messages=context, stream=True)
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# 8. Post-Generation Actions
if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "assistant":
    pdf_data = create_pdf(st.session_state.messages[-1]["content"])
    st.download_button(label="📄 Download PRD as PDF", data=pdf_data, file_name="Staff_PM_PRD.pdf", mime="application/pdf")