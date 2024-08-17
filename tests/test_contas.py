from http import HTTPStatus

import pytest


def test_create_user(client):
    response = client.post(
        '/contas/',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'test',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'test@test.com',
        'username': 'test',
    }


@pytest.mark.parametrize(
    'payload',
    [
        # Repete username
        {
            'username': 'user0',
            'email': 'email@email.com',
            'password': 'test',
        },
        # Repete email (baseado em factory.Sequence)
        {
            'username': 'test',
            'email': 'user1@test.com',
            'password': '12345',
        },
    ],
)
def test_create_user_conflict(client, user, payload):
    response = client.post('/contas/', json=payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'conta já consta no MADR'}
