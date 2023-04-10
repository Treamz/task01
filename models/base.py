from sqlmodel import SQLModel, Field, func
from sqlalchemy import Column, DateTime
from typing import Optional



class BaseModel(SQLModel):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: Optional[int] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
        )
    )
    updated_at: Optional[int] = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=func.now(),
            server_default=func.now()
        )
    )