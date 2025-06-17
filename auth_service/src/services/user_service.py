import logging
from datetime import timedelta
from functools import lru_cache
from typing import Annotated

import user_agents
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from src.core.config import settings
from src.core.exceptions import TokenRevokedException
from src.core.security import (create_access_token, create_refresh_token,
                               verify_token)
from src.db.postgres import get_session
from src.db.redis_client import get_redis_auth
from src.models.social_account import SocialAccount
from src.models.user import LoginHistory, User
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services.auth_service import AuthService
from src.utils.normalize_country import normalize_country

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, db: AsyncSession, redis_client: AuthService):
        self.db = db
        self.redis_client = redis_client

    @staticmethod
    def _get_device_type(user_agent_str: str) -> str:
        ua = user_agents.parse(user_agent_str)
        if ua.is_mobile or ua.is_tablet:
            return "mobile"

        elif ua.is_pc:
            return "web"

        elif "smart" in user_agent_str.lower():
            return "smart"

        else:
            return "unknown"

    @staticmethod
    def _get_normalize_country(value: str) -> tuple[str, str]:
        try:
            norm_country = normalize_country(value)

        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unknown country: {value}"
            )

        else:
            if norm_country == "Russian Federation":
                partition_country = "RUS"

            else:
                partition_country = "Abroad"

            return norm_country, partition_country

    async def _create_tokens_from_user(
        self, user: User, source_service: str = 'undefined'
    ) -> tuple[str, str]:
        """
        Вспомогательный метод для создания access и refresh токенов и
        добавления refresh токена в Redis.
        """
        role = user.role.value

        access_token = create_access_token(user.id, role)
        refresh_token = create_refresh_token(user.id, role)

        if source_service != "admin_service":
            await self.redis_client.set(
                refresh_token,
                settings.token_active,
                expire=int(timedelta(
                    days=settings.refresh_token_expire_days).total_seconds()
                ),
            )

        return access_token, refresh_token

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        lock_sql = text("SELECT pg_advisory_xact_lock(hashtext(:login))")
        await self.db.execute(lock_sql, {"login": user_data.login})

        stmt = select(User.id).where(User.login == user_data.login).limit(1)
        existing = await self.db.scalar(stmt)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login already registered",
            )

        norm_country, partition_country = self._get_normalize_country(
            user_data.country
        )

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            login=user_data.login,
            password=user_data.password,
            email=user_data.email,
            country=norm_country,
            partition_country=partition_country
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    async def login_user(
        self, login: str, password: str, user_agent: str, source_service: str
    ) -> Token:
        user = await User.get_user_by_login(self.db, login)
        if not user or not user.check_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        access_token, refresh_token = await self._create_tokens_from_user(
            user, source_service
        )

        user_device_type = self._get_device_type(user_agent)
        await user.add_login_history(self.db, user_agent, user_device_type)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def login_user_oauth(self, user: User) -> Token:
        """
        Авторизация OAuth-пользователя — создание токенов и запись истории
        входа.
        """
        access_token, refresh_token = await self._create_tokens_from_user(user)
        await user.add_login_history(
            self.db,
            user_agent="oauth",
            user_device_type="web",
        )
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> Token:
        user = await User.get_user_by_token(self.db, refresh_token)

        if not await self.redis_client.check_value(
            refresh_token, settings.token_active
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh-token has revoked"
            )

        access_token, new_refresh_token = await self._create_tokens_from_user(
            user
        )

        await self.redis_client.delete(refresh_token)

        return Token(
            access_token=access_token, refresh_token=new_refresh_token
        )

    async def update_user(self, token: str, user_update: UserUpdate) -> User:
        user = await User.get_user_by_token(self.db, token)

        if await self.redis_client.check_value(
            token, settings.token_revoke
        ):
            raise TokenRevokedException()

        if first_name := user_update.first_name:
            user.first_name = first_name

        if last_name := user_update.last_name:
            user.last_name = last_name

        if password := user_update.password:
            user.password = generate_password_hash(password)

        if country := user_update.country:
            user.country, user.partition_country = self._get_normalize_country(
                country
            )

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def logout_user(self, access_token: str, refresh_token: str) -> None:
        if await self.redis_client.check_value(
            access_token, settings.token_revoke
        ):
            raise TokenRevokedException()

        access_payload = verify_token(access_token)
        del access_payload["exp"]
        refresh_payload = verify_token(refresh_token)
        del refresh_payload["exp"]

        if access_payload == refresh_payload:
            if self.redis_client.check_value(
                refresh_token, settings.token_active
            ):
                await self.redis_client.revoke_token(access_token)
                await self.redis_client.delete(refresh_token)
                return None

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh-token has revoked"
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect refresh-token"
        )

    async def get_login_history(
        self, token: str, page_size: int, page_number: int
    ) -> list[LoginHistory]:
        user = await User.get_user_by_token(self.db, token)

        if await self.redis_client.check_value(
            token, settings.token_revoke
        ):
            raise TokenRevokedException()

        return await user.get_login_history(
            db=self.db, page_size=page_size, page_number=page_number
        )

    async def get_or_create_oauth_user(
        self,
        provider: str,
        oauth_id: str,
        username: str,
        email: str | None = None,
    ) -> User:
        """
        1. Проверяем, нет ли уже SocialAccount с таким provider+oauth_id.
        2. Если пришёл email — ищем пользователя по email.
        3. Создаём при необходимости и пользователя, и SocialAccount.
        """
        stmt = select(SocialAccount).where(
            SocialAccount.provider == provider,
            SocialAccount.oauth_id == oauth_id,
        )
        if social := (await self.db.scalars(stmt)).first():
            return social.user

        user: User | None = None
        if email:
            user = await User.get_user_by_email(self.db, email)

        if not user:
            user = User(
                login=username or f"user_{provider}_{oauth_id[:8]}",
                email=email,
                password=None,          # пароля нет — OAuth
            )
            self.db.add(user)
            await self.db.flush()       # получаем user.id

        social = SocialAccount(
            provider=provider,
            oauth_id=oauth_id,
            email=email,
            username=username,
            user_id=user.id,
        )
        self.db.add(social)
        await self.db.commit()
        await self.db.refresh(user)
        return user


@lru_cache()
def get_user_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[AuthService, Depends(get_redis_auth)],
) -> UserService:
    """
    Провайдер для получения экземпляра UserService.

    Функция создаёт синглтон экземпляр UserService, используя
    Postgres и Redis, которые передаётся через Depends (зависимости FastAPI).

    :param db: Сессия Postgres, предоставленный через Depends.
    :param redis: Экземпляр клиента Redis, предоставленный через Depends.
    :return: Экземпляр UserService, который используется для
    работы с пользователями.
    """
    logger.info(
        "Создаётся экземпляр UserService с использованием "
        "Postgres и Redis."
    )
    return UserService(db, redis)
