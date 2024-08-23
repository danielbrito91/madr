import re

from fastapi_pagination import Params


def sanitiza_nome(nome: str) -> str:
    nome = re.sub(r'\s+', ' ', nome)
    nome = re.sub(r'[.!?]', '', nome)
    return nome.lower().strip()


def get_params(size: int = 20):
    return Params(size=size)
