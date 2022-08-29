import json

import jwt
import time
import uuid
from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Security, Request, Response, Form
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import HTMLResponse
from fastapi.security import SecurityScopes, OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.templating import Jinja2Templates
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from website.core import crud, schemas
from website.core.config import JWT_SECRET, JWT_ALG, JWT_EXPIRE_SECONDS
from website.core.database import get_session

auth = APIRouter()


class OAuth2PasswordBearerCustom(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # authorization: str = request.cookies.get("access_token")  # cookie version
        authorization: str = request.headers.get("Authorization")  # header version
        scheme, param = get_authorization_scheme_param(authorization)
        return param


oauth2_scheme = OAuth2PasswordBearerCustom(
    tokenUrl='/api/auth/login-user',
    scopes={'me': 'Read information about the current user.', 'admin': 'Access database, modify records, etc.'}
)


async def get_user_from_token(
        db: AsyncSession = Depends(get_session),
        token: str = Depends(oauth2_scheme)
) -> Optional[schemas.User]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get('sub')
        user = await crud.get_user(db, email=email)
        return user
    except:
        # database errors, jwt errors, no token errors
        return None


async def get_scopes_from_token(
        token: str = Depends(oauth2_scheme)
) -> Optional[list[str]]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        token_scopes = payload.get('scopes', [])
        return token_scopes
    except:
        return None


async def get_current_user_required(
        security_scopes: SecurityScopes,
        user: Optional[schemas.User] = Depends(get_user_from_token),
        scopes: Optional[list[str]] = Depends(get_scopes_from_token)
) -> schemas.User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if security_scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'
    for scope in security_scopes.scopes:
        if scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have permission to access this page",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_user_optional(
        user: Optional[schemas.User] = Depends(get_user_from_token)
) -> Optional[schemas.User]:
    return user


async def check_change_password(
        db: AsyncSession,
        user: schemas.UserUpdatePassword
):
    errors = {}
    temp_user = await crud.get_user(db, email=user.email)
    if not bcrypt.verify(user.old_password, temp_user.password):
        errors['old_password'] = "Incorrect password"
    if user.old_password == user.new_password:
        errors['all'] = "New password cannot be the same as old password"
    if len(user.new_password) < 7:
        errors['new_password'] = "Password must be at least 8 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    user.new_password = bcrypt.hash(user.new_password)
    await crud.update_user_password(db, user)
    return {"status": "success", "detail": "Changed password!"}


@auth.post('/api/auth/change-password')
async def change_password(
        old_password: str = Form(),
        new_password: str = Form(),
        current_user: schemas.User = Security(get_current_user_required, scopes=['me']),
        db: AsyncSession = Depends(get_session)
):
    updated_user = schemas.UserUpdatePassword(email=current_user.email, first_name=current_user.first_name, last_name=current_user.last_name,
                                              old_password=old_password, new_password=new_password)
    return await check_change_password(db, updated_user)


async def check_login_user(
        db: AsyncSession,
        email: str,
        password: str
):
    errors = {}
    user = await crud.get_user(db, email=email)
    if user is None:
        errors['email'] = "User does not exist"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )
    if not bcrypt.verify(password, user.password):
        errors['password'] = "Incorrect password"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    return {"status": "success", "detail": "Logged in!"}


@auth.post('/api/auth/login-user')
async def login_user(
        response: Response,
        # email: str = Form(),
        # password: str = Form(), for cookies
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_session)
):
    email = form_data.username
    password = form_data.password
    await check_login_user(db, email, password)
    user = await crud.get_user(db, email=email)
    scopes = []
    for scope in user.permissions:
        scopes.append(scope.permission_name)

    token_info = schemas.Token(
        iss="dmecc",
        sub=email,
        iat=int(time.time()),
        exp=int(time.time() + JWT_EXPIRE_SECONDS),
        jti=str(uuid.uuid4()),
        scopes=scopes
    )
    access_token = jwt.encode(token_info.dict(), JWT_SECRET)
    # response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="Strict")
    return {'access_token': access_token, 'token_type': 'bearer'}


async def check_signup_user(
        db: AsyncSession,
        user: schemas.UserCreate
):
    errors = {}
    temp_user = await crud.get_user(db, email=user.email)
    if temp_user is not None:
        errors['all'] = "User already exists"
    if len(user.email) < 2:
        errors['email'] = "Email must be at least 3 characters"
    if len(user.first_name) < 1:
        errors['first_name'] = "First name must be at least 2 characters"
    if len(user.last_name) < 1:
        errors['last_name'] = "Last name must be at least 2 characters"
    if len(user.password) < 7:
        errors['password'] = "Password must be at least 8 characters"
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{json.dumps(errors)}"
        )

    user.password = bcrypt.hash(user.password)
    await crud.create_user(db, user)
    return {"status": "success", "detail": "Signed up!"}


@auth.post('/api/auth/signup-user')
async def signup_user(
        email: str = Form(),
        first_name: str = Form(),
        last_name: str = Form(),
        password: str = Form(),
        db: AsyncSession = Depends(get_session)
):
    new_user = schemas.UserCreate(email=email, first_name=first_name, last_name=last_name, password=password)
    return await check_signup_user(db, new_user)


@auth.post('/api/auth/logout-user')
async def logout_user(
        response: Response,
        current_user: schemas.User = Security(get_current_user_required, scopes=['volunteer'])
):
    response.delete_cookie("access_token")
    return {"status": "success", "detail": "Logged out!"}
