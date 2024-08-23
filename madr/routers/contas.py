from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from madr.database import get_session
from madr.models import User
from madr.schemas import Token, UserPublic, UserSchema
from madr.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from madr.utils import sanitiza_nome

router = APIRouter(prefix='/user', tags=['contas'])

T_Session = Annotated[Session, Depends(get_session)]
T_Current_User = Annotated[User, Depends(get_current_user)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema,
    session: T_Session,
):
    username_sanitizado = sanitiza_nome(user.username)
    db_user = session.scalar(
        select(User).where(
            (User.username == username_sanitizado) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='conta já consta no MADR',
        )

    db_user = User(
        username=username_sanitizado,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_Current_User,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Não autorizado',
        )

    username_sanitizado = sanitiza_nome(user.username)
    db_user = session.scalar(
        select(User).where(
            (User.username == username_sanitizado) | (User.email == user.email)
        )
    )
    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='conta já consta no MADR',
        )

    current_user.username = username_sanitizado
    current_user.email = user.email
    current_user.password = get_password_hash(user.password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}')
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_Current_User,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Não autorizado',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'Conta deletada com sucesso'}


@router.post('/token', response_model=Token)
def login_for_access_token(session: T_Session, form: T_OAuth2Form):
    user = session.scalar(select(User).where(User.email == form.username))

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email ou senha incorretos',
        )

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh-token', response_model=Token)
def refresh_access_token(user: T_Current_User):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
