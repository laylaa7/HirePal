# app.py

import uvicorn
import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
# Assuming your chat_rag.py is in the same directory
from chat_rag_final import ask, InMemoryChatMessageHistory # Import the ask function and history classes

# A dictionary to store chat histories keyed by a unique session ID
chat_histories: Dict[str, InMemoryChatMessageHistory] = {}

# Define Pydantic models for the request and response bodies
class Query(BaseModel):
    session_id: str
    question: str

class SessionResponse(BaseModel):
    session_id: str
    message: str

# Initialize the FastAPI application
app = FastAPI(
    title="RAG Chatbot API",
    description="A simple API to interact with a CV-focused RAG chatbot with history persistence."
)


# Since nextjs is running on localhost:3000, we allow CORS for that origin
# This is necessary for the frontend to communicate with the backend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Added 127.0.0.1 as well
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly list methods
    allow_headers=["*"],
    expose_headers=["*"] # This can help with more complex scenarios
)

# A simple health check endpoint
@app.get("/")
def read_root():
    return {"message": "RAG Chatbot is running!"}

@app.get("/new_session", response_model=SessionResponse)
def get_new_session():
    """
    Creates a new chat session and returns its ID.
    This ID should be used for subsequent requests to maintain conversation history.
    """
    session_id = str(uuid.uuid4())
    chat_histories[session_id] = InMemoryChatMessageHistory()
    return {"session_id": session_id, "message": "New session created."}

# Endpoint to handle user queries with history
# app.py
# ... (keep previous code)

@app.post("/ask")
def chat_with_bot_with_history(query: Query):
    """
    Sends a question to the RAG chatbot and returns the response, maintaining history.
    """
    session_id = query.session_id
    question = query.question

    if session_id not in chat_histories:
        raise HTTPException(status_code=404, detail="Session not found.")

    session_history = chat_histories[session_id]

    try:
        # Call the ask function, which now returns a dict
        response_data = ask(question, session_history)
        
        # Add type field for frontend to distinguish response types
        if response_data.get("candidates"):
            response_data["type"] = "candidates"
        else:
            response_data["type"] = "text"
            
        return response_data
    except Exception as e:
        # Return a structured error as well
        return {"type": "error", "content": f"An error occurred: {str(e)}"}
      
if __name__ == "__main__":
    # Get the port from an environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Run the application with uvicorn
    # The "app:app" syntax means:
    # app is the name of the file (app.py)
    # app is the name of the FastAPI object within the file
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
