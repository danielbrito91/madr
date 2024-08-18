from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'contas'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]


@table_registry.mapped_as_dataclass
class Livro:
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    ano: Mapped[int]
    titulo: Mapped[str] = mapped_column(unique=True)
    romancista_id: Mapped[int] = mapped_column(ForeignKey('romancistas.id'))


@table_registry.mapped_as_dataclass
class Romancista:
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(unique=True)
