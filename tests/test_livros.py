from http import HTTPStatus


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
