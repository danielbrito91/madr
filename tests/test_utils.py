import pytest

from madr.utils import sanitiza_nome


@pytest.mark.parametrize(
    ('entrada', 'sanitizado'),
    [
        ('Machado de Assis', 'machado de assis'),
        ('Manuel        Bandeira', 'manuel bandeira'),
        ('Edgar Alan Poe         ', 'edgar alan poe'),
        (
            'Androides Sonham Com Ovelhas Elétricas?',
            'androides sonham com ovelhas elétricas',
        ),
        ('  breve  história  do tempo ', 'breve história do tempo'),
        (
            'O mundo assombrado pelos demônios',
            'o mundo assombrado pelos demônios',
        ),
        ('U.S.A.: The Complete Trilogy', 'usa: the complete trilogy'),
    ],
)
def test_sanitizar_nome(entrada, sanitizado):
    assert sanitiza_nome(nome=entrada) == sanitizado
