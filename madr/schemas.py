from typing import Sequence, TypeVar

from pydantic import BaseModel, EmailStr

T = TypeVar('T')


class UserSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str


class LivroSchema(BaseModel):
    ano: int
    titulo: str
    romancista_id: int


class LivroPublic(BaseModel):
    id: int
    ano: int
    titulo: str
    romancista_id: int


class LivroUpdate(BaseModel):
    ano: int | None = None
    titulo: str | None = None
    romancista_id: int | None = None


class LivroList(BaseModel):
    total: int
    livros: Sequence[T]
    page: int
    size: int
    pages: int


class RomancistaSchema(BaseModel):
    nome: str


class RomancistaPublic(BaseModel):
    id: int
    nome: str


class RomancistaList(BaseModel):
    total: int
    romancistas: Sequence[T]
    page: int
    size: int
    pages: int
