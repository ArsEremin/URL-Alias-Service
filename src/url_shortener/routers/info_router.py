from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import HttpUrl

from src.models import User
from src.schemas import UrlSchema

from src.url_shortener.utils import get_short_url
from src.url_shortener.service import UrlService, get_url_service
from src.users.dependencies import get_current_user


router = APIRouter(
    tags=["Urls"],
    prefix="/info"
)


@router.get(
    "/urls",
    response_model=list[HttpUrl],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    summary="Эндпоинт выборки списка созданных ссылок",
    description="Возвращает список созданных сервисом ссылок с пагинацией"
)
async def get_urls_list(
    service: Annotated[UrlService, Depends(get_url_service)],
    skip: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    active_only: bool | None = False
):
    tokens = await service.get_url_tokens(active_only, skip, limit)
    return [get_short_url(token) for token in tokens]


@router.get(
    "/stats",
    response_model=list[UrlSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
    summary="Эндпоинт выборки статистики по переходам",
    description="Возвращает статистику по всем ссылкам с сортировкой по количеству переходов"
)
async def get_stats(service: Annotated[UrlService, Depends(get_url_service)]):
    sorted_urls = await service.get_sorted_urls()
    return sorted_urls


@router.get(
    "/my_stats",
    response_model=list[UrlSchema],
    status_code=status.HTTP_200_OK,
    summary="Эндпоинт выборки статистики по переходам для текущего пользователя",
    description="Возвращает статистику по ссылкам, созданным именно текущим пользователем"
)
async def get_my_stats(
    user: Annotated[User, Depends(get_current_user)]
):
    user_urls = user.created_urls
    return sorted(user_urls, key=lambda url: url.number_of_clicks, reverse=True)
