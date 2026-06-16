"""Testes de validação da estrutura de grafo (carga e regras de integridade)."""

import pytest

from src.grafo import ErroTopologia, Grafo


def grafo_minimo() -> dict:
    return {
        "nome": "Mínimo",
        "nos": [{"id": "A"}, {"id": "B"}],
        "arestas": [{"origem": "A", "destino": "B", "latencia_ms": 1.0}],
    }


def test_de_dict_carrega_nos_e_arestas() -> None:
    grafo = Grafo.de_dict(grafo_minimo())

    assert set(grafo.nos) == {"A", "B"}
    assert grafo.vizinhos("A") == {"B": 1.0}
    # Aresta bidirecional por padrão.
    assert grafo.vizinhos("B") == {"A": 1.0}


def test_no_duplicado_e_rejeitado() -> None:
    grafo = Grafo()
    grafo.adicionar_no("A")

    with pytest.raises(ErroTopologia):
        grafo.adicionar_no("A")


def test_aresta_com_no_inexistente_e_rejeitada() -> None:
    grafo = Grafo()
    grafo.adicionar_no("A")

    with pytest.raises(ErroTopologia):
        grafo.adicionar_aresta("A", "FANTASMA", 1.0)


def test_lista_de_nos_vazia_e_rejeitada() -> None:
    with pytest.raises(ErroTopologia):
        Grafo.de_dict({"nome": "X", "nos": [], "arestas": []})


def test_aresta_sem_campos_obrigatorios_e_rejeitada() -> None:
    dados = grafo_minimo()
    dados["arestas"] = [{"origem": "A", "destino": "B"}]  # falta latencia_ms

    with pytest.raises(ErroTopologia):
        Grafo.de_dict(dados)


def test_no_sem_id_e_rejeitado() -> None:
    dados = grafo_minimo()
    dados["nos"] = [{"tipo": "computador"}]  # sem 'id'

    with pytest.raises(ErroTopologia):
        Grafo.de_dict(dados)


def test_aresta_unidirecional_nao_volta() -> None:
    grafo = Grafo()
    grafo.adicionar_no("A")
    grafo.adicionar_no("B")
    grafo.adicionar_aresta("A", "B", 2.0, bidirecional=False)

    assert grafo.vizinhos("A") == {"B": 2.0}
    assert grafo.vizinhos("B") == {}


def test_de_json_arquivo_inexistente() -> None:
    with pytest.raises(ErroTopologia):
        Grafo.de_json("caminho/que/nao/existe.json")


def test_atributos_preserva_metadados_do_no() -> None:
    grafo = Grafo.de_dict(
        {
            "nome": "Meta",
            "nos": [{"id": "DEV1", "tipo": "computador", "vlan": 20}],
            "arestas": [],
        }
    )

    assert grafo.atributos("DEV1") == {"tipo": "computador", "vlan": 20}
