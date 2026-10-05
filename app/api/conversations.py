from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.message_source_repository import MessageSourceRepository

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)

conversation_repository = ConversationRepository()
message_repository = MessageRepository()
message_source_repository = MessageSourceRepository()

class CreateConversationRequest(BaseModel):
    title: str | None = None

@router.post("")
def create_conversation(
    request: CreateConversationRequest
):
    return conversation_repository.create(title=request.title)

@router.get("")
def list_conversations():
    return conversation_repository.list_all()

@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    conversation = (conversation_repository.get(conversation_id))

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = (message_repository.list_by_conversation(conversation_id))

    for message in messages:
        message["sources"] = (
            message_source_repository.list_by_message(message["id"])
        )
        

    return {
        "conversation": conversation,
        "messages": messages
    }