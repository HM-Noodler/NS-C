from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())


class UUIDMixin(SQLModel):
    """Mixin for UUID primary key."""

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False,
    )
