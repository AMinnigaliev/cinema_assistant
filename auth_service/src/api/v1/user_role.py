from uuid import UUID

from fastapi import APIRouter, Depends

from src.dependencies.auth import role_dependency
from src.models.user import User, UserRoleEnum
from src.schemas.user import UserResponse
from src.services.user_role_service import (UserRoleService,
                                            get_user_role_service)

router = APIRouter(
    dependencies=[Depends(role_dependency(UserRoleEnum.get_is_staff_roles()))]
)


@router.post(
    "/{user_id}/assign-role/{role}",
    response_model=UserResponse,
    summary="Назначение роли пользователю",
    description="Эндпоинт для назначения пользователю новой роли. Возвращает "
                "обновлённого пользователя.",
)
async def assign_role(
    user_id: UUID,
    role: UserRoleEnum,
    user_role_service: UserRoleService = Depends(
        get_user_role_service
    ),
) -> User:
    """Эндпоинт для назначения пользователю роли."""
    return await user_role_service.assign_role(user_id, role)


@router.get(
    "/{user_id}/role",
    summary="Получение роли пользователя",
    description="Эндпоинт для получения роли конкретного пользователя.",
)
async def get_user_role(
    user_id: UUID,
    user_role_service: UserRoleService = Depends(
        get_user_role_service
    ),
) -> str:
    """Эндпоинт для получения роли пользователя."""
    return await user_role_service.get_user_role(user_id)
