import schemas
from db.redis_db import redis
from utils.errors import EmailIsRequiredError, AuthFailedError, TwoFactorCodeIsRequiredError
from services import (
    get_apps, 
    add_accounts,
    remove_accounts,
    get_app_accounts,
    base_auth,
    check_login_status,
    auth_with_email,
    auth_with_2fa,
    
)

from typing import Union

from fastapi.routing import APIRouter
from fastapi import status, HTTPException




root = APIRouter()


@root.get("/apps", status_code=status.HTTP_200_OK, tags=['GET'])
async def get_apps_endpoint(key: str) -> schemas.Response:
    return await get_apps(key=key)
    
@root.get("/{app_id}", status_code=status.HTTP_200_OK, tags=['GET'])
async def get_app_accounts_endpoint(key: str, app_id: str) -> schemas.Response:
    return await get_app_accounts(key=key, app_id=app_id)

@root.post("/check_login_status", status_code=status.HTTP_200_OK, tags=['POST'])
async def check_login_status_endpoint(data: schemas.AuthDataLogin) -> dict:
    if not data.login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Request data is required'
        )
    return await check_login_status(login=data.login)
    
@root.post("/add/{app_id}", status_code=status.HTTP_200_OK, tags=['POST'])
async def add_accs_endpoint(key: str, app_id: int | str, data: schemas.RequestData) -> dict:
    if not data.accs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Request data is required'
        )
    for value in data.accs:
        if not isinstance(value, (str, int)) or not str(value).isnumeric():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed. Wrong data.'
            )
    return await add_accounts(key, app_id, data.accs)

@root.post("/remove/{app_id}", status_code=status.HTTP_200_OK, tags=['POST'])
async def delete_accs_endpoint(key: str, app_id: int | str, data: schemas.RequestData) -> dict:
    if not data.accs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Request data is required'
        )
    for value in data.accs:
        if not isinstance(value, (str, int)) or not str(value).isnumeric():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed. Wrong data.'
            )
    return await remove_accounts(key=key, app_id=app_id, accounts=data.accs)

@root.post('/auth', status_code=status.HTTP_200_OK, tags=['POST'])
async def auth_endpoint(data: schemas.AuthData) -> dict:
    if not data.login or not data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Login or password is required'
        )
    if not data.code and not data.email:
        try:
            return await base_auth(login=data.login, password=data.password)
        except EmailIsRequiredError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email data is required. Try again'
            )
        except TwoFactorCodeIsRequiredError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Need to set a 2fa code to confirm. Try again',
            )
        except AuthFailedError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed on auth, try again.',
            )
    elif data.email and not data.code:
        try:
            return await auth_with_email(login=data.login, password=data.password, email=data.email)
        except AuthFailedError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='failed to auth'
            )
    elif data.code and not data.email:
        try:
            return await auth_with_2fa(login=data.login, password=data.password, code=data.code)
        except AuthFailedError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='failed to auth'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='request data missmatch'
        )
    
@root.post('/confirm_auth/{key}', status_code=status.HTTP_200_OK, tags=['POST'])
def confirm_auth_endpoint(code: str | int, key: str) -> dict:
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='params missmatch. code is required',
        )
    if redis.get_single(key=key) is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session key missmatch',
        )
    redis.set_single(key=key, value=code)
    return {'status': status.HTTP_200_OK, 'message': 'successfully add the code'}

@root.get('/confirm_auth/{key}', status_code=status.HTTP_200_OK, tags=['GET'])
def get_session_code_endpoint(key: str) -> dict:
    if redis.get_single(key=key) is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session key missmatch',
        )
    return {key: redis.get_single(key=key)}

