from http import HTTPStatus


def test_create_romancista(client, token):
    response = client.post(
        '/romancistas/',
        headers={'Authorization': f'Bearer {token}'},
        json={'nome': 'Machado de Assis'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'nome': 'machado de assis', 'id': 1}
