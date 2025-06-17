import uuid
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import (Column, DateTime, ForeignKeyConstraint, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base


class SocialProviderEnum(str, Enum):
    YANDEX = "yandex"
    GOOGLE = "google"
    VK = "vk"
    # дополняйте при подключении новых провайдеров


class SocialAccount(Base):
    __tablename__ = "social_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "oauth_id", name="uq_provider_oauth_id"),
        ForeignKeyConstraint(
            ["user_id", "partition_country"],
            ["auth.users.id", "auth.users.partition_country"],
            ondelete="CASCADE"
        ),
        {"schema": "auth"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, nullable=False)
    provider = Column(String(50), nullable=False)
    oauth_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    linked_at = Column(DateTime(timezone=True),
                       default=lambda: datetime.now(UTC), nullable=False)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    partition_country = Column(String(10), nullable=False, default="unknown")

    user = relationship("User", back_populates="social_accounts")
