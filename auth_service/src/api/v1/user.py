from functools import lru_cache

from fastapi import (APIRouter, Depends, HTTPException, Path, Query, Request,
                     status)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.db.redis_client import get_redis_auth
from src.dependencies.auth import oauth2_scheme
from src.models.social_account import SocialProviderEnum
from src.schemas.login_history import LoginHistory
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserResponse, UserUpdate
from src.services.auth_service import AuthService
from src.services.oauth_service import YandexOAuthService
from src.services.user_service import UserService, get_user_service

router = APIRouter()

OAUTH_PROVIDERS: dict[str, type[YandexOAuthService]] = {
    SocialProviderEnum.YANDEX: YandexOAuthService,
}


@lru_cache()
def get_oauth_service() -> YandexOAuthService:
    """
    Провайдер для YandexOAuthService.
    """
    return YandexOAuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя с логином, паролем и профилем. "
                "Возвращает объект пользователя."
)
async def register_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Регистрирует нового пользователя.
    """
    return await user_service.create_user(user_create)


@router.post(
    "/login",
    response_model=Token,
    summary="Аутентификация пользователя",
    description="Проверяет логин и пароль. Возвращает access и refresh токены."
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """
    Аутентифицирует пользователя и возвращает JWT токены.
    """
    user_agent = request.headers.get("user-agent", "unknown")
    source_service = request.headers.get("X-Source-Service", "undefined")
    return await user_service.login_user(
        form_data.username, form_data.password, user_agent, source_service
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление access-токена",
    description="Обновляет access-токен при валидном refresh-токене. "
                "Возвращает новые токены."
)
async def refresh_token(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """
    Обновляет access и refresh токены, если refresh валиден.
    """
    return await user_service.refresh_tokens(refresh_token)


@router.patch(
    "/update",
    response_model=UserResponse,
    summary="Обновление данных пользователя",
    description="Позволяет пользователю изменить логин и/или пароль без "
                "подтверждения email."
)
async def update_user(
    user_update: UserUpdate,
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await user_service.update_user(token, user_update)


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет refresh токен и отзывает access токен."
)
async def logout(
    refresh_token: str,
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> dict[str, str]:
    """
    Удаляет refresh и отзывает access токен.
    """
    await user_service.logout_user(token, refresh_token)
    return {"message": "Successfully logged out"}


@router.get(
    "/history",
    response_model=list[LoginHistory],
    summary="История входов пользователя",
    description="Возвращает список логинов пользователя по токену."
)
async def login_history(
    token: str = Depends(oauth2_scheme),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Кол-во записей",
    ),
    page_number: int = Query(
        default=1,
        ge=1,
        description="Пагинация",
    ),
    user_service: UserService = Depends(get_user_service),
) -> list[LoginHistory]:
    """
    Возвращает историю входов пользователя.
    """
    return await user_service.get_login_history(
        token=token, page_size=page_size, page_number=page_number
    )


@router.get(
    "/social/login/{provider}",
    summary="Перенаправляет на страницу авторизации провайдера",
)
async def social_login(provider: SocialProviderEnum = Path(...)):
    service_cls = OAUTH_PROVIDERS.get(provider)
    if not service_cls:
        raise HTTPException(status_code=404, detail="Unsupported provider")
    return RedirectResponse(service_cls().build_auth_url())


@router.get(
    "/social/callback/{provider}",
    response_model=Token,
    summary="Колбэк от OAuth-провайдера",
)
async def social_callback(
    provider: SocialProviderEnum,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_redis_auth),
) -> Token:
    service_cls = OAUTH_PROVIDERS.get(provider)
    if not service_cls:
        raise HTTPException(status_code=404, detail="Unsupported provider")

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Missing code")

    cache_key = f"{provider}_code:{code}"
    if cached := await auth_service.redis_client.get(cache_key):
        return Token.parse_raw(cached)

    service = service_cls()
    token_value = await service.get_access_token(code)
    user_info = await service.get_user_info(token_value)

    if provider is SocialProviderEnum.YANDEX:
        email = user_info.get("default_email")
        oauth_id = user_info["id"]
        username = user_info.get("login") or f"user_{oauth_id}"
    else:
        email = user_info.get("email")
        oauth_id = user_info["id"]
        username = user_info.get("username") or f"user_{oauth_id}"

    user = await user_service.get_or_create_oauth_user(
        provider=provider,
        oauth_id=oauth_id,
        username=username,
        email=email,
    )
    result = await user_service.login_user_oauth(user)

    await auth_service.redis_client.set(cache_key, result.json(), ex=600)
    return result
