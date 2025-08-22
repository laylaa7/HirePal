# file: chat_rag.py
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_vertexai.vectorstores import VectorSearchVectorStore
from google.cloud import aiplatform

from config_manager import ConfigManager
from models import CandidatesResponse, Candidate # Assuming your pydantic models are in a models.py file

# Get the single instance of the configuration
config = ConfigManager()

PROJECT_ID = config.PROJECT_ID
BUCKET = "cv-rag-west-4" # This bucket name is used to construct the public URL for the CVs.
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
retriever = vector_store.as_retriever(search_kwargs={"k": 20}, score_threshold=0.5)

# Chat model (Gemini on Vertex AI)
llm = ChatVertexAI(
    model="gemini-2.5-flash", 
    project=PROJECT_ID,
    location=REGION,
    temperature=0.2,
).with_structured_output(CandidatesResponse)

# UPDATED PROMPT: Added a new rule for generating the full public CV link.
SYSTEM = """
You are an AI assistant called HirePal that helps recruiters analyze CVs and support the hiring process for Deloitte Innovation Hub.

Rules:
- If multiple pieces of information refer to the same candidate, combine their relevant content into a single, comprehensive entry. Each unique candidate must appear only once in the final 'candidates' list.
- Only answer questions related to candidates, their CVs, or the application process.
- If the user asks about anything unrelated (politics, jokes, news, sports, etc.), politely decline and redirect.
- Never invent candidate data. Only use the provided CONTEXT.
- For the cv_link field, you **must** construct the full public URL for the PDF file. The URL should follow this format: https://storage.googleapis.com/cv-rag-west-4/<filename>, where <filename> is the name of the file found in the document metadata.

INSTRUCTIONS:
- Based on the USER QUERY and CONTEXT, generate a reply and a list of candidates.
- If no matches were found in the CONTEXT, provide a reply stating this and an empty list of candidates.
- If the query is off-topic, provide a reply stating this and an empty list of candidates.
- For each unique matching candidate, extract their Name, a summary of their combined background/skills, and the link to their CV.
- Ensure the 'reply' field contains a helpful, conversational message.
- If a system error occurs, provide a relevant error message in the 'reply' field and an empty candidates list.
- When i ask something regarding the previous result, you should use the HISTORY of the conversation to answer my question.
- When asked about years of experience, you should estimate based on the information given in the CVs about experience in the company's domain, if no work experience found it is fine.

HISTORY is the previous conversation between the user and you:
{history}
"""

# UPDATED PROMPT TEMPLATE: Removed the redundant context message.
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
    ("system", "Context chunks:\n{context}")
])

def ask(question: str, history: BaseChatMessageHistory) -> dict:
    """
    Sends a question to the RAG chatbot and returns the response, maintaining history.
    
    Args:
        question (str): The user's question.
        history (BaseChatMessageHistory): The conversation history object for the session.

    Returns:
        dict: The chatbot's response as a Python dictionary.
    """
    try:
        # retrieve relevant documents based on the user's question
        docs = retriever.invoke(question) 
        
        # format the retrieved documents into a context string for the model
        context = "\n\n---\n\n".join(
            f"[{i+1}] {d.page_content[:1200]}\n(source: {d.metadata.get('filename')})"
            for i, d in enumerate(docs)
        )
        
        # build the full messages list for the model, including history and context
        msgs = prompt.format_messages(history=history.messages, question=question, context=context)
        
        # call the language model to generate a response
        resp = llm.invoke(msgs)
        
        # update the conversation history with the user's message and the AI's response
        history.add_user_message(question)
        history.add_ai_message(resp.model_dump_json())
        
        # Return the response as a dictionary
        return resp.model_dump()
    except Exception as e:
        print(f"An error occurred in the ask function: {e}")
        # Return a structured error response
        return {
            "reply": f"An error occurred: {e}. Please try again.",
            "candidates": []
        }

# file: app.py
# ... (unchanged)

# file: models.py
from pydantic import BaseModel, Field
from typing import List, Optional

# Define the data structure for a single candidate
class Candidate(BaseModel):
    name: str = Field(description="The full name of the candidate.")
    relevant_content: str = Field(description="A summary of the candidate's skills and experience relevant to the query.")
    cv_link: Optional[str] = Field(None, description="The filename or link to the candidate's CV.")

# Define the overall response structure
class CandidatesResponse(BaseModel):
    reply: str = Field(description="A conversational and professional message for the recruiter.")
    candidates: List[Candidate] = Field(description="A list of candidates that match the search criteria. This list should be empty if no candidates were found.")
