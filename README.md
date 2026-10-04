# 📚 StudyBuddy — AI-Powered Personalized Learning Assistant

StudyBuddy is a local AI-powered learning assistant that transforms study PDFs into an interactive learning experience.

It allows students to upload study material, ask questions from their documents, generate AI-powered summaries and quizzes, and track their learning performance.

---

## ✨ Features

### 📄 PDF Processing

* Upload PDF study material
* Extract and clean PDF text
* Split documents into manageable chunks
* Generate embeddings for semantic search
* Store document vectors using ChromaDB
* Prevent duplicate document ingestion

### 💬 AI-Powered Q&A

* Ask questions about uploaded study material
* Semantic retrieval using vector embeddings
* Context-aware answers using Qwen 2.5
* Answers are restricted to the uploaded material
* Reduces hallucination and off-topic answers
* Displays source information

### 📝 AI Summary

* Generate structured summaries from uploaded documents
* Extract important concepts and definitions
* Organize information into revision-friendly sections
* Uses local Ollama inference
* Optimized section-based summarization

### 🧠 AI Quiz Generator

* Generate multiple-choice questions from study material
* Select the number of questions
* Automatic quiz validation
* Detects invalid answers and duplicate options
* Provides explanations
* Automatic score calculation
* Displays answer review

### 📊 Learning Dashboard

* Track total quizzes
* Average score
* Best score
* Questions attempted
* Quiz history
* Performance over time
* Per-document performance
* Learning progress visualization

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │      Streamlit      │
                    │    Web Interface    │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌───────────┐   ┌───────────┐
        │    Q&A    │    │  Summary  │   │   Quiz    │
        │    RAG    │    │  Generator│   │ Generator │
        └─────┬─────┘    └─────┬─────┘   └─────┬─────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │     ChromaDB        │
                    │   Vector Database   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Ollama + Qwen 2.5   │
                    │    Local LLM        │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ nomic-embed-text    │
                    │    Embeddings       │
                    └─────────────────────┘
```

---

## 🔄 RAG Pipeline

StudyBuddy uses a Retrieval-Augmented Generation pipeline:

```text
PDF
 ↓
Text Extraction
 ↓
Text Cleaning
 ↓
Chunking
 ↓
Embedding Generation
 ↓
ChromaDB
 ↓
Semantic Retrieval
 ↓
Relevant Context
 ↓
Qwen 2.5
 ↓
Grounded Answer
```

This allows the application to answer questions using the user's uploaded study material instead of relying only on the model's general knowledge.

---

## 🛠️ Technology Stack

| Technology       | Purpose            |
| ---------------- | ------------------ |
| Python           | Core application   |
| Streamlit        | Web interface      |
| Ollama           | Local AI inference |
| Qwen 2.5 1.5B    | Language model     |
| nomic-embed-text | Text embeddings    |
| ChromaDB         | Vector database    |
| PyMuPDF          | PDF processing     |
| Pandas           | Data analysis      |
| Git & GitHub     | Version control    |

---

## 📁 Project Structure

```text
StudyBuddy/
│
├── app/
│   ├── ingest.py
│   ├── rag.py
│   ├── summarizer.py
│   ├── quiz.py
│   ├── progress.py
│   └── vector_store.py
│
├── frontend/
│   └── app.py
│
├── data/
│   └── documents/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/aryanchande/StudyBuddy.git
cd StudyBuddy
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama from:

https://ollama.com/

Then download the required models:

```powershell
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

### 5. Add study material

Place your PDF files inside:

```text
data/documents/
```

### 6. Ingest a PDF

From the project root:

```powershell
python app/ingest.py
```

Enter the PDF path when prompted.

### 7. Start StudyBuddy

```powershell
streamlit run frontend/app.py
```

---

## 🧪 Example

For example, after uploading:

```text
chapter 1 DBMS.pdf
```

StudyBuddy can answer questions such as:

```text
What is a DBMS?
```

It can also generate:

* A structured summary
* Multiple-choice questions
* Quiz explanations
* Performance statistics

Questions outside the uploaded material can be rejected instead of answered using unrelated model knowledge.

---

## 🎯 Project Goals

StudyBuddy was designed to explore practical applications of:

* Retrieval-Augmented Generation
* Vector databases
* Local LLM inference
* Semantic search
* AI-assisted education
* Document processing
* AI evaluation and validation
* Interactive learning systems

---

## 🔮 Future Improvements

Planned improvements include:

* User authentication
* Multiple subject workspaces
* Flashcard generation
* More advanced question difficulty levels
* Better summary optimization
* Cloud deployment
* Persistent user profiles
* More detailed learning analytics
* Model selection
* Export summaries and quizzes
* Voice-based interaction

---

## 👨‍💻 Author

**Aryan Chande**

B.Tech Hons. CSE (AI)

GitHub: https://github.com/aryanchande

LinkedIn: https://www.linkedin.com/in/aryan-chande-7b04a1369

---

## ⭐ Project Status

StudyBuddy is an actively developed educational AI project.

Current functionality includes:

**PDF Processing → RAG Q&A → AI Summary → AI Quiz → Progress Tracking → Dashboard Analytics**
