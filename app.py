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
import backend  # Import our logic file

# 2. Config & Branding
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="Orbit 🪐", 
    page_icon="🪐", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Initialize Session State
if "vector_store" not in st.session_state:
    st.session_state.vector_store = backend.get_vector_store()

# --- FIX: Set the Greeting ONE TIME at startup ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm Orbit! The AI assistant for CollabCircle. How may I help you?"}
    ]

# --- UI: Sidebar (Logo & Admin) ---
with st.sidebar:
    # 1. DISPLAY LOGO
    # Use columns to center the logo nicely
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2:
        # Check if file exists to prevent errors
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=100)
        else:
            st.warning("Logo not found")
            
    st.markdown("---") # Divider line
    
    st.header("⚙️ Settings")
    
    # Check if Brain is loaded
    if st.session_state.vector_store:
        st.success("🟢 System Online")
    else:
        st.error("🔴 Brain Missing")

    # Admin Panel
    with st.expander("Admin: Update Knowledge"):
        password = st.text_input("Admin Password", type="password")
        if password == "collab123": 
            uploaded_files = st.file_uploader("Upload New Research", type="pdf", accept_multiple_files=True)
            if st.button("Update Database"):
                if uploaded_files:
                    with st.spinner("Processing..."):
                        st.session_state.vector_store = backend.update_knowledge_base(uploaded_files)
                        st.success("Database Updated!")

# --- UI: Main Header ---
col_a, col_b = st.columns([1, 5])
with col_a:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=70)
with col_b:
    st.title("Orbit 🪐")
    st.caption("The Knowledge Hub for CollabCircle")

st.markdown("---")

# --- UI: Chat Loop ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about CollabCircle..."):
    # Add User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    if st.session_state.vector_store:
        try:
            rag_chain = backend.get_rag_chain(st.session_state.vector_store)
            
            with st.spinner("Accessing CollabCircle Archives..."):
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]

            # Add AI Message
            st.chat_message("assistant").markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Orbit is offline. Please initialize the knowledge base.")