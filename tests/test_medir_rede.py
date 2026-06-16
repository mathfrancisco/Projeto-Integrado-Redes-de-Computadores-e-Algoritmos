"""Testes dos interpretadores da saída de ping (funções puras, sem rede)."""

import pytest

from scripts.medir_rede import (
    converter_numero,
    interpretar_linux,
    interpretar_windows,
)

PING_WINDOWS_EN = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=14ms TTL=117

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 13ms, Maximum = 18ms, Average = 15ms
"""

PING_WINDOWS_PT = """
Disparando 8.8.8.8 com 32 bytes de dados:
Resposta de 8.8.8.8: bytes=32 tempo=14ms TTL=117

Estatísticas do Ping para 8.8.8.8:
    Pacotes: Enviados = 4, Recebidos = 4, Perdidos = 0 (0% de perda),
Aproximar um número redondo de vezes em milissegundos:
    Mínimo = 13ms, Máximo = 18ms, Média = 15ms
"""

# Saída real PT-BR: o "(0% de perda)" quebra de linha entre 'de' e 'perda'.
PING_WINDOWS_PT_QUEBRADO = """
Estatísticas do Ping para 8.8.8.8:
    Pacotes: Enviados = 2, Recebidos = 2, Perdidos = 0 (0% de
             perda),
Aproximar um número redondo de vezes em milissegundos:
    Mínimo = 14ms, Máximo = 14ms, Média = 14ms
"""

PING_WINDOWS_PERDA_TOTAL = """
Ping statistics for 10.0.0.9:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
"""

PING_LINUX = """
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=14.2 ms
--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 13.1/15.2/18.3/1.0 ms
"""


def test_converter_numero_aceita_virgula() -> None:
    assert converter_numero("12,5") == pytest.approx(12.5)
    assert converter_numero("12.5") == pytest.approx(12.5)


def test_windows_en() -> None:
    enviados, recebidos, perda, minimo, medio, maximo = interpretar_windows(PING_WINDOWS_EN)

    assert (enviados, recebidos, perda) == (4, 4, 0.0)
    assert (minimo, medio, maximo) == (13.0, 15.0, 18.0)


def test_windows_pt() -> None:
    enviados, recebidos, perda, minimo, medio, maximo = interpretar_windows(PING_WINDOWS_PT)

    assert (enviados, recebidos, perda) == (4, 4, 0.0)
    assert (minimo, medio, maximo) == (13.0, 15.0, 18.0)


def test_windows_pt_com_quebra_de_linha() -> None:
    # Regressão: a quebra entre 'de' e 'perda' fazia o resumo não casar (REVISAR).
    enviados, recebidos, perda, minimo, medio, maximo = interpretar_windows(
        PING_WINDOWS_PT_QUEBRADO
    )

    assert (enviados, recebidos, perda) == (2, 2, 0.0)
    assert (minimo, medio, maximo) == (14.0, 14.0, 14.0)


def test_windows_perda_total_sem_tempos() -> None:
    enviados, recebidos, perda, minimo, medio, maximo = interpretar_windows(
        PING_WINDOWS_PERDA_TOTAL
    )

    assert (enviados, recebidos, perda) == (4, 0, 100.0)
    assert (minimo, medio, maximo) == (None, None, None)


def test_linux() -> None:
    enviados, recebidos, perda, minimo, medio, maximo = interpretar_linux(PING_LINUX)

    assert (enviados, recebidos, perda) == (4, 4, 0.0)
    assert (minimo, medio, maximo) == (13.1, 15.2, 18.3)


def test_saida_irreconhecivel_retorna_none() -> None:
    assert interpretar_windows("texto sem dados") == (None,) * 6
    assert interpretar_linux("texto sem dados") == (None,) * 6
