from http import HTTPStatus

import pytest

from tests.conftest import RomancistaFactory


def test_create_romancista(client, token):
    response = client.post(
        '/romancistas/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Machado de Assis'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'nome': 'machado de assis', 'id': 1}


def test_create_romancista_already_exists(client, token, romancista):
    response = client.post(
        '/romancistas/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': romancista.nome},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'romancista já consta no MADR'}


def test_delete_romancista(client, token, romancista):
    response = client.delete(
        f'/romancistas/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Romancista deletada no MADR'}


def test_delete_romancista_does_not_exist(client, token, romancista):
    response = client.delete(
        '/romancistas/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'romancista não encontrado'}


def test_patch_romancista(client, token, romancista):
    response = client.patch(
        f'/romancistas/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Machado de Assis'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'nome': 'machado de assis', 'id': romancista.id}


def test_patch_romancista_does_not_exist(client, token, romancista):
    response = client.patch(
        '/romancistas/999',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Machado de Assis'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'romancista não encontrado'}


def test_patch_romancista_nome_sanitizado_already_exists(
    client, token, romancista
):
    response = client.patch(
        f'/romancistas/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': romancista.nome},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'romancista já consta no MADR'}


def test_get_romancista_by_id(client, token, romancista):
    response = client.get(
        f'/romancistas/{romancista.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': romancista.id, 'nome': romancista.nome}


def test_get_romancista_by_id_not_found(client, token, romancista):
    response = client.get(
        '/romancistas/999',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'romancista não encontrado'}


@pytest.mark.parametrize(
    (
        'romancista_params',
        'url',
        'expected_romancistas',
    ),
    [
        (
            {'size': 1, 'nome': 'Machado de Assis'},
            '/romancistas/?nome=Machado de Assis',
            1,
        ),
        (
            {'size': 1, 'nome': 'Machado de Assis'},
            '/romancistas/?nome=mach',
            1,
        ),
        (
            {'size': 1, 'nome': 'Machado de Assis'},
            '/romancistas/?nome=clarice',
            0,
        ),
        (
            {'size': 10},
            '/romancistas/?nome=roman',
            10,
        ),
        (
            {
                'size': 60,
            },
            '/romancistas/?nome=roman',
            60,
        ),
    ],
)
def test_get_livro(  # noqa
    session,
    client,
    token,
    romancista_params,
    url,
    expected_romancistas,
    page_limit: int = 20,
):
    session.bulk_save_objects(
        RomancistaFactory.create_batch(**romancista_params)
    )
    session.commit()

    response = client.get(
        url,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['total'] == expected_romancistas
    assert response.json()['size'] == page_limit
    assert (
        response.json()['pages']
        == (expected_romancistas + page_limit - 1) // page_limit
    )
    if expected_romancistas == 0:
        assert response.json()['romancistas'] == []
