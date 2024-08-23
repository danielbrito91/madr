from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from madr.database import get_session
from madr.models import Romancista, User
from madr.schemas import RomancistaList, RomancistaPublic, RomancistaSchema
from madr.security import get_current_user
from madr.utils import sanitiza_nome

router = APIRouter(prefix='/romancistas', tags=['romancistas'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
def create_romancista(
    romancista: RomancistaSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    nome_sanitizado = sanitiza_nome(romancista.nome)
    db_romancista = session.scalar(
        select(Romancista).where((Romancista.nome == nome_sanitizado))
    )

    if db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='romancista já consta no MADR',
        )

    db_romancista = Romancista(
        nome=nome_sanitizado,
    )
    session.add(db_romancista)
    session.commit()
    session.refresh(db_romancista)

    return db_romancista


@router.delete('/{romancista_id}')
def delete_romancista(
    romancista_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )
    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='romancista não encontrado',
        )
    return {'message': 'Romancista deletada no MADR'}


@router.patch('/{romancista_id}', response_model=RomancistaPublic)
def update_romancista(
    romancista_id: int,
    romancista: RomancistaSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )

    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='romancista não encontrado',
        )

    nome_sanitizado = sanitiza_nome(romancista.nome)

    db_romancista_nome = session.scalar(
        select(Romancista).where(Romancista.nome == nome_sanitizado)
    )
    if db_romancista_nome:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='romancista já consta no MADR',
        )

    setattr(db_romancista, 'nome', nome_sanitizado)

    session.add(db_romancista)
    session.commit()
    session.refresh(db_romancista)

    return db_romancista


@router.get('/{romancista_id}', response_model=RomancistaPublic)
def read_romancista_by_id(romancista_id: int, session: T_Session):
    db_romancista = session.scalar(
        select(Romancista).where(Romancista.id == romancista_id)
    )
    if not db_romancista:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='romancista não encontrado',
        )
    return db_romancista


@router.get('/', response_model=RomancistaList)
def read_romancistas(
    session: T_Session,
    nome: str,
    params: Params = Params(size=20),
):
    query = select(Romancista).where(
        Romancista.nome.contains(sanitiza_nome(nome))
    )

    paginated = paginate(session, query, params)

    return RomancistaList(
        total=paginated.total,
        romancistas=[
            RomancistaPublic(
                id=i.id,
                nome=i.nome,
            )
            for i in paginated.items
        ],
        page=paginated.page,
        size=paginated.size,
        pages=paginated.pages,
    )
