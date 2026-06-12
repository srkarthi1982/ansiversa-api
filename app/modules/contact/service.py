from sqlalchemy.orm import Session

from app.modules.contact.models import ContactMessage
from app.modules.contact.schemas import ContactMessageCreateRequest


def create_contact_message(
    db: Session,
    payload: ContactMessageCreateRequest,
) -> ContactMessage:
    contact_message = ContactMessage(
        name=payload.name,
        email=payload.email,
        subject=payload.subject,
        message=payload.message,
    )
    db.add(contact_message)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(contact_message)

    return contact_message
