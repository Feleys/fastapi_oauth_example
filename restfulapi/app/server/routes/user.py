from fastapi import APIRouter, Body, HTTPException, status, Header
from fastapi.encoders import jsonable_encoder
from app.server.database import (
    db_add_user,
    db_delete_user,
    db_retrieve_user,
    db_update_user,
    db_get_token,
    verify_token,
)
from app.server.helper.response import Response
from app.server.models.user import (
    UpdateUserModel,
    CreateUserModel,
)
from app.server.models.user import LoginUserModel

router = APIRouter()


@router.post("/create", response_description="Create user data")
async def add_user_data(user: CreateUserModel = Body(...)):
    user = jsonable_encoder(user)
    return await db_add_user(user)


@router.post("/login", response_description="Get user token")
async def user_token(user: LoginUserModel):
    return await db_get_token(user.username, user.password)


@router.get("/get/{username}", response_description="Get user data")
async def get_user_data(username: str, authorization_: str = Header(...)):
    verify_token(authorization_, scopes=['user:read'])
    return await db_retrieve_user(username)


@router.put("/update/{username}", response_description="Update user data")
async def update_user_data(username: str, req: UpdateUserModel = Body(...), authorization_: str = Header(...)):
    await verify_token(authorization_, scopes=['user:write'])
    await db_retrieve_user(username)

    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await db_update_user(username, req)
    if updated_user:
        return Response(
            "user ID: {} update is successful".format(username),
            200,
            "user updated successfully",
        )
    return Response(
        "An error occurred",
        404,
        "There was an error updating the user data."
    )


@router.delete("/{username}", response_description="user data deleted")
async def delete_user_data(username: str, authorization_: str = Header(...)):
    await verify_token(authorization_, scopes=['user:delete'])
    await db_retrieve_user(username)

    deleted_user = await db_delete_user(username)
    if deleted_user:
        return Response(
            "user with ID: {} removed".format(username), "user deleted successfully"
        )
    return Response(
        "An error occurred",
        404,
        "user with id {0} doesn't exist: ".format(username)
    )
