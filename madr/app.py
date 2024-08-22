from fastapi import FastAPI
from fastapi_pagination import add_pagination

from madr.routers import contas, livros, romancistas

app = FastAPI()
app.include_router(contas.router)
app.include_router(livros.router)
app.include_router(romancistas.router)

add_pagination(app)


@app.get('/')
def read_root():
    return {'message': 'oi!!'}
