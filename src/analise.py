from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from src.dijkstra import menor_caminho
from src.grafo import Grafo


@dataclass(frozen=True)
class Comparacao:
    origem: str
    destino: str
    caminho_atual: tuple[str, ...]
    caminho_proposto: tuple[str, ...]
    custo_atual_ms: float
    custo_proposto_ms: float

    @property
    def diferenca_ms(self) -> float:
        return self.custo_atual_ms - self.custo_proposto_ms

    @property
    def melhoria_percentual(self) -> float:
        if self.custo_atual_ms == 0:
            return 0.0

        return (self.diferenca_ms / self.custo_atual_ms) * 100


def concentracao_de_rotas(grafo: Grafo) -> Counter[str]:
    """Conta quantos menores caminhos passam por cada nó intermediário."""

    contagem: Counter[str] = Counter()

    for origem, destino in combinations(sorted(grafo.nos), 2):
        resultado = menor_caminho(grafo, origem, destino)

        if not resultado.alcancavel:
            continue

        for no_intermediario in resultado.caminho[1:-1]:
            contagem[no_intermediario] += 1

    for no in grafo.nos:
        contagem.setdefault(no, 0)

    return contagem


def comparar_topologias(
    atual: Grafo,
    proposta: Grafo,
    origem: str,
    destino: str,
) -> Comparacao:
    atual_resultado = menor_caminho(atual, origem, destino)
    proposta_resultado = menor_caminho(proposta, origem, destino)

    if not atual_resultado.alcancavel:
        raise ValueError(
            f"Não existe caminho na topologia atual: {origem} -> {destino}"
        )

    if not proposta_resultado.alcancavel:
        raise ValueError(
            f"Não existe caminho na topologia proposta: {origem} -> {destino}"
        )

    return Comparacao(
        origem=origem,
        destino=destino,
        caminho_atual=atual_resultado.caminho,
        caminho_proposto=proposta_resultado.caminho,
        custo_atual_ms=atual_resultado.custo_total_ms,
        custo_proposto_ms=proposta_resultado.custo_total_ms,
    )
