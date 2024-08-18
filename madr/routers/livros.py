from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from madr.database import get_session
from madr.models import Livro, Romancista, User
from madr.schemas import LivroPublic, LivroSchema
from madr.security import (
    get_current_user,
)

router = APIRouter(prefix='/livros', tags=['livros'])

T_Session = Annotated[Session, Depends(get_session)]
T_Current_User = Annotated[User, Depends(get_current_user)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/', response_model=LivroPublic)
def create_livro(
    livro: LivroSchema,
    session: T_Session,
    current_user: T_Current_User,
):
    db_livro = session.scalar(
        select(Livro).where(
            (Livro.titulo == livro.titulo)
            & (Livro.romancista_id == livro.romancista_id)
        )
    )

    if db_livro:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='livro já consta no MADR',
        )

    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == livro.romancista_id)
    )

    if db_romancista is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='romancista não encontrado',
        )

    db_livro = Livro(
        titulo=livro.titulo,
        ano=livro.ano,
        romancista_id=livro.romancista_id,
    )
    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    print(db_romancista)
    return db_livro
