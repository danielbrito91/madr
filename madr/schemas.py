from pydantic import BaseModel, EmailStr


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


class RomancistaSchema(BaseModel):
    nome: str


class RomancistaPublic(BaseModel):
    id: int
    nome: str
