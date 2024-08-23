from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from jwt import decode

from madr.security import create_access_token, get_current_user
from madr.settings import Settings

settings = Settings()


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, [settings.ALGORITHM])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_token_expires(client, user):
    start_time = '2024-01-01 12:00:00'
    with freeze_time(start_time):
        response = client.post(
            '/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time(
        datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    ):
        response = client.put(
            f'/user/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            data={
                'username': 'new_username',
                'email': 'new_email',
                'password': 'new_password',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Não autorizado'}


def test_get_current_user_without_email_must_return_exception(session):
    data = {}
    token = create_access_token(data)

    with pytest.raises(HTTPException):
        get_current_user(session=session, token=token)


def test_get_current_user_with_invalid_email_must_return_exception(session):
    data = {'sub': 'thisemaildoestnotexist@test.com'}
    token = create_access_token(data)

    with pytest.raises(HTTPException):
        get_current_user(session=session, token=token)
