from http import HTTPStatus


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