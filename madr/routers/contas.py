from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from madr.database import get_session
from madr.schemas import UserPublic, UserSchema

from madr.models import User
from madr.security import get_password_hash


T_Session = Annotated[Session, Depends(get_session)]

router = APIRouter(prefix='/contas', tags=['contas'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema,
    session: T_Session,
):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user
