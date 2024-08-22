from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from madr.database import get_session
from madr.models import Romancista
from madr.schemas import RomancistaPublic, RomancistaSchema
from madr.utils import sanitiza_nome

router = APIRouter(prefix='/romancistas', tags=['romancistas'])
T_Session = Annotated[Session, Depends(get_session)]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=RomancistaPublic
)
def create_romancista(romancista: RomancistaSchema, session: T_Session):
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
def delete_romancista(romancista_id: int):
    raise NotImplementedError


@router.patch('/{romancista_id}', response_model=RomancistaPublic)
def update_romancista(romancista_id: int, nome: RomancistaSchema):
    raise NotImplementedError


@router.get('/{romancista_id}', response_model=RomancistaPublic)
def read_romancista_by_id(romancista_id: int):
    raise NotImplementedError


@router.get('/', response_model=list[RomancistaPublic])
def read_romancistas():
    raise NotImplementedError
