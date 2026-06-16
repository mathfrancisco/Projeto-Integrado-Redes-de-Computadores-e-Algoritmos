from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf, isfinite

from src.grafo import Grafo


@dataclass(frozen=True)
class ResultadoCaminho:
    origem: str
    destino: str
    caminho: tuple[str, ...]
    custo_total_ms: float

    @property
    def alcancavel(self) -> bool:
        return bool(self.caminho) and isfinite(self.custo_total_ms)


def dijkstra(
    grafo: Grafo,
    origem: str,
) -> tuple[dict[str, float], dict[str, str | None]]:
    """Calcula as menores distâncias partindo de um nó de origem."""

    if not grafo.contem_no(origem):
        raise KeyError(f"Origem inexistente: {origem}")

    distancias = {no: inf for no in grafo.nos}
    predecessores: dict[str, str | None] = {
        no: None for no in grafo.nos
    }

    distancias[origem] = 0.0
    fila: list[tuple[float, str]] = [(0.0, origem)]

    while fila:
        distancia_atual, no_atual = heappop(fila)

        # Ignora entradas antigas da fila.
        if distancia_atual > distancias[no_atual]:
            continue

        for vizinho, peso in grafo.vizinhos(no_atual).items():
            nova_distancia = distancia_atual + peso

            if nova_distancia < distancias[vizinho]:
                distancias[vizinho] = nova_distancia
                predecessores[vizinho] = no_atual
                heappush(fila, (nova_distancia, vizinho))

    return distancias, predecessores


def reconstruir_caminho(
    predecessores: dict[str, str | None],
    origem: str,
    destino: str,
) -> tuple[str, ...]:
    if origem == destino:
        return (origem,)

    caminho: list[str] = []
    atual: str | None = destino

    while atual is not None:
        caminho.append(atual)

        if atual == origem:
            caminho.reverse()
            return tuple(caminho)

        atual = predecessores.get(atual)

    return tuple()


def menor_caminho(
    grafo: Grafo,
    origem: str,
    destino: str,
) -> ResultadoCaminho:
    if not grafo.contem_no(destino):
        raise KeyError(f"Destino inexistente: {destino}")

    distancias, predecessores = dijkstra(grafo, origem)
    caminho = reconstruir_caminho(
        predecessores=predecessores,
        origem=origem,
        destino=destino,
    )

    return ResultadoCaminho(
        origem=origem,
        destino=destino,
        caminho=caminho,
        custo_total_ms=distancias[destino],
    )
