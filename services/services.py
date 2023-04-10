from fastapi import HTTPException, status

from api import Facebook
from utils.errors import LoginIsRequiredError
from schemas import Response
from settings import settings
from db.connection import DatabaseConnection


async def remove_accounts(key: str, app_id: str | int, accounts: list[int]):
    f = Facebook(key=key, headless=settings.browser_headless)
    if not f.cookies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Looks like key is deprecated or invalid. Login is required',
        )
    try:
        is_deleted = f.delete_accounts_id(accs=accounts, app_id=app_id)
    except LoginIsRequiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Login is required or apps doesnt exists on account',
        )
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to delete accounts. Try again.',
        )
    return {'status': status.HTTP_200_OK, 'message': 'Accounts was deleted successfully'}

async def add_accounts(key: str, app_id: int | str, accounts: list[int | str]) -> dict:
    f = Facebook(key=key, headless=settings.browser_headless)
    if not f.cookies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Looks like key is deprecated or invalid. Login is required',
        )
    try:
        is_added = f.add_accounts_id(accs=accounts, app_id=app_id)
    except LoginIsRequiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Login is required or apps doesnt exists on account',
        )
    if not is_added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to add accounts. Try again.',
        )
    return {'status': status.HTTP_200_OK, 'message': 'Accounts was added successfully'}

async def get_app_accounts(key: str, app_id: int | str) -> Response:
    f = Facebook(key=key, headless=settings.browser_headless)
    if not f.cookies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Looks like key is deprecated or invalid. Login is required',
        )
    try:
        apps_ids = f.get_app_accounts(app_id=app_id)
    except LoginIsRequiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Login is required or apps doesnt exists on account',
        )
    if not apps_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Looks like account have no apps_id'
        )
    return Response(
        status=status.HTTP_200_OK,
        accs=apps_ids,
        message='Successfully'
    )

async def base_auth(login: str, password: str) -> dict:
    f = Facebook(key=None, headless=settings.browser_headless)
    key = f.sign_up(login=login, password=password)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed on auth. Try again.'
        )
    return {'status': status.HTTP_200_OK, 'key': key, 'message': 'Successfully authenticated.'}

async def auth_with_email(login: str, password: str, email: str) -> dict:
    f = Facebook(key=None, headless=settings.browser_headless)
    data = f.sign_up(login=login, password=password, email=email)
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed on auth. Try again.'
        )
    try:
        return {'status': status.HTTP_400_BAD_REQUEST, 'message': 'Need to set a code from email to confirm', 'hash_key': data['second_step_key']}
    finally:
        data['second_step']()

async def auth_with_2fa(login: str, password: str, code: str) -> dict:
    f = Facebook(key=None, headless=settings.browser_headless)
    data = f.sign_up(login=login, password=password, email=code)
    if not isinstance(data, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed on auth. Try again.'
        )

    return {'status': status.HTTP_200_OK, 'key': data}

async def check_login_status(login: str) -> dict:
    db = DatabaseConnection()
    check = db.check_session_exists(login=login)
    return {'status': status.HTTP_200_OK, 'is_login': check}

async def get_apps(key: str) -> Response:
    f = Facebook(key=key, headless=settings.browser_headless)
    if not f.cookies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Looks like key is deprecated or invalid. Login is required',
        )
    
    try:
        ids = f.get_apps_id()
    except LoginIsRequiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Login is required or apps doesnt exists on account',
        )
    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Apps doesnt exists on account',
        )
    return Response(
        status=status.HTTP_200_OK,
        accs=ids,
        message='Successfully',
    )
