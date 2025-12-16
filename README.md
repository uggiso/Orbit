# Orbit 🪐
**A RAG-powered internal research assistant for CollabCircle.**

Orbit is a specialized AI chatbot designed to serve as the central knowledge hub for CollabCircle. Powered by Google's Gemini API and LangChain, Orbit ingests internal research papers, policy documents, and meeting minutes to provide accurate, context-aware answers to organization members.

## Features
* **Walled Garden:** Answers questions *only* based on internal CollabCircle documents.
* **Privacy First:** Uses a local vector database (ChromaDB) to store document knowledge.
* **Source Citing:** References specific internal documents when answering.

## Tech Stack
* **Frontend:** Streamlit
* **LLM:** Google Gemini 1.5 Flash
* **Vector Store:** ChromaDB
* **Orchestration:** LangChain

## Setup
1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Add your API key to `.env`.
4.  Run the app: `streamlit run app.py`