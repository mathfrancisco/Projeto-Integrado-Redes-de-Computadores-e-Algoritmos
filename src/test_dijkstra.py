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
