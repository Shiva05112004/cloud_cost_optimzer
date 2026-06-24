from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.rag.rag_chain import ask_cloudopt
from app.routes.auth import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    aws_context: dict   # pass current instance/cost data from frontend


class ChatResponse(BaseModel):
    answer: str
    question: str


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest, _user=Depends(get_current_user)):
    """
    RAG-powered chat endpoint.
    Frontend sends the user's question + current AWS context.
    Returns a grounded LLM answer.
    """
    answer = ask_cloudopt(payload.question, payload.aws_context)
    return ChatResponse(answer=answer, question=payload.question)