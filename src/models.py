from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


timestamp = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True))]


class User(Base):
    __tablename__ = "user"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    created_at: Mapped[timestamp] = mapped_column(server_default=func.now())

    created_urls: Mapped[list["Url"]] = relationship(back_populates="creator", lazy="selectin")


class Url(Base):
    __tablename__ = "url"

    id = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    long_url: Mapped[str]
    token: Mapped[str] = mapped_column(unique=True)
    created_by = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    number_of_clicks: Mapped[int] = mapped_column(server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    created_at: Mapped[timestamp] = mapped_column(server_default=func.now())
    expires_at: Mapped[timestamp] = mapped_column(server_default=text("now() + INTERVAL '1 day'"))

    creator: Mapped[User] = relationship(back_populates="created_urls", lazy="selectin")
