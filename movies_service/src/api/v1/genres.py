import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.dependencies.auth import role_dependency
from src.models.models import GenreBase
from src.schemas.user_role_enum import UserRoleEnum
from src.services.genre_service import GenreService, get_genre_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/search",
    response_model=list[GenreBase],
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def search_genres(
    query: str | None = Query(None, description="Поисковый запрос по жанрам"),
    genre_service: GenreService = Depends(get_genre_service),
) -> list[GenreBase]:
    """Эндпоинт для поиска жанров."""
    genres = await genre_service.search_genres(query=query)

    if not genres:
        # Выбрасываем HTTP-исключение с кодом 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Genres not found",
        )

    return genres


@router.get("", response_model=list[GenreBase])
async def get_genres(
    genre_service: GenreService = Depends(get_genre_service),
) -> list[GenreBase]:
    """Эндпоинт для получения всех жанров."""
    genres = await genre_service.get_genres()

    if not genres:
        # Выбрасываем HTTP-исключение с кодом 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Genres not found",
        )

    return genres


@router.get(
    "/{genre_id}",
    response_model=GenreBase,
    dependencies=[Depends(role_dependency(UserRoleEnum.get_all_roles()))],
)
async def genre_details(
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service),
) -> GenreBase:
    """Эндпоинт для получения конкретного жанра по ID."""
    genre = await genre_service.get_genre_by_id(genre_id)

    if not genre:
        logger.info("Жанра с ID: %s не найден.", genre_id)
        # Выбрасываем HTTP-исключение с кодом 404
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Genre not found",
        )

    return genre[0]
