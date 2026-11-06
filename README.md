# Interviewer-ki-job-kha-jaunga

AI-powered interview mentoring platform that helps candidates practice mock interviews, enables subject-matter experts to contribute knowledge, and gives leadership a view of evaluation performance.

## Overview

This project combines a Streamlit web app with LangChain, Groq-powered LLMs, and a FAISS vector database to create a role-based interview preparation platform.

It is designed around three user personas:

- Candidate: practice mock interviews and receive readiness feedback
- Feeder: upload or provide SME knowledge for interview material generation
- Executive: review summary metrics and evaluation trends

## Features

### Candidate Experience
- Topic-based study mode with question-and-answer material
- Mock interview flow with 10-question quiz evaluation
- AI-generated follow-up questions
- Final readiness summary with scoring feedback

### Feeder / SME Experience
- Accepts raw expert input
- Converts input into structured interview Q&A and rubric data
- Stores materials in a retrieval system for future use

### Executive Experience
- Tracks interview counts
- Calculates average readiness scores
- Stores evaluation metrics for dashboard-style review

## Architecture

```text
Interviewer-ki-job-kha-jaunga/
├── backend/
│   ├── agents/
│   │   ├── candidate_agent.py
│   │   ├── executive_agent.py
│   │   ├── feeder_agent.py
│   │   └── __init__.py
│   ├── database/
│   │   ├── faiss_manager.py
│   │   └── __init__.py
│   └── __init__.py
├── frontend/
│   └── app.py
├── faiss_store/
├── .env
├── main.py
├── requirements.txt
├── README.md
└── .git/
```

## Tech Stack

- Python
- Streamlit
- LangChain
- Groq LLMs
- Hugging Face embeddings
- FAISS vector store
- Python-dotenv

## How It Works

1. The Streamlit frontend loads a role-based interface.
2. The candidate flow asks interview questions based on a topic.
3. Retrieval is performed using FAISS to pull relevant context from stored knowledge.
4. A Groq LLM generates interview questions, study material, or summary feedback.
5. Feeder content is transformed into structured interview data and added to the vector database.
6. Executive metrics are logged as JSON to track evaluation performance.

## Prerequisites

- Python 3.10+
- A valid Groq API key
- Internet access for model inference and package installation

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/DeepRoy2002/Interviewer-ki-job-kha-jaunga.git
cd Interviewer-ki-job-kha-jaunga
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama3-8b-8192
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_STORE_PATH=faiss_store
```

## Run the App

From the project root:

```bash
streamlit run main.py
```

This starts the Streamlit app and opens the interview mentoring platform in the browser.

## Project Files

### Entry point
- `main.py` starts the app using Streamlit.

### Frontend
- `frontend/app.py` contains the UI and role-selection flow.

### Agents
- `backend/agents/candidate_agent.py` handles candidate Q&A and scoring logic.
- `backend/agents/feeder_agent.py` transforms raw SME input into structured knowledge.
- `backend/agents/executive_agent.py` records evaluation metrics.

### Data layer
- `backend/database/faiss_manager.py` manages the vector database and similarity search.
- `faiss_store/` stores the FAISS index and related embeddings.

## Notes

This project is a functional MVP/prototype and is best suited for experimentation and extension. It is not yet structured as a production-grade application with persistent user accounts, secure data storage, or a fully hardened API layer.

## Future Improvements

- Add authentication and role-based user management
- Store interview data in a database instead of JSON files
- Add a proper executive dashboard UI with charts
- Improve prompt reliability and scoring consistency
- Add tests for agent logic and FAISS persistence
- Support multiple topic domains and data ingestion formats
