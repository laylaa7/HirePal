# # file: chat_rag.py
# from typing import List
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.chat_history import InMemoryChatMessageHistory

# from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
# from langchain_google_vertexai.vectorstores import VectorSearchVectorStore
# from google.cloud import aiplatform

# from config_manager import ConfigManager
# from models import CandidatesResponse

# # Get the single instance of the configuration
# config = ConfigManager()

# PROJECT_ID = config.PROJECT_ID
# BUCKET = "cv-rag-west-4"
# REGION = config.REGION
# INDEX_ID = "3037589987731177472"
# INDEX_DISPLAY_NAME = "cv-index-rag"
# ENDPOINT_ID = "7123093721570082816"

# aiplatform.init(project=PROJECT_ID, location=REGION)

# # Embeddings (must match index dims used at ingestion)
# emb = VertexAIEmbeddings(
#     model_name="text-embedding-005",
#     project=PROJECT_ID,
#     location=REGION,
# )

# # Vector store / retriever
# index = aiplatform.MatchingEngineIndex(INDEX_ID)
# endpoint = aiplatform.MatchingEngineIndexEndpoint(ENDPOINT_ID)
# vector_store = VectorSearchVectorStore.from_components(
#     embedding=emb,
#     index_id=INDEX_ID,
#     endpoint_id=ENDPOINT_ID,
#     gcs_bucket_name=BUCKET,
#     project_id=PROJECT_ID,
#     region=REGION,
# )
# retriever = vector_store.as_retriever(search_kwargs={"k": 20}, score_threshold = {0.5})

# # Chat model (Gemini on Vertex AI)
# llm = ChatVertexAI(
#     model="gemini-2.5-flash", 
#     project=PROJECT_ID,
#     location=REGION,
#     temperature=0.2,
# ).with_structured_output(CandidatesResponse)

# # System prompt for recruiter-style answers with citations back to files

# # CONTEXT:
# # {context}

# # USER QUERY:
# # {query}

# SYSTEM = prompt_template = """
# You are an AI assistant that helps recruiters analyze CVs and support the hiring process.

# Rules:
# - Output a single JSON object that strictly adheres to the provided structures. **Do not include any other text or characters before or after the JSON.**
# - Only answer questions related to candidates, their CVs, or the application process.
# - If the user asks about anything unrelated (politics, jokes, news, sports, etc.), politely decline and redirect.
# - Never invent candidate data. Only use the provided CONTEXT.
# - Never include anything before or after the response JSON object.

# Example 1 (Candidates Found):

# {{
#   "reply": "Here is a list of candidates that match your criteria:",
#   "candidates": [
#     {{
#       "name": "Jane Doe",
#       "relevant_content": "5 years experience in backend development, specialized in Python and Django.",
#       "cv_link": "[https://example.com/cv/jane_doe.pdf](https://example.com/cv/jane_doe.pdf)"
#     }},
#     {{
#       "name": "John Smith",
#       "relevant_content": "Data scientist with expertise in NLP and machine learning, 3 published papers.",
#       "cv_link": "[https://example.com/cv/john_smith.pdf](https://example.com/cv/john_smith.pdf)"
#     }}
#   ]
# }}


# Example 2 (No Candidates Found or off-topic query):

# {{
#   "reply": "I couldn’t find any matching candidates at the moment. Please ask a question related to recruitment and talent acquisition.",
#   "candidates": []
# }}


# INSTRUCTIONS:
# - Based on the USER QUERY and CONTEXT, generate a JSON object using the exact structure specified above.
# - If no matches were found in the CONTEXT, use the "No Candidates Found" JSON structure.
# - If the query is off-topic, use the "No Candidates Found" JSON structure and include a polite redirection message in the "reply" field.
# - For each matching candidate, extract their Name, a summary of their background/skills, and the link to their CV.
# - Ensure the "reply" field contains a helpful, conversational message.
# - If a system error occurs, use the "No Candidates Found" JSON structure with a relevant error message in the "reply" field.
# - Make sure to clean to response scheme to ensure correct pure JSON object output only.
# """







