import uuid
from datetime import UTC, datetime
from enum import Enum

from fastapi import HTTPException, status
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.core.security import verify_token
from src.db.postgres import Base
from src.models.login_history import LoginHistory
from src.models.social_account import SocialAccount  # noqa


class UserRoleEnum(str, Enum):
    SUPERUSER = "superuser"
    ADMIN = "admin"
    USER = "user"

    @classmethod
    def get_is_staff_roles(cls) -> list[str]:
        """
        Возвращает список всех значений ролей, относящиеся к персоналу.
        """
        return UserRoleEnum.SUPERUSER, UserRoleEnum.ADMIN

    @classmethod
    def get_all_roles(cls) -> list[str]:
        """
        Возвращает список всех значений ролей, определённых в перечислении.
        """
        return [role.strip() for role in cls]


class User(Base):
    __table_args__ = (
        UniqueConstraint("id", "partition_country"),
        UniqueConstraint("login", "partition_country"),
        UniqueConstraint("email", "partition_country"),
        UniqueConstraint("oauth_id", "partition_country"),
        {
            "postgresql_partition_by": "LIST (partition_country)",
            "schema": "auth",
        },
    )
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    login = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    role = Column(
        SQLAEnum(UserRoleEnum), nullable=False, default=UserRoleEnum.USER
    )
    is_active = Column(Boolean, default=True, nullable=False)
    login_history = relationship(
        "LoginHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    social_accounts = relationship(
        "SocialAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    country = Column(String(100), nullable=False, default="unknown")
    partition_country = Column(
        String(10), nullable=False, primary_key=True, default="unknown"
    )

    def __init__(
        self,
        login: str,
        password: str = "",
        email: str | None = None,
        oauth_id: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        country: str | None = None,
        partition_country: str | None = None,
        role: UserRoleEnum = UserRoleEnum.USER,
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password) if password else ""
        self.email = email
        self.oauth_id = oauth_id
        self.country = country
        self.partition_country = partition_country
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: UUID) -> "User":
        if user_id:
            result = await db.execute(
                select(cls).where(cls.id == user_id)
            )
            if user := result.scalar_one_or_none():
                return user

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    @classmethod
    async def get_user_by_login(
        cls, db: AsyncSession, login: str
    ) -> "User | None":
        """
        Возвращает пользователя по логину.
        """
        result = await db.execute(select(cls).where(cls.login == login))
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_by_email(
        cls, db: AsyncSession, email: str
    ) -> "User | None":
        """
        Возвращает пользователя по email.
        """
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    @classmethod
    async def get_user_by_token(
        cls, db: AsyncSession, token: str
    ) -> "User | None":
        """
        Извлекает пользователя из JWT access-токена.
        """
        payload = verify_token(token)
        user_id = payload.get("user_id")

        return await cls.get_user_by_id(db, user_id)

    async def add_login_history(
            self, db: AsyncSession, user_agent: str, user_device_type: str
    ) -> None:
        """
        Добавляет запись входа в систему.
        """
        login_entry = LoginHistory(
            user_id=self.id,
            user_agent=user_agent,
            user_device_type=user_device_type,
            partition_country=self.partition_country,
        )
        db.add(login_entry)
        await db.commit()

    async def get_login_history(
            self, db: AsyncSession, page_size: int, page_number: int
    ) -> list[LoginHistory]:
        """
        Возвращает список истории входов пользователя.
        """
        offset = (page_number - 1) * page_size

        stmt = select(LoginHistory).where(
            LoginHistory.user_id == self.id
        ).limit(page_size).offset(offset)
        result = await db.execute(stmt)

        return result.scalars().all()

    def __repr__(self) -> str:
        return f"<User {self.login}>"
