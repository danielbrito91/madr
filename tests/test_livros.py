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
        'titulo': 'Dom Casmurro',
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
        'titulo': 'Dom Casmurro',
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


@pytest.mark.parametrize(
    ('livros_params', 'url', 'expected_livros'),
    [
        (
            {'size': 1, 'titulo': 'Dom Casmurro'},
            '/livros/?titulo=Dom Casmurro',
            1,
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

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['items']) == expected_livros
