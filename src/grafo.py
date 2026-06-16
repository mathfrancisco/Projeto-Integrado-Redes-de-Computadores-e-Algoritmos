from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ErroTopologia(ValueError):
    """Erro encontrado durante a leitura ou validação da topologia."""


@dataclass(frozen=True)
class Aresta:
    origem: str
    destino: str
    latencia_ms: float
    meio: str = ""
    bidirecional: bool = True


class Grafo:
    """Grafo ponderado representado por uma lista de adjacência."""

    def __init__(self, nome: str = "Topologia") -> None:
        self.nome = nome
        self._nos: dict[str, dict[str, Any]] = {}
        self._adjacencias: dict[str, dict[str, float]] = {}
        self._arestas: list[Aresta] = []

    @property
    def nos(self) -> tuple[str, ...]:
        return tuple(self._nos.keys())

    @property
    def arestas(self) -> tuple[Aresta, ...]:
        return tuple(self._arestas)

    def adicionar_no(self, identificador: str, **atributos: Any) -> None:
        identificador = identificador.strip()

        if not identificador:
            raise ErroTopologia("O identificador do nó não pode ser vazio.")

        if identificador in self._nos:
            raise ErroTopologia(f"Nó duplicado: {identificador}")

        self._nos[identificador] = dict(atributos)
        self._adjacencias[identificador] = {}

    def adicionar_aresta(
        self,
        origem: str,
        destino: str,
        latencia_ms: float,
        *,
        meio: str = "",
        bidirecional: bool = True,
    ) -> None:
        if origem not in self._nos:
            raise ErroTopologia(f"Nó de origem inexistente: {origem}")

        if destino not in self._nos:
            raise ErroTopologia(f"Nó de destino inexistente: {destino}")

        try:
            latencia = float(latencia_ms)
        except (TypeError, ValueError) as exc:
            raise ErroTopologia(
                f"Latência inválida na conexão {origem} -> {destino}."
            ) from exc

        if latencia < 0 or not math.isfinite(latencia):
            raise ErroTopologia(
                "O algoritmo de Dijkstra exige pesos finitos e não negativos."
            )

        self._adjacencias[origem][destino] = latencia

        if bidirecional:
            self._adjacencias[destino][origem] = latencia

        self._arestas.append(
            Aresta(
                origem=origem,
                destino=destino,
                latencia_ms=latencia,
                meio=meio,
                bidirecional=bidirecional,
            )
        )

    def contem_no(self, identificador: str) -> bool:
        return identificador in self._nos

    def vizinhos(self, identificador: str) -> dict[str, float]:
        if identificador not in self._adjacencias:
            raise KeyError(f"Nó inexistente: {identificador}")

        return dict(self._adjacencias[identificador])

    def atributos(self, identificador: str) -> dict[str, Any]:
        if identificador not in self._nos:
            raise KeyError(f"Nó inexistente: {identificador}")

        return dict(self._nos[identificador])

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "Grafo":
        if not isinstance(dados, dict):
            raise ErroTopologia("A topologia deve ser um objeto JSON.")

        grafo = cls(str(dados.get("nome", "Topologia")))

        nos = dados.get("nos")
        arestas = dados.get("arestas")

        if not isinstance(nos, list) or not nos:
            raise ErroTopologia("'nos' deve ser uma lista não vazia.")

        if not isinstance(arestas, list):
            raise ErroTopologia("'arestas' deve ser uma lista.")

        for item in nos:
            if not isinstance(item, dict) or "id" not in item:
                raise ErroTopologia("Cada nó deve possuir a propriedade 'id'.")

            atributos = dict(item)
            identificador = str(atributos.pop("id"))
            grafo.adicionar_no(identificador, **atributos)

        for item in arestas:
            if not isinstance(item, dict):
                raise ErroTopologia("Cada aresta deve ser um objeto JSON.")

            obrigatorios = {"origem", "destino", "latencia_ms"}
            ausentes = obrigatorios - item.keys()

            if ausentes:
                campos = ", ".join(sorted(ausentes))
                raise ErroTopologia(f"Aresta sem os campos obrigatórios: {campos}")

            grafo.adicionar_aresta(
                origem=str(item["origem"]),
                destino=str(item["destino"]),
                latencia_ms=float(item["latencia_ms"]),
                meio=str(item.get("meio", "")),
                bidirecional=bool(item.get("bidirecional", True)),
            )

        return grafo

    @classmethod
    def de_json(cls, caminho: str | Path) -> "Grafo":
        arquivo = Path(caminho)

        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ErroTopologia(f"Arquivo não encontrado: {arquivo}") from exc
        except json.JSONDecodeError as exc:
            raise ErroTopologia(
                f"JSON inválido: linha {exc.lineno}, coluna {exc.colno}."
            ) from exc

        return cls.de_dict(dados)
