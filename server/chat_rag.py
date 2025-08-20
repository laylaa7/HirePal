# file: chat_rag.py
from typing import List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_google_vertexai.vectorstores import VectorSearchVectorStore
from google.cloud import aiplatform

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

def ask(question: str, history: BaseChatMessageHistory) -> str:
    """
    Sends a question to the RAG chatbot and returns the response, maintaining history.
    
    Args:
        question (str): The user's question.
        history (BaseChatMessageHistory): The conversation history object for the session.

    Returns:
        str: The chatbot's response.
    """
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
    history.add_ai_message(resp.content)
    
    return resp.content

