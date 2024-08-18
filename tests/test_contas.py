from http import HTTPStatus

import pytest


def test_create_user(client):
    response = client.post(
        '/user/',
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
    response = client.post('/user/', json=payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'conta já consta no MADR'}


# Teste auth
def test_get_token(client, user):
    response = client.post(
        '/user/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


@pytest.mark.parametrize(
    'form',
    [
        # Non-existent user
        {'username': 'non_existent', 'password': '123456'},
        # Wrong password
        {'username': 'user1@test.com', 'password': 'wrong_password'},
    ],
)
def test_get_token_invalid(client, form, user):
    response = client.post(
        '/user/token',
        data=form,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email ou senha incorretos'}


def test_update_user(client, user, token):
    response = client.put(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'new_username',
            'email': 'new_email@email.com',
            'password': 'new_password',
            'id': 999,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'new_username',
        'email': 'new_email@email.com',
        'id': 1,
    }


def test_update_user_other_client_id(client, user, token):
    response = client.put(
        '/user/99',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'new_username',
            'email': 'new_email@email.com',
            'password': 'new_password',
            'id': 999,
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_update_user_repeating_other_user_username(
    client, user, other_user, token
):
    response = client.put(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': 'a-new-email@email.com',
            'password': 'new_password',
            'id': 999,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'conta já consta no MADR'}


def test_update_user_repeating_other_user_email(
    client, user, other_user, token
):
    response = client.put(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'a-new-username',
            'email': other_user.email,
            'password': 'new_password',
            'id': 999,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'conta já consta no MADR'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Conta deletada com sucesso'}


def test_delete_user_other_client_id(client, other_user, token):
    response = client.delete(
        f'/user/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/user/refresh-token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'
