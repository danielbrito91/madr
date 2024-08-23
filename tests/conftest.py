import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from madr.app import app
from madr.database import get_session
from madr.models import Livro, Romancista, User, table_registry
from madr.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')


class RomancistaFactory(factory.Factory):
    class Meta:
        model = Romancista

    nome = factory.Sequence(lambda n: f'romancista{n}')


class LivroFactory(factory.Factory):
    class Meta:
        model = Livro

    titulo = factory.Sequence(lambda n: f'livro{n}')
    ano = factory.Sequence(lambda n: 1900 + n)
    romancista_id = factory.Sequence(lambda n: n + 1)


@pytest.fixture
def client(session):
    def get_session_override():
        yield session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    pwd = 'testest'
    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def other_user(session):
    pwd = 'testtest'
    other_user = UserFactory(password=get_password_hash(pwd))

    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_user.clean_password = pwd

    return other_user


@pytest.fixture
def romancista(session):
    romancista = RomancistaFactory()

    session.add(romancista)
    session.commit()
    session.refresh(romancista)

    return romancista


@pytest.fixture
def livro(session):
    livro = LivroFactory()

    session.add(livro)
    session.commit()
    session.refresh(livro)

    return livro


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']
