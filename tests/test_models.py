from sqlalchemy.sql import select

from madr.models import User


def test_create_user(session):
    user = User(username='daniel', email='email@email.com', password='123456')

    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.username == 'daniel'))

    assert result.id == 1
    assert result.email == 'email@email.com'
    assert result.password == '123456'
