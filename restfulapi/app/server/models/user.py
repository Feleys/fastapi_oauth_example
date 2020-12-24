from typing import Optional, Union
from pydantic import BaseModel, Field

from app.settings import TOKEN_TYPE


class UserSchema(BaseModel):
    username: str = Field(..., unique=True)
    hashed_password: str = Field(...)
    email: str = Field(...)
    scopes: list = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "test",
                "hashed_password": "secret",
                "email": "test@email.com",
                "scopes": ["user:read"]
            }
        }


class CreateUserModel(BaseModel):
    username: str = Field(..., unique=True)
    password: str = Field(...)
    email: str = Field(...)
    scopes: list = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "test",
                "password": "secret",
                "email": "test@email.com",
                "scopes": ["user:read"]
            }
        }


class UpdateUserModel(BaseModel):
    username: Optional[str]
    hashed_password: Optional[str]
    email: Optional[str]
    scopes: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                "username": "test",
                "hashed_password": "secret",
                "email": "test@email.com",
                "scopes": ["user:read"]
            }
        }


class UserBaseModel(BaseModel):
    id: Optional[str]


class LoginUserModel(BaseModel):
    username: Optional[str]
    password: Optional[str]


class TokenModel(BaseModel):
    access_token: str = Field(...)
    token_type: str = Field(TOKEN_TYPE)