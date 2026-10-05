from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.rag.generation.rag_service import RAGService
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.message_source_repository import MessageSourceRepository

from app.core.metrics import (
    CHAT_REQUESTS_TOTAL,
    CHAT_FAILURES_TOTAL
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2
    )

    conversation_id: str |None = None

    top_k:int = Field(
        default=5,
        ge=1,
        le=20 
    )

@router.post("")
def chat(
    request: ChatRequest
):
    CHAT_REQUESTS_TOTAL.inc()
    try:
        conversation_repository = ConversationRepository()
        message_repository = MessageRepository()
        message_source_repository = MessageSourceRepository()

        conversation_id = request.conversation_id
        if not conversation_id:
            conversation = conversation_repository.create(title=request.question[:60])
            conversation_id = conversation["id"]
            if not conversation_id:
                CHAT_FAILURES_TOTAL.inc()
                raise RuntimeError(
                    f"Conversation created did not return an id: {conversation}"
                )
        else:
            conversation = conversation_repository.get(conversation_id)
            if conversation is None:
                CHAT_FAILURES_TOTAL.inc()
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
        
        print ("conversation_id before user message: ", conversation_id)

        history = message_repository.get_recent(
            conversation_id=conversation_id,
            limit=settings.rag_history_message_limit
        )

        print (
            "History before current question: ",
            [
                (item["role"], item["content"][:80]) 
                for item in history
            ]
        )
        
        service = RAGService()
        result = service.ask(
            question=request.question,
            top_k=request.top_k,
            history=history
        )

        # Persist current turn only after RAG succeeds
        message_repository.create(
            conversation_id=conversation_id,
            role="user",
            content=request.question
        )

        assistant_message = message_repository.create(
            conversation_id=conversation_id, 
            role="assistant", 
            content=result["answer"]
        )

        message_source_repository.create_many(
            message_id=assistant_message["id"],
            sources=result["sources"]
        )

        return {
            "conversation_id": conversation_id,
            **result
        }    
    except HTTPException:
        CHAT_FAILURES_TOTAL.inc()
        raise
    except Exception as exc:
        CHAT_FAILURES_TOTAL.inc()
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

