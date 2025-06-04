from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl


class UrlSchema(BaseModel):
    id: UUID
    long_url: HttpUrl
    token: str
    created_by: UUID
    number_of_clicks: int
    is_active: bool
    created_at: datetime
    expires_at: datetime
