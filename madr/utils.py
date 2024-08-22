import re


def sanitiza_nome(nome: str) -> str:
    nome = re.sub(r'\s+', ' ', nome)
    nome = re.sub(r'[.!?]', '', nome)
    return nome.lower().strip()
