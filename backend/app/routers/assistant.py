from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.llm.assistant_service import process_message


router = APIRouter(
    prefix="/assistant",
    tags=["Assistant IA"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    response = process_message(
        db=db,
        session_id=request.session_id,
        user_message=request.message,
    )

    return {
        "response": response,
        "session_id": request.session_id,
    }