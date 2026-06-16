from __future__ import annotations

import argparse
from math import isfinite
from pathlib import Path

from src.analise import comparar_topologias, concentracao_de_rotas
from src.dijkstra import menor_caminho
from src.grafo import ErroTopologia, Grafo


def formatar_caminho(caminho: tuple[str, ...]) -> str:
    return " -> ".join(caminho) if caminho else "INALCANÇÁVEL"


def executar_caminho(args: argparse.Namespace) -> None:
    grafo = Grafo.de_json(args.topologia)
    resultado = menor_caminho(grafo, args.origem, args.destino)

    print(f"Topologia: {grafo.nome}")
    print(f"Origem: {resultado.origem}")
    print(f"Destino: {resultado.destino}")
    print(f"Caminho: {formatar_caminho(resultado.caminho)}")

    if isfinite(resultado.custo_total_ms):
        print(f"Latência acumulada: {resultado.custo_total_ms:.2f} ms")
    else:
        print("Latência acumulada: infinito")


def executar_gargalos(args: argparse.Namespace) -> None:
    grafo = Grafo.de_json(args.topologia)
    ranking = concentracao_de_rotas(grafo).most_common(args.limite)

    print(f"Topologia: {grafo.nome}")
    print("Nós com maior concentração de caminhos mínimos:")

    for posicao, (no, quantidade) in enumerate(ranking, start=1):
        print(f"{posicao:>2}. {no:<15} {quantidade:>3} rotas")


def executar_comparacao(args: argparse.Namespace) -> None:
    atual = Grafo.de_json(args.atual)
    proposta = Grafo.de_json(args.proposta)

    resultado = comparar_topologias(
        atual=atual,
        proposta=proposta,
        origem=args.origem,
        destino=args.destino,
    )

    print("TOPOLOGIA ATUAL")
    print(f"Caminho: {formatar_caminho(resultado.caminho_atual)}")
    print(f"Custo: {resultado.custo_atual_ms:.2f} ms")
    print()

    print("TOPOLOGIA PROPOSTA")
    print(f"Caminho: {formatar_caminho(resultado.caminho_proposto)}")
    print(f"Custo: {resultado.custo_proposto_ms:.2f} ms")
    print()

    print(f"Diferença: {resultado.diferenca_ms:.2f} ms")
    print(f"Melhoria estimada: {resultado.melhoria_percentual:.2f}%")


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Análise de rede utilizando grafos e Dijkstra."
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    caminho = subparsers.add_parser(
        "caminho",
        help="Calcula o caminho de menor latência.",
    )
    caminho.add_argument("--topologia", type=Path, required=True)
    caminho.add_argument("--origem", required=True)
    caminho.add_argument("--destino", required=True)
    caminho.set_defaults(funcao=executar_caminho)

    gargalos = subparsers.add_parser(
        "gargalos",
        help="Lista os nós utilizados por mais caminhos mínimos.",
    )
    gargalos.add_argument("--topologia", type=Path, required=True)
    gargalos.add_argument("--limite", type=int, default=10)
    gargalos.set_defaults(funcao=executar_gargalos)

    comparar = subparsers.add_parser(
        "comparar",
        help="Compara o mesmo caminho nas duas topologias.",
    )
    comparar.add_argument("--atual", type=Path, required=True)
    comparar.add_argument("--proposta", type=Path, required=True)
    comparar.add_argument("--origem", required=True)
    comparar.add_argument("--destino", required=True)
    comparar.set_defaults(funcao=executar_comparacao)

    return parser


def main() -> int:
    parser = criar_parser()
    args = parser.parse_args()

    try:
        args.funcao(args)
    except (ErroTopologia, KeyError, ValueError) as exc:
        parser.exit(2, f"Erro: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
