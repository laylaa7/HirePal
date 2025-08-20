# file: chat_rag.py
from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_vertexai.vectorstores import VectorSearchVectorStore
from google.cloud import aiplatform
import uuid  # <-- ADD THIS IMPORT
from typing import List, Dict  # You might want to add Dict for type hinting too
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config_manager import ConfigManager

# Get the single instance of the configuration
config = ConfigManager()

PROJECT_ID = config.PROJECT_ID
BUCKET = "cv-rag-west-4"
REGION = config.REGION
INDEX_ID = "3037589987731177472"
INDEX_DISPLAY_NAME = "cv-index-rag"
ENDPOINT_ID = "7123093721570082816"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Embeddings (must match index dims used at ingestion)
emb = VertexAIEmbeddings(
    model_name="text-embedding-005",
    project=PROJECT_ID,
    location=REGION,
)

# Vector store / retriever
index = aiplatform.MatchingEngineIndex(INDEX_ID)
endpoint = aiplatform.MatchingEngineIndexEndpoint(ENDPOINT_ID)
vector_store = VectorSearchVectorStore.from_components(
    embedding=emb,
    index_id=INDEX_ID,
    endpoint_id=ENDPOINT_ID,
    gcs_bucket_name=BUCKET,
    project_id=PROJECT_ID,
    region=REGION,
)
retriever = vector_store.as_retriever(search_kwargs={"k": 20}, score_threshold = {0.2})

# Chat model (Gemini on Vertex AI)
llm = ChatVertexAI(
    model="gemini-2.5-flash", 
    project=PROJECT_ID,
    location=REGION,
    temperature=0.2,
)

# System prompt for recruiter-style answers with citations back to files
SYSTEM = """You are a helpful CV assistant for a recruiting team.
Use the retrieved chunks to answer.
Return brief, structured results with candidate summaries.
Always include the source filename(s) for each suggestion from metadata.filename.
If the user asks for people "with X", list top matches with 1–2 bullets each."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
    ("system", "Context chunks:\n{context}")
])

# file: chat_rag.py
# ... (keep previous imports)
def ask(question: str, history: BaseChatMessageHistory) -> dict:
    """
    Sends a question to the RAG chatbot and returns a structured response.
    """
    print(f"\n--- New Question: '{question}' ---")  # Debug print

    # Retrieve relevant documents
    docs = retriever.invoke(question)
    print(f"Number of CV chunks found: {len(docs)}")  # Debug print

    # Format context for the LLM
    context = "\n\n---\n\n".join(
        f"[{i+1}] {d.page_content[:1200]}\n(source: {d.metadata.get('filename')})"
        for i, d in enumerate(docs)
    )

    # Build the messages for the LLM
    msgs = prompt.format_messages(history=history.messages, question=question, context=context)

    # Get the LLM's text response
    resp = llm.invoke(msgs)

    # Update history
    history.add_user_message(question)
    history.add_ai_message(resp.content)

    # --- NEW LOGIC: Always return structured data if we found CVs ---
    if docs:  # Simplified condition: if we found any CV chunks
        print("Found CVs. Returning candidate cards data.")  # Debug print
        candidate_list = []
        for doc in docs:
            filename = doc.metadata.get('filename', '')
            # A simple cleanup: remove '.pdf' and common separators
            name_from_file = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
            
            # Try to extract a first name from the filename as a fallback
            name_parts = name_from_file.split()
            first_name = name_parts[0] if name_parts else "Candidate"

            # Create a candidate object for the frontend card.
            candidate_data = {
                "id": str(uuid.uuid4()),
                "name": name_from_file,
                "role": "AI Candidate",  # You can make this more dynamic based on the content
                "avatar": "",
                "skills": extract_skills_from_text(doc.page_content),  # See function below
                "location": "", 
                "experience": "",
                "cvUrl": f"gs://{BUCKET}/{filename}",  # Or doc.metadata.get('gcs_uri', '')
                "initials": ''.join([n[0] for n in name_from_file.split()[:2]]).upper(),
                "gradientFrom": "#667eea",
                "gradientTo": "#764ba2",
                "text": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content
            }
            candidate_list.append(candidate_data)
        
        # Return structured data for candidate cards
        return {
            "type": "candidates",
            "content": candidate_list,
            "llmResponse": resp.content  # Also include the LLM's text summary
        }
    else:
        # If no CVs were found, return just the text
        print("No CVs found. Returning text response only.")  # Debug print
        return {
            "type": "text",
            "content": resp.content
        }

# Helper function to extract skills (optional but makes cards much better)
def extract_skills_from_text(text: str) -> list:
    """A simple function to extract potential skills from CV text."""
    skills_keywords = ["python", "java", "react", "node", "js", "javascript", "machine learning", "ai", 
                      "tensorflow", "pytorch", "sql", "aws", "docker", "kubernetes", "git", 
                      "c++", "html", "css", "fastapi", "django", "flask", "vue", "angular"]
    found_skills = []
    text_lower = text.lower()
    for skill in skills_keywords:
        if skill in text_lower:
            # Capitalize the skill for display
            found_skills.append(skill.title())
    # Return unique skills, max 5 to not overcrowd the card
    return list(set(found_skills))[:5]