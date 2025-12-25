# --- 1. DEPLOYMENT FIX (Must remain at top) ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass
# ----------------------------------------------

import streamlit as st
import os
from dotenv import load_dotenv
import backend

# 2. Config & Branding
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="Orbit 🪐", 
    page_icon="🪐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS HACK: Circular Logo & Footer Styling ---
st.markdown("""
    <style>
        /* 1. Make the Sidebar Image a Circle */
        [data-testid="stSidebar"] img {
            border-radius: 50%;
            border: 3px solid #0088CC; /* Optional: Blue border ring */
            object-fit: cover;
        }
        /* 2. Style the Footer */
        .footer {
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-top: 20px;
        }
        .footer a {
            color: #0088CC;
            text-decoration: none;
            margin: 0 5px;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "vector_store" not in st.session_state:
    st.session_state.vector_store = backend.get_vector_store()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm Orbit! The AI assistant for CollabCircle. How may I help you?"}
    ]

# --- UI: Sidebar ---
with st.sidebar:
    # A. LOGO (Circular due to CSS above)
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=120)
    else:
        st.header("Orbit 🪐")
    
    st.markdown("### CollabCircle Research")
    st.markdown("---")
    
    # B. STATUS & ADMIN
    if st.session_state.vector_store:
        st.success("🟢 Orbit is Online")
    else:
        st.error("🔴 Brain Missing")

    with st.expander("Admin Access"):
        password = st.text_input("Password", type="password")
        if password == "collab123": 
            uploaded_files = st.file_uploader("Upload Docs", type="pdf", accept_multiple_files=True)
            if st.button("Update Database"):
                if uploaded_files:
                    with st.spinner("Processing..."):
                        st.session_state.vector_store = backend.update_knowledge_base(uploaded_files)
                        st.success("Updated!")

    # C. FOOTER (Developed By + Socials)
    st.markdown("---")
    st.markdown("""
        <div class="footer">
            <p>Developed by <b>Shah Mohammad Rizvi</b></p>
            <p>&copy; 2025 CollabCircle</p>
            <p>
                <a href="https://www.linkedin.com/company/collabcircle-official/" target="_blank">LinkedIn</a> | 
                <a href="https://www.facebook.com/collabcircle.official/" target="_blank">Facebook</a> | 
                <a href="https://www.youtube.com/@collabcircle.official" target="_blank">YouTube</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- UI: Main Header ---
col_a, col_b = st.columns([1, 5])
with col_a:
    # Small logo in header too (also circular now)
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=70)
with col_b:
    st.title("Orbit 🪐")
    st.caption("The Knowledge Hub for CollabCircle")

st.divider()

# --- UI: Chat Interface ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about policies, research, or guidelines..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.vector_store:
        try:
            rag_chain = backend.get_rag_chain(st.session_state.vector_store)
            with st.spinner("Analyzing..."):
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]
            
            st.chat_message("assistant").markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please upload documents in the Admin panel.")