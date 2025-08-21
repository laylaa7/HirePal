<img width="256" height="171" alt="image" src="https://github.com/user-attachments/assets/52f4a171-5566-42c1-a994-9d2e4551427e" />
 
**An AI-Powered Recruiter Co-pilot** | Streamline your hiring process with an intelligent chat interface that helps you examine, compare, and evaluate CVs at lightning speed.  

![Next.js](https://img.shields.io/badge/Next.js-15.1.6-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi)
![LangChain](https://img.shields.io/badge/LangChain-0.1.16-FF6A00?style=for-the-badge)
![GCP](https://img.shields.io/badge/GCP-Cloud-4285F4?style=for-the-badge&logo=googlecloud)

---
<img width="1425" height="694" alt="image" src="https://github.com/user-attachments/assets/04843b81-4f82-4c11-8548-92f910baaae1" />

## Overview  
HirePal is an **intelligent chat-based dashboard for recruiters**.  
It leverages **AI (RAG with LangChain)** to let recruiters interact with a database of CVs **conversationally**. Instead of manually skimming through hundreds of PDFs, recruiters can ask **natural language questions** to instantly identify the most qualified candidates.  

### Key Problem it Solves  
- Eliminates tedious, manual CV screening.  
- Reduces **time-to-hire** significantly.  
- Uncovers **deep candidate insights** that might otherwise be overlooked.  

---

## Core Features  
- **Natural Language Queries**  
   *Example:*  
   - “Find me all candidates with 5+ years of Python experience and a Master’s degree.”  
   - “Show me backend engineers who have worked at FAANG companies.”  
   - “Compare the skillsets of John Doe and Jane Smith.”  

- **Interactive Chat Dashboard** — A modern Next.js interface built for productivity.  

-  **Advanced CV Processing** — Understands context & nuances in CVs with **LangChain + RAG**.  

-  **Blazing Fast API** — Built on **FastAPI** for low-latency responses.  

- **Multi-CV Analysis** — Upload & process multiple CVs simultaneously into a searchable knowledge base.  

---

##  Tech Stack  

| Layer               | Technology |
|----------------------|------------|
| **Frontend**         | Next.js 15, React, Tailwind CSS, Axios |
| **Backend**          | Python, FastAPI, Uvicorn |
| **AI & NLP**         | LangChain, OpenAI API / Gemini , Sentence Transformers |
| **Vector Database**  | ChromaDB / Pinecone / FAISS |
| **Document Parsing** | Unstructured.io / PyPDF2, LangChain Document Loaders |
| **Cloud Hosting**    | **Google Cloud Platform (GCP)** — Compute Engine, Cloud Run, Vertex AI, Cloud Storage |
| **HTTP Client**      | Axios |

---

## 📦 Installation & Setup  

###  Prerequisites  
- Node.js (v18+)  
- Python (3.9+)  
- `pip` (Python package manager)   
- *(Optional)* GCP account + project setup  

---

### Clone the Repository 
```bash
git clone https://github.com/your-username/HirePal.git
cd HirePal
```
### set up the backend
```bash
cd server

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

uvicorn app:app --reload --host 0.0.0.0 --port 8000 &
```

### set up the frontend
``` bash
# Install dependencies
npm install
```
API available at: http://localhost:8000

Swagger docs: http://localhost:8000/docs

Frontend available at: http://localhost:3000

---

##  How to Use HirePal  

- **Upload CVs:**  
  Use the dashboard interface to upload multiple CVs (PDF/DOCX).  
  The backend will process them, chunk the text, and embed them into the vector database.  

- **Start Chatting:**  
  Navigate to the chat interface.  
  - **Ask Questions:** Type your questions in natural language. For example:  
    - “List all candidates who know React and Node.js.”  
    - “What is this candidate's most recent work experience?”  

- **Evaluate Candidates:**  
  Use the AI's insights to quickly shortlist and compare potential hires.  


---
🤝 Contributing

Contributions are welcome! Please open issues & pull requests to improve HirePal.
