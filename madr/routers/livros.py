from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
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
from madr.security import get_current_user
from madr.utils import sanitiza_nome

router = APIRouter(prefix='/livros', tags=['livros'])


T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=LivroPublic)
def create_livro(
    livro: LivroSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    titulo_sanitizado = sanitiza_nome(livro.titulo)
    db_livro = session.scalar(
        select(Livro).where(
            (Livro.titulo == titulo_sanitizado)
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
        titulo=titulo_sanitizado,
        ano=livro.ano,
        romancista_id=livro.romancista_id,
    )
    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    return db_livro


@router.delete('/{livro_id}')
def delete_livro(
    livro_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
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
    current_user: T_CurrentUser,
):
    db_livro = session.scalar(select(Livro).where((Livro.id == livro_id)))

    if not db_livro:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Livro não consta no MADR',
        )
    for field, value in livro.model_dump(exclude_unset=True).items():
        if field == 'titulo':
            sanitezed_value = sanitiza_nome(value)
            setattr(db_livro, field, sanitezed_value)
        else:
            setattr(db_livro, field, value)

    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)

    return db_livro


@router.get('/{livro_id}', response_model=LivroPublic)
def get_livro_by_id(
    livro_id: int,
    session: T_Session,
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
    titulo: str | None = None,
    ano: int | None = None,
    params: Params = Params(size=20),
):
    query = select(Livro)
    if titulo:
        titulo_sanitizado = sanitiza_nome(titulo)
        query = query.where(Livro.titulo.contains(titulo_sanitizado))

    if ano:
        query = query.where(Livro.ano == ano)

    return paginate(session, query, params)
