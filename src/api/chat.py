from fastapi import APIRouter, HTTPException
from src.chat.models import ChatRequest, ChatResponse
from src.chat.service import chat_service

router = APIRouter(prefix="/chat", tags=["Natural Language Analyst"])

@router.post("/aq", response_model=ChatResponse)
async def ask_air_quality(request: ChatRequest):
    """
    Ask a natural language question about air quality.
    """
    response = chat_service.ask(request)
    return response
