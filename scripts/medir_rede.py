"""Mede latência e perda de pacotes com ping e grava o resultado em CSV.

O script roda o ``ping`` do sistema operacional, interpreta a saída (Windows ou
Linux) e extrai pacotes enviados/recebidos, perda (%) e latências min/média/máx.
Cada execução vira uma linha em ``data/medicoes.csv``.
"""

from __future__ import annotations

import argparse
import csv
import platform
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Medicao:
    data_hora: str
    nome: str
    host: str
    origem: str
    destino: str
    pacotes_enviados: int | None
    pacotes_recebidos: int | None
    perda_percentual: float | None
    latencia_min_ms: float | None
    latencia_media_ms: float | None
    latencia_max_ms: float | None
    status: str


CAMPOS = list(Medicao.__dataclass_fields__.keys())


def _nova_medicao(
    *,
    nome: str,
    host: str,
    origem: str,
    destino: str,
    status: str,
    **valores: object,
) -> Medicao:
    """Cria uma ``Medicao`` com todos os campos numéricos em None por padrão.

    Evita repetir o preenchimento manual de None em cada caminho de erro.
    """

    base: dict[str, object] = dict(
        data_hora=datetime.now().isoformat(timespec="seconds"),
        nome=nome,
        host=host,
        origem=origem,
        destino=destino,
        pacotes_enviados=None,
        pacotes_recebidos=None,
        perda_percentual=None,
        latencia_min_ms=None,
        latencia_media_ms=None,
        latencia_max_ms=None,
        status=status,
    )
    base.update(valores)
    return Medicao(**base)  # type: ignore[arg-type]


def converter_numero(valor: str) -> float:
    """Converte '12,5' ou '12.5' em float, aceitando vírgula decimal."""

    return float(valor.replace(",", "."))


def interpretar_windows(
    saida: str,
) -> tuple[int | None, int | None, float | None, float | None, float | None, float | None]:
    """Extrai (enviados, recebidos, perda, min, médio, máx) do ping do Windows.

    Aceita saída em inglês e português. Campos não encontrados voltam como None.
    """

    enviados = recebidos = None
    perda = minimo = medio = maximo = None

    resumo = re.search(
        r"(?:Sent|Enviados)\s*=\s*(\d+).*?"
        r"(?:Received|Recebidos)\s*=\s*(\d+).*?"
        r"\((\d+(?:[.,]\d+)?)%\s*(?:loss|de\s+perda)\)",
        saida,
        re.IGNORECASE | re.DOTALL,
    )

    if resumo:
        enviados = int(resumo.group(1))
        recebidos = int(resumo.group(2))
        perda = converter_numero(resumo.group(3))

    tempos = re.search(
        r"(?:Minimum|Mínimo)\s*=\s*(\d+)\s*ms.*?"
        r"(?:Maximum|Máximo)\s*=\s*(\d+)\s*ms.*?"
        r"(?:Average|Média)\s*=\s*(\d+)\s*ms",
        saida,
        re.IGNORECASE | re.DOTALL,
    )

    if tempos:
        minimo = converter_numero(tempos.group(1))
        maximo = converter_numero(tempos.group(2))
        medio = converter_numero(tempos.group(3))

    return enviados, recebidos, perda, minimo, medio, maximo


def interpretar_linux(
    saida: str,
) -> tuple[int | None, int | None, float | None, float | None, float | None, float | None]:
    """Extrai (enviados, recebidos, perda, min, médio, máx) do ping do Linux/macOS.

    Lê a linha 'packets transmitted' e a linha 'rtt min/avg/max'. None se ausente.
    """

    enviados = recebidos = None
    perda = minimo = medio = maximo = None

    resumo = re.search(
        r"(\d+)\s+packets transmitted,\s+"
        r"(\d+)\s+(?:packets )?received.*?"
        r"(\d+(?:[.,]\d+)?)%\s+packet loss",
        saida,
        re.IGNORECASE | re.DOTALL,
    )

    if resumo:
        enviados = int(resumo.group(1))
        recebidos = int(resumo.group(2))
        perda = converter_numero(resumo.group(3))

    tempos = re.search(
        r"(?:rtt|round-trip).*?=\s*"
        r"(\d+(?:[.,]\d+)?)/"
        r"(\d+(?:[.,]\d+)?)/"
        r"(\d+(?:[.,]\d+)?)/",
        saida,
        re.IGNORECASE,
    )

    if tempos:
        minimo = converter_numero(tempos.group(1))
        medio = converter_numero(tempos.group(2))
        maximo = converter_numero(tempos.group(3))

    return enviados, recebidos, perda, minimo, medio, maximo


