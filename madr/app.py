from fastapi import FastAPI

from madr.routers import contas, livros, romancistas

app = FastAPI()
app.include_router(contas.router)
app.include_router(livros.router)
app.include_router(romancistas.router)


@app.get('/')
def read_root():
    return {'message': 'oi!!'}
