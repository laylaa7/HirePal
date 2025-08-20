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
retriever = vector_store.as_retriever(search_kwargs={"k": 8}, score_threshold = {0.5})

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
    print(f"\n--- New Question: '{question}' ---")
    
    # 1. SEMANTIC SEARCH: Get relevant chunks using vector similarity
    docs = retriever.invoke(question)
    print(f"Number of CV chunks found by semantic search: {len(docs)}")
    
    # --- HYBRID SEARCH: COMBINE SEMANTIC + KEYWORD FILTERING ---
    # Detect if user is searching for a specific name
    question_lower = question.lower()
    name_keywords = ["name", "called", "named", "find", "search for", "who is"]
    
    if any(keyword in question_lower for keyword in name_keywords):
        # Extract potential names (capitalized words that might be names)
        potential_names = []
        for word in question.split():
            if word.istitle() and len(word) > 2:  # Simple name detection
                potential_names.append(word.lower())
        
        print(f"Potential names detected: {potential_names}")
        
        if potential_names:
            # Apply keyword filter ON TOP of semantic results
            filtered_docs = []
            for doc in docs:
                doc_text_lower = doc.page_content.lower()
                # Keep document if it contains ANY of the potential names
                if any(name in doc_text_lower for name in potential_names):
                    filtered_docs.append(doc)
            
            # ONLY replace results if we found keyword matches
            # This preserves semantic search when no names are found in documents
            if filtered_docs:
                print(f"After keyword filtering: {len(filtered_docs)} chunks contain the name(s)")
                docs = filtered_docs
            else:
                print("No documents contain the specified name(s), using semantic results only")  # Debug print

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

    # --- INTENT DETECTION LOGIC --- 
    # Define triggers for candidate search
    search_intent_keywords = [
        "find", "search", "show", "look for", "need", "hire", "recruit", "candidate", 
        "developer", "engineer", "designer", "who has", "with experience", "skill", "java", 
        "python", "react", "node", "aws", "sql", "experienced", "senior", "junior"
    ]

    # Define triggers for conversational intent (should NOT return candidates)
    conversation_intent_keywords = [
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "who are you", "what is your name", "how are you", "thank", "thanks", 
        "bye", "goodbye", "ok", "okay", "yes", "no", "not sure", "explain", "what can you do"
    ]

    user_query_lower = question.lower()

    # Check if this is clearly a conversation, not a search
    is_conversation = any(keyword in user_query_lower for keyword in conversation_intent_keywords)

    # Check if this is clearly a candidate search  
    is_candidate_search = any(keyword in user_query_lower for keyword in search_intent_keywords)

    # Check if the user is likely giving more context about a role
    is_role_description = ("looking for" in user_query_lower or 
                           "role is" in user_query_lower or 
                           "position for" in user_query_lower)

    print(f"Conversation intent: {is_conversation}")
    print(f"Search intent: {is_candidate_search}")
    print(f"Role description: {is_role_description}")

    # DECISION TREE: Should we return candidates?
    should_return_candidates = False

    if is_conversation:
        # Definitely don't return candidates for greetings/etc.
        should_return_candidates = False
    elif is_candidate_search:
        # Definitely return candidates for clear search queries
        should_return_candidates = True
    elif is_role_description and docs:
        # If user describes a role AND we found relevant CVs, return them
        should_return_candidates = True  
    elif not docs:
        # If no CVs were found at all, never return candidates
        should_return_candidates = False
    else:
        # Default: be conservative and don't return candidates for ambiguous queries
        should_return_candidates = False

    print(f"Decision: return candidates = {should_return_candidates}\n")
    # --- END INTENT DETECTION LOGIC ---

    # --- NEW LOGIC: Group chunks by CV file ---
    if should_return_candidates:
        print("Preparing candidate cards...")
        candidate_dict = {}  # Key: filename, Value: {'doc': best_doc}

        for doc in docs:
            filename = doc.metadata.get('filename', 'unknown.pdf')
            
            # Simple check if this is likely a CV file
            if not filename.lower().endswith('.pdf'):
                continue
                
            # If we haven't seen this CV, keep it
            if filename not in candidate_dict:
                candidate_dict[filename] = {
                    'doc': doc,
                }

        # Get the best chunk for each unique CV
        unique_candidate_docs = [info['doc'] for info in candidate_dict.values()]
        print(f"Number of unique candidates found: {len(unique_candidate_docs)}")
        
        # Only take the top 5 most relevant unique candidates
        top_candidates = unique_candidate_docs[:5]
        
        candidate_list = []
        for doc in top_candidates:
            filename = doc.metadata.get('filename', '')
            name_from_file = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
            name_parts = name_from_file.split()
            first_name = name_parts[0] if name_parts else "Candidate"

            candidate_data = {
                "id": str(uuid.uuid4()),
                "name": name_from_file,
                "role": "Potential Candidate", 
                "avatar": "",
                "skills": extract_skills_from_text(doc.page_content),
                "location": "", 
                "experience": "",
                "cvUrl": f"gs://{BUCKET}/{filename}", 
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
            "llmResponse": resp.content 
        }
    else:
        # For conversational messages, return just the text response
        print("Returning text response only.")
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