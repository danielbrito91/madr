from http import HTTPStatus

import pytest

from tests.conftest import LivroFactory, RomancistaFactory


def test_add_livro(client, token, romancista):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': 'Dom Casmurro',
            'ano': 1899,
            'romancista_id': 1,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'titulo': 'dom casmurro',
        'ano': 1899,
        'romancista_id': 1,
        'id': 1,
    }


def test_add_livro_with_romancista_not_found(client, token):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': 'Dom Casmurro',
            'ano': 1899,
            'romancista_id': 999,
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'romancista não encontrado'}


def test_add_livro_already_exists(client, token, romancista, livro):
    response = client.post(
        '/livros/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': livro.titulo,
            'ano': livro.ano,
            'romancista_id': livro.romancista_id,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'livro já consta no MADR'}


def test_add_livro_without_token(client):
    response = client.post(
        '/livros/',
        headers={'Authorization': 'Bearer 1234'},
        json={'nome': 'Dom Casmurro'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_delete_livro(client, token, romancista, livro):
    response = client.delete(
        f'/livros/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Livro deletado no MADR'}


def test_delete_livro_does_not_exists(client, token, romancista, livro):
    response = client.delete(
        '/livros/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro não consta no MADR'}


def test_delete_livro_without_token(client, romancista, livro):
    response = client.delete(
        '/livros/1',
        headers={'Authorization': 'Bearer 1234'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_patch_livro_titulo(client, token, romancista, livro):
    response = client.patch(
        f'/livros/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'titulo': 'Dom Casmurro',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'titulo': 'dom casmurro',
        'ano': livro.ano,
        'romancista_id': livro.romancista_id,
    }


def test_patch_livro_ano(client, token, romancista, livro):
    response = client.patch(
        f'/livros/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'ano': 1888,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'titulo': livro.titulo,
        'ano': 1888,
        'romancista_id': livro.romancista_id,
    }


def test_patch_livro_romancista_id(client, token, romancista, livro):
    response = client.patch(
        f'/livros/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'romancista_id': 1},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'titulo': livro.titulo,
        'ano': livro.ano,
        'romancista_id': 1,
    }


def test_patch_livro_doesnot_exists(client, token, romancista, livro):
    response = client.patch(
        '/livros/999',
        json={'ano': 2000},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro não consta no MADR'}


def test_patch_livro_without_token(client, romancista, livro):
    response = client.patch(
        f'/livros/{livro.id}',
        headers={'Authorization': 'Bearer 1234'},
        json={
            'titulo': 'Dom Casmurro',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Não autorizado'}


def test_get_livro_by_id(client, token, romancista, livro):
    response = client.get(
        f'/livros/{livro.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'titulo': livro.titulo,
        'ano': livro.ano,
        'romancista_id': livro.romancista_id,
        'id': livro.id,
    }


def test_get_livro_by_id_not_found(client, token, romancista, livro):
    response = client.get(
        '/livros/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Livro não consta no MADR'}


def test_get_livro_by_id_without_token(client, romancista, livro):
    response = client.get(
        f'/livros/{livro.id}',
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    ('livros_params', 'url', 'expected_livros'),
    [
        (
            {'size': 1, 'titulo': 'Dom Casmurro'},
            '/livros/?titulo=Dom Casmurro',
            1,
        ),
        (
            {'size': 1, 'titulo': 'Dom Casmurro'},
            '/livros/?titulo=dom',
            1,
        ),
        (
            {'size': 1, 'titulo': 'Dom Casmurro'},
            '/livros/?titulo=lusíadas',
            0,
        ),
        (
            {'size': 10, 'ano': 2024},
            '/livros/?ano=2024',
            10,
        ),
        (
            {'size': 60, 'ano': 2024},
            '/livros/?ano=2024',
            60,
        ),
    ],
)
def test_get_livro(  # noqa
    session,
    client,
    token,
    livros_params,
    url,
    expected_livros,
    page_limit: int = 20,
):
    session.bulk_save_objects(
        RomancistaFactory.create_batch(size=livros_params.get('size'))
    )
    session.commit()

    session.bulk_save_objects(LivroFactory.create_batch(**livros_params))
    session.commit()

    response = client.get(
        url,
        headers={'Authorization': f'Bearer {token}'},
    )
    query_param, query_value = list(livros_params.items())[1]
    assert response.status_code == HTTPStatus.OK
    assert response.json()['total'] == expected_livros
    assert response.json()['size'] == page_limit
    assert (
        response.json()['pages']
        == (expected_livros + page_limit - 1) // page_limit
    )
    if expected_livros > 0:
        assert response.json()['livros'][0][query_param] == query_value
    elif expected_livros == 0:
        assert response.json()['livros'] == []


def test_get_livro_without_token(client, romancista, livro):
    response = client.get(
        '/livros/?titulo=livro',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['livros'][0]['titulo'] == livro.titulo
