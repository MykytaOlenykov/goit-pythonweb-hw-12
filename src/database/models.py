from datetime import date
from typing import List
from enum import Enum

from sqlalchemy import Integer, String, Date, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserStatus(str, Enum):
    REGISTERED = "registered"
    VERIFIED = "verified"
    DELETED = "deleted"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus),
        default=UserStatus.REGISTERED,
        nullable=False,
    )

    tokens: Mapped[List["Token"]] = relationship(back_populates="user")
    contacts: Mapped[List["Contact"]] = relationship(back_populates="user")


class TokenType(str, Enum):
    REFRESH = "refresh"
    ACTIVATION = "activation"


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[TokenType] = mapped_column(SQLEnum(TokenType), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="tokens")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(255), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="contacts")
