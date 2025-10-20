from pydantic import BaseModel
from typing import Optional, List

class StructuredRequest(BaseModel):
    position: Optional[str] = ""
    skills: Optional[str] = ""
    working_mode: Optional[str] = ""
    salary: Optional[int] = 0
    workplace: Optional[str] = ""
    offer_details: Optional[str] = ""
    experience_level: Optional[str] = ""
    availability: Optional[str] = ""

class ChatRequest(BaseModel):
    text: str

class JobOut(BaseModel):
    id: int
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    match_score: float
    link: Optional[str]

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