def _decodificar(dados: bytes) -> str:
    """Decodifica a saída do ping respeitando o codepage do console.

    No Windows o ping usa o codepage OEM (ex.: cp850 em PT-BR), não UTF-8;
    decodificar como UTF-8 corromperia acentos e quebraria os regex.
    """

    if not dados:
        return ""

    if platform.system().lower() == "windows":
        try:
            import ctypes

            codepage = f"cp{ctypes.windll.kernel32.GetOEMCP()}"  # type: ignore[attr-defined]
            return dados.decode(codepage, errors="replace")
        except Exception:
            return dados.decode("latin-1", errors="replace")

    return dados.decode("utf-8", errors="replace")


def executar_ping(host: str, pacotes: int) -> tuple[int, str]:
    sistema = platform.system().lower()

    if sistema == "windows":
        comando = ["ping", "-n", str(pacotes), host]
    else:
        comando = ["ping", "-c", str(pacotes), host]

    processo = subprocess.run(
        comando,
        capture_output=True,
        timeout=max(30, pacotes * 3),
        check=False,
    )

    saida = f"{_decodificar(processo.stdout)}\n{_decodificar(processo.stderr)}"
    return processo.returncode, saida


def medir(
    *,
    nome: str,
    host: str,
    origem: str,
    destino: str,
    pacotes: int,
) -> Medicao:
    dados = dict(nome=nome, host=host, origem=origem, destino=destino)

    try:
        retorno, saida = executar_ping(host, pacotes)
    except FileNotFoundError:
        return _nova_medicao(**dados, status="PING_NAO_ENCONTRADO")
    except subprocess.TimeoutExpired:
        return _nova_medicao(**dados, status="TIMEOUT", pacotes_enviados=pacotes)

    if platform.system().lower() == "windows":
        valores = interpretar_windows(saida)
    else:
        valores = interpretar_linux(saida)

    enviados, recebidos, perda, minimo, medio, maximo = valores
    interpretado = enviados is not None and recebidos is not None

    return _nova_medicao(
        **dados,
        status="OK" if retorno == 0 and interpretado else "REVISAR",
        pacotes_enviados=enviados,
        pacotes_recebidos=recebidos,
        perda_percentual=perda,
        latencia_min_ms=minimo,
        latencia_media_ms=medio,
        latencia_max_ms=maximo,
    )


def salvar_csv(medicao: Medicao, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    arquivo_existe = caminho.exists() and caminho.stat().st_size > 0

    with caminho.open("a", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=CAMPOS,
            delimiter=";",
        )

        if not arquivo_existe:
            writer.writeheader()

        writer.writerow(asdict(medicao))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mede latência e perda e salva o resultado em CSV."
    )
    parser.add_argument("--host", required=True)
    parser.add_argument("--nome", required=True)
    parser.add_argument("--origem", required=True)
    parser.add_argument("--destino", required=True)
    parser.add_argument("--pacotes", type=int, default=20)
    parser.add_argument(
        "--saida",
        type=Path,
        default=Path("data/medicoes.csv"),
    )
    args = parser.parse_args()

    if args.pacotes <= 0:
        parser.error("--pacotes deve ser maior que zero.")

    resultado = medir(
        nome=args.nome,
        host=args.host,
        origem=args.origem,
        destino=args.destino,
        pacotes=args.pacotes,
    )

    salvar_csv(resultado, args.saida)

    print(f"Status: {resultado.status}")
    print(f"Perda: {resultado.perda_percentual}%")
    print(f"Latência média: {resultado.latencia_media_ms} ms")
    print(f"Arquivo: {args.saida}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
