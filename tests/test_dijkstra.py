from pathlib import Path

import pytest

from src.analise import comparar_topologias, concentracao_de_rotas
from src.dijkstra import menor_caminho
from src.grafo import Grafo


RAIZ = Path(__file__).resolve().parents[1]


def test_menor_caminho_na_topologia_atual() -> None:
    grafo = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")

    resultado = menor_caminho(grafo, "DEV1", "CLOUD")

    assert resultado.caminho == (
        "DEV1",
        "SW1",
        "R1",
        "INTERNET",
        "CLOUD",
    )
    assert resultado.custo_total_ms == pytest.approx(33.0)


def test_topologia_proposta_tem_menor_custo_simulado() -> None:
    atual = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")
    proposta = Grafo.de_json(RAIZ / "data" / "topologia_proposta.json")

    comparacao = comparar_topologias(
        atual,
        proposta,
        "DEV1",
        "CLOUD",
    )

    assert comparacao.custo_proposto_ms < comparacao.custo_atual_ms


def test_concentracao_de_rotas_inclui_switch() -> None:
    grafo = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")

    ranking = concentracao_de_rotas(grafo)

    assert ranking["SW1"] > 0


def test_rejeita_peso_negativo() -> None:
    grafo = Grafo("Teste")
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")

    with pytest.raises(ValueError):
        grafo.adicionar_aresta("A", "B", -1)


def test_caminho_proposta_dev1_cloud() -> None:
    grafo = Grafo.de_json(RAIZ / "data" / "topologia_proposta.json")

    resultado = menor_caminho(grafo, "DEV1", "CLOUD")

    assert resultado.caminho == ("DEV1", "SW_CORE", "FW", "ISP1", "CLOUD")
    assert resultado.custo_total_ms == pytest.approx(27.4)


def test_destino_inalcancavel_retorna_infinito() -> None:
    grafo = Grafo("Ilhas")
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")  # B fica isolado, sem arestas

    resultado = menor_caminho(grafo, "A", "B")

    assert resultado.caminho == ()
    assert resultado.alcancavel is False
    assert resultado.custo_total_ms == float("inf")


def test_origem_igual_destino_tem_custo_zero() -> None:
    grafo = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")

    resultado = menor_caminho(grafo, "DEV1", "DEV1")

    assert resultado.caminho == ("DEV1",)
    assert resultado.custo_total_ms == pytest.approx(0.0)


def test_origem_inexistente_levanta_keyerror() -> None:
    grafo = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")

    with pytest.raises(KeyError):
        menor_caminho(grafo, "NAO_EXISTE", "CLOUD")


def test_destino_inexistente_levanta_keyerror() -> None:
    grafo = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")

    with pytest.raises(KeyError):
        menor_caminho(grafo, "DEV1", "NAO_EXISTE")
