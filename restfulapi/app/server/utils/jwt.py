from app.settings import JWT_ALGO, JWT_SK

from jose import jwt
from typing import Union


def jwt_encode_token(token_dict: dict) -> str:
    return jwt.encode(token_dict, JWT_SK, algorithm=JWT_ALGO)


def jwt_decode_token(token_value: str) -> Union[dict, None]:
    return jwt.decode(token_value, JWT_SK, algorithms=[JWT_ALGO])

