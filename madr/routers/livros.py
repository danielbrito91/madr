from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from madr.database import get_session
from madr.models import Livro, Romancista, User
from madr.schemas import (
    LivroPublic,
    LivroSchema,
    LivroUpdate,
)
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


@router.delete('/{livro_id}')
def delete_livro(
    livro_id: int,
    session: T_Session,
    current_user: T_Current_User,
):
    db_livro = session.scalar(select(Livro).where((Livro.id == livro_id)))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR',
        )

    session.delete(db_livro)
    session.commit()

    return {'message': 'Livro deletado no MADR'}


@router.patch('/{livro_id}', response_model=LivroSchema)
def update_livro(
    livro_id: int,
    livro: LivroUpdate,
    session: T_Session,
    current_user: T_Current_User,
):
    db_livro = session.scalar(select(Livro).where((Livro.id == livro_id)))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR',
        )
    for field, value in livro.model_dump(exclude_unset=True).items():
        setattr(db_livro, field, value)

    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    return db_livro


@router.get('/{livro_id}', response_model=LivroPublic)
def get_livro_by_id(
    livro_id: int,
    session: T_Session,
    current_user: T_Current_User,
):
    db_livro = session.scalar(select(Livro).where((Livro.id == livro_id)))
    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR',
        )

    return db_livro


@router.get('/', response_model=Page[LivroPublic])
def get_livros(  # noqa
    session: T_Session,
    current_user: T_Current_User,
    titulo: str | None = None,
    ano: int | None = None,
    params: Params = Params(size=20),
    # limit: int = 20,
    # limit: int = Query(20, ge=0, le=20),
):
    query = select(Livro)
    if titulo:
        query = query.where(Livro.titulo == titulo)

    if ano:
        query = query.where(Livro.ano == ano)

    return paginate(session, query, params)
