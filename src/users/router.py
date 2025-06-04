from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from src.users.exceptions import UserExistsException, InvalidAuthDataException
from src.users.utils import create_access_token
from src.users.service import UserService, get_user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Эндпоинт регистрации")
async def register_user(
    service: Annotated[UserService, Depends(get_user_service)],
    username: Annotated[str, Query(min_length=3, max_length=50)],
    password: Annotated[str, Query(min_length=3, max_length=64)]
):
    """
    Логика работы ручки:

    Проверяем, есть ли в БД пользователь с таким же username:
      - если есть, то кидаем ошибку
      - если нет, то добавляем нового пользователя в БД
    """
    existing_user = await service.get_user_by_username(username)
    if existing_user is not None:
        raise UserExistsException
    await service.add_user(username, password)
    return {"status": "registration successful"}


@router.post("/login", status_code=status.HTTP_200_OK, summary="Эндпоинт аутентификации")
async def login_user(
    response: Response,
    service: Annotated[UserService, Depends(get_user_service)],
    login: str,
    password: str
):
    """
    Логика работы ручки:

    Проверяем, есть ли в БД пользователь с таким логином и паролем:
      - если есть, то генерируем JWT-токен и добавляем его в cookie
      - если нет, то кидаем ошибку
    """
    user = await service.auth_user(login, password)
    if user is None:
        raise InvalidAuthDataException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("shortener_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout", summary="Эндпоинт логаута", description="Удаляет JWT-токен из cookie")
async def logout_user(response: Response):
    response.delete_cookie("shortener_access_token")
    return {"status": "logout successful"}
