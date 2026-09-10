from sqlalchemy.orm import Session

from app.models import Conversation, ConversationMessage


def get_or_create_conversation(
    db: Session,
    session_id: str,
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .first()
    )

    if conversation:
        return conversation

    conversation = Conversation(
        session_id=session_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_history(
    db: Session,
    conversation_id,
):
    messages = (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.conversation_id
            == conversation_id
        )
        .order_by(
            ConversationMessage.created_at.asc()
        )
        .all()
    )

    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]


def save_message(
    db: Session,
    conversation_id,
    role: str,
    content: str,
):
    message = ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message