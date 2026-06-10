from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import ParentBase


class Metadata(ParentBase):
    __tablename__ = "Metadata"

    key: Mapped[str] = mapped_column("key", String(255), primary_key=True)
    content: Mapped[dict | None] = mapped_column("content", JSON(), nullable=True)
