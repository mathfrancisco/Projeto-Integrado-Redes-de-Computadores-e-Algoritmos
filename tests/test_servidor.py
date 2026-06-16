"""Testes da validação de host do servidor de testes (proteção de entrada)."""

import pytest

from scripts.servidor_testes import validar_host


@pytest.mark.parametrize(
    "host",
    ["8.8.8.8", "1.1.1.1", "google.com", "host-name.local", "  8.8.8.8  "],
)
def test_hosts_validos(host: str) -> None:
    # Espaços nas pontas são removidos antes da validação.
    assert validar_host(host) == host.strip()


@pytest.mark.parametrize(
    "host",
    ["", "bad host", "a;rm -rf /", "8.8.8.8 && calc", "host/rota", "x" * 254],
)
def test_hosts_invalidos_sao_rejeitados(host: str) -> None:
    with pytest.raises(ValueError):
        validar_host(host)
