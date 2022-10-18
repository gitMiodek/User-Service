from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class UserNotification(BaseModel):
    operation: str
    user: dict


class BaseUser(SQLModel):
    nickname: str = Field(index=True)
    email: str = Field(index=True)
    countryCode: str
    dateOfBirth: str
    firstName: str
    lastName: str
    gender: str


class UserTable(BaseUser, table=True):
    __tablename__ = 'api_db'

    id: Optional[int] = Field(primary_key=True, default=None)


class UserRead(BaseUser):
    id: int


class UserCreate(BaseUser):
    pass
