# --- 1. DEPLOYMENT FIX (Safe for both Windows & Cloud) ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass
# ---------------------------------------------------------

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma

# 2. Load API Keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 3. Setup the Page
st.set_page_config(page_title="Orbit 🪐", page_icon="🪐")
st.title("Orbit 🪐")
st.caption("The CollabCircle Research Assistant")

# 4. Initialize the 'Brain' (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CRITICAL CHANGE: Load the Persistent Brain ---
# We check if the database already exists. If yes, we load it!
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "./chroma_db"

if os.path.exists(persist_directory) and os.path.isdir(persist_directory):
    st.session_state.vector_store = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embedding_function
    )
else:
    st.session_state.vector_store = None

# --- SIDEBAR: Admin Mode ---
with st.sidebar:
    st.header("⚙️ Knowledge Base")
    st.info("Orbit is running on pre-loaded CollabCircle data.")
    
    # Optional: Keep this hidden or password protected in future
    with st.expander("Update Knowledge (Admin Only)"):
        uploaded_files = st.file_uploader("Upload New Research", type="pdf", accept_multiple_files=True)
        if st.button("Process & Update"):
            if uploaded_files:
                with st.spinner("Updating Brain..."):
                    all_splits = []
                    for uploaded_file in uploaded_files:
                        with open(uploaded_file.name, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        loader = PyPDFLoader(uploaded_file.name)
                        docs = loader.load()
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                        splits = text_splitter.split_documents(docs)
                        all_splits.extend(splits)
                        os.remove(uploaded_file.name)

                    # Update the persistent DB
                    st.session_state.vector_store = Chroma.from_documents(
                        documents=all_splits,
                        embedding=embedding_function,
                        persist_directory=persist_directory
                    )
                    st.success("Knowledge Base Updated!")

# --- MAIN: Chat Interface ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask Orbit..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.vector_store:
        try:
            retriever = st.session_state.vector_store.as_retriever()
            
            # --- CRITICAL CHANGE: Identity & Persona ---
            system_prompt = (
                "You are Orbit, the AI assistant for CollabCircle. "
                "Your tone is helpful, professional, and encouraging. "
                "Always start your very first interaction with: 'Hi, I'm Orbit! The AI assistant for CollabCircle. How may I help you?' "
                "For subsequent questions, answer directly based on the context. "
                "Use the following pieces of retrieved context to answer the question. "
                "If you don't know the answer, say that you don't know based on the available documents. "
                "Context: {context}"
            )
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])

            llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)
            question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            with st.spinner("Thinking..."):
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]

            st.chat_message("assistant").markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Orbit's brain is missing! Please upload documents in the sidebar.")