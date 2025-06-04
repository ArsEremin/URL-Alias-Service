from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status, Body, Request
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl

from src.models import User
from src.url_shortener.exceptions import InvalidSiteException, InvalidUrlTokenException, InactiveUrlException, \
    ExpiredUrlException
from src.url_shortener.utils import check_website_exist, get_short_url
from src.url_shortener.service import UrlService, get_url_service
from src.users.dependencies import get_current_user

router = APIRouter(
    tags=["Urls"]
)


@router.post(
    "/make_shorter",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Site with this url does not exists or status code of request >= 400"
        },
    },
    summary="Эндпоинт создания короткой ссылки"
)
async def make_shorter(
    url: Annotated[HttpUrl, Body(embed=True, example={"url": "https://google.com"})],
    service: Annotated[UrlService, Depends(get_url_service)],
    user: Annotated[User, Depends(get_current_user)]
) -> HttpUrl:
    """
    Логика работы ручки:

    Проверяем, существует и доступен ли переданный адрес: если нет - кидаем ошибку\n
    Проверяем, что у нас еще нет сокращенного варианта урла для этого длинного адреса:
      - если он уже есть, активен и не устарел, то возвращаем его
      - если еще нет или существующий неактивен/устарел:
          1) Подбираем токен, которого еще нет в базе
          2) На основе этого токена и текущих настроек приложения генерируем полноценный короткий урл
          3) Возвращаем сгенерированный урл
    """
    url = str(url)
    valid_site, message = await check_website_exist(url)
    if not valid_site:
        raise InvalidSiteException(message)

    existing_url = await service.get_url_by_long(url)
    if existing_url is not None:
        if existing_url.expires_at > datetime.now(timezone.utc):
            return get_short_url(existing_url.token)
        await service.deactivate_url(existing_url.token)

    url_token = await service.get_url_token()
    await service.add_short_url(url, url_token, user.id)
    return get_short_url(url_token)


@router.get(
    "/{url_token}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "URL `request.url` doesn't exist"},
        status.HTTP_410_GONE: {"description": "URL is inactive or expired"},
    },
    summary="Эндпоинт редиректа на оригинальную ссылку"
)
async def redirect_to_long(
    request: Request,
    url_token: str,
    service: Annotated[UrlService, Depends(get_url_service)]
):
    """
    Логика работы ручки:

    Проверяем, что у нас есть url_token в базе:
      - если он есть, активен и не устарел, то:
          1) совершаем редирект на длинный урл
          2) увеличиваем счетчик переходов на 1
      - если нет, то кидаем ошибку.
    """
    url = await service.get_url_by_token(url_token)
    if url is None:
        raise InvalidUrlTokenException(request.url)
    if not url.is_active:
        raise InactiveUrlException
    if url.expires_at < datetime.now(timezone.utc):
        raise ExpiredUrlException
    await service.update_number_of_clicks(url_token)
    return RedirectResponse(url.long_url)


@router.patch(
    "/{url_token}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
    summary="Эндпоинт деактивации ссылки",
    description="Помечает в БД ссылку как неактивную"
)
async def deactivate_url(
    url_token: str,
    service: Annotated[UrlService, Depends(get_url_service)]
):
    await service.deactivate_url(url_token)
