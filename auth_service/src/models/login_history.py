import uuid
from datetime import UTC, datetime

from sqlalchemy import (Column, DateTime, ForeignKeyConstraint, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base


class LoginHistory(Base):
    __table_args__ = (
        UniqueConstraint("id", "user_device_type"),
        ForeignKeyConstraint(
            ["user_id", "partition_country"],
            ["auth.users.id", "auth.users.partition_country"],
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        {
            "postgresql_partition_by": "LIST (user_device_type)",
            "schema": "auth"
        },
    )
    __tablename__ = "login_history"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), nullable=False)
    login_time = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    user_agent = Column(String(512), nullable=False, default="unknown")
    user_device_type = Column(
        String(20), nullable=False, primary_key=True, default="unknown"
    )
    partition_country = Column(String(10), nullable=False, default="unknown")

    user = relationship("User", back_populates="login_history")

    def __repr__(self) -> str:
        return (
            f"<LoginHistory user_id={self.user_id} "
            f"login_time={self.login_time}>"
        )
