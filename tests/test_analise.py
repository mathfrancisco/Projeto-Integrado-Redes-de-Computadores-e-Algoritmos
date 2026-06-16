"""Testes da camada de análise: comparação de topologias e gargalos."""

from pathlib import Path

import pytest

from src.analise import comparar_topologias, concentracao_de_rotas
from src.grafo import Grafo

RAIZ = Path(__file__).resolve().parents[1]


def carregar(nome: str) -> Grafo:
    return Grafo.de_json(RAIZ / "data" / nome)


def test_comparacao_calcula_diferenca_e_melhoria() -> None:
    comparacao = comparar_topologias(
        carregar("topologia_atual.json"),
        carregar("topologia_proposta.json"),
        "DEV1",
        "CLOUD",
    )

    assert comparacao.custo_atual_ms == pytest.approx(33.0)
    assert comparacao.custo_proposto_ms == pytest.approx(27.4)
    assert comparacao.diferenca_ms == pytest.approx(5.6)
    # 5.6 / 33.0 * 100 ≈ 16.97%
    assert comparacao.melhoria_percentual == pytest.approx(16.9697, abs=1e-3)


def grafo_ilhado(nome: str) -> Grafo:
    grafo = Grafo(nome)
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")  # sem aresta entre A e B
    return grafo


def test_comparacao_destino_inalcancavel_levanta_erro() -> None:
    with pytest.raises(ValueError):
        comparar_topologias(
            grafo_ilhado("Atual"),
            grafo_ilhado("Proposta"),
            "A",
            "B",
        )


def test_concentracao_de_rotas_marca_pontos_criticos() -> None:
    grafo = carregar("topologia_atual.json")

    ranking = concentracao_de_rotas(grafo)

    # SW1 e R1 são pontos únicos de falha: passam por muitas rotas.
    assert ranking["SW1"] > 0
    assert ranking["R1"] > 0
    # Todo nó aparece no Counter, mesmo com zero.
    assert set(ranking) == set(grafo.nos)


def test_melhoria_percentual_zero_quando_custo_atual_zero() -> None:
    grafo = carregar("topologia_atual.json")

    # Mesmo nó: custo zero nas duas pontas -> melhoria 0, sem divisão por zero.
    comparacao = comparar_topologias(grafo, grafo, "DEV1", "DEV1")

    assert comparacao.custo_atual_ms == pytest.approx(0.0)
    assert comparacao.melhoria_percentual == 0.0
