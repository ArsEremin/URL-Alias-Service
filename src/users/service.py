from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.users.utils import verify_password, get_password_hash
from src.models import User


class UserService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_by_id(self, user_id: UUID):
        query = select(User).filter_by(id=user_id)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()

    async def get_user_by_username(self, username: str):
        query = select(User).filter_by(username=username)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()

    async def add_user(self, username, password):
        hashed_password = get_password_hash(password)
        stmt = insert(User).values(username=username, hashed_password=hashed_password)
        await self._session.execute(stmt)
        await self._session.commit()

    async def auth_user(self, login: str, password: str):
        user = await self.get_user_by_username(login)
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user


async def get_user_service(session: Annotated[AsyncSession, Depends(get_async_session)]) -> UserService:
    return UserService(session)
