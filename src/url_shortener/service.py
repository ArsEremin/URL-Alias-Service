from typing import Annotated
from random import choice
from string import ascii_uppercase, digits
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from src.database import get_async_session
from src.models import Url


class UrlService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_url_by_token(self, url_token: str):
        query = select(Url).filter_by(token=url_token)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()

    async def get_url_by_long(self, long_url: str):
        query = select(Url).filter_by(long_url=long_url)
        return await self._session.scalar(query)

    async def get_url_tokens(self, active_only: bool, offset: int, limit: int):
        query = select(Url.token).offset(offset).limit(limit)
        if active_only:
            query = query.filter_by(is_active=True)
        return await self._session.scalars(query)

    async def get_sorted_urls(self):
        query = select(Url).order_by(Url.number_of_clicks.desc())
        res = await self._session.execute(query)
        return res.scalars().all()

    async def get_url_token(self) -> str:
        while True:
            url_token = "".join(choice(ascii_uppercase + digits) for _ in range(5))
            existing_url = await self.get_url_by_token(url_token)
            if existing_url is None:
                break
        return url_token

    async def add_short_url(self, long_url: str, url_token: str, creator_id: UUID):
        new_url = Url(long_url=long_url, token=url_token, created_by=creator_id)
        self._session.add(new_url)
        await self._session.commit()

    async def update_number_of_clicks(self, url_token: str):
        url = await self.get_url_by_token(url_token)
        url.number_of_clicks += 1
        await self._session.commit()

    async def deactivate_url(self, url_token: str):
        url = await self.get_url_by_token(url_token)
        url.is_active = False
        await self._session.commit()


async def get_url_service(session: Annotated[AsyncSession, Depends(get_async_session)]) -> UrlService:
    return UrlService(session)
