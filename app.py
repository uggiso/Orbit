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

# 1. Load API Keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 2. Setup the Page
st.set_page_config(page_title="Orbit 🪐", page_icon="🪐")
st.title("Orbit 🪐")
st.caption("The CollabCircle Research Assistant")

# 3. Initialize the 'Brain' (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# --- SIDEBAR: Document Ingestion ---
with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader("Upload PDF Research Papers", type="pdf", accept_multiple_files=True)
    
    if st.button("Process Documents"):
        if uploaded_files:
            with st.spinner("Digesting documents..."):
                all_splits = []
                
                # A. Read each PDF
                for uploaded_file in uploaded_files:
                    # Save temp file because PyPDFLoader needs a real file path
                    with open(uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    loader = PyPDFLoader(uploaded_file.name)
                    docs = loader.load()
                    
                    # B. Split text into chunks
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    splits = text_splitter.split_documents(docs)
                    all_splits.extend(splits)
                    
                    # Cleanup temp file
                    os.remove(uploaded_file.name)

                # C. Store in Vector Database (Chroma) using LOCAL Embeddings
                # This runs on your laptop (CPU), so it's free and has no rate limits!
                st.session_state.vector_store = Chroma.from_documents(
                    documents=all_splits,
                    embedding=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
                    persist_directory="./chroma_db"
                )
                
                st.success("Knowledge Base Updated! You can now chat.")
        else:
            st.warning("Please upload a PDF first.")

# --- MAIN: Chat Interface ---

# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle User Input
if prompt := st.chat_input("Ask a question about CollabCircle research..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Answer
    if st.session_state.vector_store:
        try:
            # A. Create the Retriever
            retriever = st.session_state.vector_store.as_retriever()
            
            # B. Define the System Prompt (The Rules)
            system_prompt = (
                "You are an assistant for CollabCircle. "
                "Use the following pieces of retrieved context to answer the question. "
                "If you don't know the answer, say that you don't know. "
                "Context: {context}"
            )
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])

            # C. Define the LLM (Gemini 1.5 Flash)
            # We still use Google for the answer generation because it's smart!
            llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.3)
            
            # D. Create the Chain (The Pipeline)
            question_answer_chain = create_stuff_documents_chain(llm, prompt_template)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            # E. Run the Chain
            with st.spinner("Thinking..."):
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]

            # Show AI message
            st.chat_message("assistant").markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        # Fallback if no docs are uploaded
        st.warning("Please upload and process documents in the sidebar first!")