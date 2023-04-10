import uuid
from typing import Optional

from sqlmodel import (
    Field, 
    Column, 
    String, 
    Integer, 
    Boolean, 
    ForeignKey,
    Relationship,
    text
)

from .base import BaseModel



class Account(BaseModel, table=True):
    __tablename__ = 'accounts'

    login: str = Field(
        sa_column=Column(
            String(length=100),
            nullable=False,
            index=True,
            default=None,
            unique=True,
            ),
    )
    password: str = Field(
        default=None,
        nullable=False
    )
    login_key: str = Field(
        sa_column=Column(
            String(),
            default=lambda: str(uuid.uuid4),
            index=True,
            nullable=False,
        )
    )
    session: 'Session' = Relationship(back_populates='account')


class Session(BaseModel, table=True):
    __tablename__ = 'sessions'

    name: str = Field(
        sa_column_kwargs=dict(nullable=False)
    )
    value: str = Field(
        sa_column=Column(
            String(),
            nullable=False,
        ),
    )
    domain: str = Field(
        sa_column=Column(
            String(),
            default=lambda: '.facebook.com'
        )
    )
    path: str = Field(
        sa_column=Column(
            String(),
            default='/'
        )
    )
    expiry: int = Field(
        sa_column=Column(
            Integer(),
            default=lambda: 'Session',
        )
    )
    sameSite: str = Field(
        sa_column=Column(
            String(),
        )
    )
    secure: bool = Field(
        sa_column=Column(
            Boolean(),
            default=True,
        )
    )
    httpOnly: bool = Field(
        sa_column=Column(
            Boolean(),
            default=lambda: True,
        )
    )
    account_id: int = Field(sa_column=Column(Integer(), ForeignKey('accounts.id', ondelete='CASCADE')))
    account: 'Account' = Relationship(sa_relationship_kwargs={'cascade': 'all,delete'}, back_populates='session')
    