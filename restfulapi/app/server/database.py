import motor.motor_asyncio
import time

from fastapi import HTTPException, status

from app.settings import TOKEN_EXPIRE_SECONDS
from app.server.utils.jwt import jwt_encode_token, jwt_decode_token
from app.server.utils.pwd import verify_pwd, hash_pwd
from app.server.helper.response import Response

MONGO_DETAILS = "mongodb://mongo:27017/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.users
user_collection = database.get_collection("users_collection")


def verify_token(token: str, scopes: list = None):
    try:
        token_dict = jwt_decode_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args)

    if not user_collection.find_one({"username": token_dict.get("sub")}):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token not valid")

    print({"scopes_demand": scopes, "scopes_owned": token_dict["scopes"]})
    for scope in scopes or []:
        if scope not in token_dict["scopes"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privilege")


async def get_id_from_token(token):
    return jwt_decode_token(token)["sub"]


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "hashed_password": user["hashed_password"],
        "email": user["email"],
        "scopes": user["scopes"],
    }


# Retrieve all users present in the database
async def db_retrieve_users():
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users


# Add a new user into to the database
async def db_add_user(user_data: dict) -> Response:
    if not "username" in user_data or not "password" in user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing fields")

    if await user_collection.find_one({"username": user_data["username"]}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User existed")

    hashed_password = hash_pwd(user_data["password"])
    user_data.pop("password")
    user_data["hashed_password"] = hashed_password
    user_data["scopes"] = user_data.get("scopes") or []
    user_collection.insert_one(user_data)
    return await db_retrieve_user(user_data['username'])


# Retrieve a user with a matching username
async def db_retrieve_user(username: str) -> dict:
    user = await user_collection.find_one({"username": username}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not exist")
    return Response(user, 200, "Get user data successfully")


# Update a user with a matching username
async def db_update_user(username: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    user = await user_collection.find_one({"username": username})
    if user:
        updated_user = await user_collection.update_one(
            {"username": username}, {"$set": data}
        )
        if updated_user:
            return True
        return False


# Delete a user from the database
async def db_delete_user(username: str):
    user = await user_collection.find_one({"username": username})
    if user:
        await user_collection.delete_one({"username": username})
        return True
    return False


# get token
async def db_get_token(username, password) -> Response:
    user = await user_collection.find_one({"username": username})
    if user and verify_pwd(password, user['hashed_password']):
        token = jwt_encode_token({
            "sub": username,
            "scopes": user.get("scopes", []),
            "exp": time.time() + TOKEN_EXPIRE_SECONDS
        })
        return Response({"access_token": token, "token_type": "Bearer"}, 200, "get token success")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")