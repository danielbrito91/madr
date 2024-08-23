from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from madr.database import get_session
from madr.models import User
from madr.routers import contas, livros, romancistas
from madr.schemas import Token
from madr.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]

app = FastAPI()
app.include_router(contas.router)
app.include_router(livros.router)
app.include_router(romancistas.router)

add_pagination(app)


@app.get('/')
def read_root():
    return {'message': ''}


@app.post('/token', response_model=Token)
def login_for_access_token(session: T_Session, form: T_OAuth2Form):
    user = session.scalar(select(User).where(User.email == form.username))

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email ou senha incorretos',
        )

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/refresh-token', response_model=Token)
def refresh_access_token(user: T_CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
