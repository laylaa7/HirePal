from pydantic import BaseModel, Field
from typing import List, Optional

# Define the data structure for a single candidate
class Candidate(BaseModel):
    name: str = Field(description="The full name of the candidate.")
    relevant_content: str = Field(description="A summary of the candidate's skills and experience relevant to the query.")
    cv_link: str = Field(description="The filename or link to the candidate's CV.")

# Define the overall response structure
class CandidatesResponse(BaseModel):
    reply: str = Field(description="A conversational and professional message for the recruiter.")
    candidates: List[Candidate] = Field(description="A list of candidates that match the search criteria. This list should be empty if no candidates were found.")