# prompt = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM),
#     MessagesPlaceholder("history"),
#     ("human", "{question}"),
#     ("system", "Context chunks:\n{context}")
# ])

# def ask(question: str, history: BaseChatMessageHistory) -> str:
#     """
#     Sends a question to the RAG chatbot and returns the response, maintaining history.
    
#     Args:
#         question (str): The user's question.
#         history (BaseChatMessageHistory): The conversation history object for the session.

#     Returns:
#         str: The chatbot's response.
#     """
#     # retrieve relevant documents based on the user's question
#     docs = retriever.invoke(question) 
    
#     # format the retrieved documents into a context string for the model
#     context = "\n\n---\n\n".join(
#         f"[{i+1}] {d.page_content[:1200]}\n(source: {d.metadata.get('filename')})"
#         for i, d in enumerate(docs)
#     )
    
#     # build the full messages list for the model, including history and context
#     msgs = prompt.format_messages(history=history.messages, question=question, context=context)
    
#     # call the language model to generate a response
#     resp = llm.invoke(msgs)
    
#     # update the conversation history with the user's message and the AI's response
#     history.add_user_message(question)
#     history.add_ai_message(resp.content)
    
#     return resp.model_dump()
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
retriever = vector_store.as_retriever(search_kwargs={"k": 20}, score_threshold=0.5)

# Chat model (Gemini on Vertex AI)
llm = ChatVertexAI(
    model="gemini-2.5-flash", 
    project=PROJECT_ID,
    location=REGION,
    temperature=0.2,
).with_structured_output(CandidatesResponse)

# UPDATED PROMPT: Removed all JSON formatting and examples.
# The model now only needs instructions on content and persona.
# UPDATED PROMPT: Added a new rule for consolidating candidate information.
SYSTEM = """
You are an AI assistant called HirePal that helps recruiters analyze CVs and support the hiring process for Deloitte Innovation Hub.

Rules:
- If multiple pieces of information refer to the same candidate, combine their relevant content into a single, comprehensive entry. Each unique candidate must appear only once in the final 'candidates' list.
- Only answer questions related to candidates, their CVs, or the application process.
- If the user asks about anything unrelated (politics, jokes, news, sports, etc.), politely decline and redirect.
- Never invent candidate data. Only use the provided CONTEXT.

INSTRUCTIONS:
- Based on the USER QUERY and CONTEXT, generate a reply and a list of candidates.
- If no matches were found in the CONTEXT, provide a reply stating this and an empty list of candidates.
- If the query is off-topic, provide a reply stating this and an empty list of candidates.
- For each unique matching candidate, extract their Name, a summary of their combined background/skills, and the link to their CV.
- Ensure the 'reply' field contains a helpful, conversational message.
- If a system error occurs, provide a relevant error message in the 'reply' field and an empty candidates list.
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
    # retrieve relevant documents based on the user's question
    docs = retriever.invoke(question) 
    
    # format the retrieved documents into a context string for the model
    context = "\n\n---\n\n".join(
        f"[{i+1}] {d.page_content[:1200]}\n(source: {d.metadata.get('filename')})"
        for i, d in enumerate(docs)
    )
    
    # build the full messages list for the model, including history and context
    # Note: The context is now passed implicitly to the SYSTEM prompt via the format_messages call.
    msgs = prompt.format_messages(history=history.messages, question=question, context=context)
    
    # call the language model to generate a response
    # The 'resp' object is now a Pydantic object (CandidatesResponse)
    resp = llm.invoke(msgs)
    
    # update the conversation history with the user's message and the AI's response
    # CORRECTED: Use model_dump_json() to add the JSON string to history
    history.add_user_message(question)
    history.add_ai_message(resp.model_dump_json())
    
    # Return the response as a dictionary
    # CORRECTED: Use model_dump() to convert the Pydantic object to a dictionary
    return resp.model_dump()
