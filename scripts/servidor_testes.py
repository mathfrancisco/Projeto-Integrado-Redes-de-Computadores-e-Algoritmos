from __future__ import annotations

import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.analise import comparar_topologias
from src.dijkstra import menor_caminho
from src.grafo import Grafo


HOST_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,253}$")


def carregar_json(caminho: Path) -> dict[str, object]:
    return json.loads(caminho.read_text(encoding="utf-8"))


def executar_comando(comando: list[str], timeout: int = 15) -> dict[str, object]:
    try:
        processo = subprocess.run(
            comando,
            cwd=RAIZ,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "codigo": None,
            "saida": exc.stdout or "",
            "erro": "Tempo limite excedido.",
        }
    except OSError as exc:
        return {
            "ok": False,
            "codigo": None,
            "saida": "",
            "erro": str(exc),
        }

    saida = processo.stdout or processo.stderr
    return {
        "ok": processo.returncode == 0,
        "codigo": processo.returncode,
        "saida": saida,
        "erro": "",
    }


def validar_host(host: str) -> str:
    host = host.strip()
    if not HOST_RE.fullmatch(host):
        raise ValueError("Host invalido.")
    return host


class Handler(BaseHTTPRequestHandler):
    server_version = "ServidorTestesRede/1.0"

    def log_message(self, formato: str, *args: object) -> None:
        print(f"{self.address_string()} - {formato % args}")

    def enviar_json(self, dados: dict[str, object], status: int = 200) -> None:
        corpo = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def enviar_arquivo(self, caminho: Path, content_type: str) -> None:
        if not caminho.is_file():
            self.send_error(404, "Arquivo nao encontrado")
            return

        corpo = caminho.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def ler_json(self) -> dict[str, object]:
        tamanho = int(self.headers.get("Content-Length", "0"))
        if tamanho == 0:
            return {}
        return json.loads(self.rfile.read(tamanho).decode("utf-8"))

    def do_GET(self) -> None:
        url = urlparse(self.path)

        if url.path in {"/", "/relatorio_visual.html"}:
            self.enviar_arquivo(RAIZ / "docs" / "relatorio_visual.html", "text/html; charset=utf-8")
            return

        if url.path == "/api/rede-local":
            self.enviar_json(executar_comando(["ipconfig", "/all"], timeout=10))
            return

        if url.path == "/api/topologias":
            try:
                atual = carregar_json(RAIZ / "data" / "topologia_atual.json")
                proposta = carregar_json(RAIZ / "data" / "topologia_proposta.json")
            except Exception as exc:
                self.enviar_json({"ok": False, "erro": str(exc)}, status=400)
                return

            self.enviar_json(
                {
                    "ok": True,
                    "atual": atual,
                    "proposta": proposta,
                }
            )
            return

        if url.path == "/api/dijkstra":
            parametros = parse_qs(url.query)
            topologia = parametros.get("topologia", ["proposta"])[0]
            origem = parametros.get("origem", ["DEV1"])[0]
            destino = parametros.get("destino", ["CLOUD"])[0]
            arquivo = "topologia_proposta.json" if topologia == "proposta" else "topologia_atual.json"

            try:
                grafo = Grafo.de_json(RAIZ / "data" / arquivo)
                resultado = menor_caminho(grafo, origem, destino)
            except Exception as exc:
                self.enviar_json({"ok": False, "erro": str(exc)}, status=400)
                return

            self.enviar_json(
                {
                    "ok": True,
                    "topologia": grafo.nome,
                    "origem": resultado.origem,
                    "destino": resultado.destino,
                    "caminho": list(resultado.caminho),
                    "custo_total_ms": resultado.custo_total_ms,
                }
            )
            return

        if url.path == "/api/comparar":
            try:
                atual = Grafo.de_json(RAIZ / "data" / "topologia_atual.json")
                proposta = Grafo.de_json(RAIZ / "data" / "topologia_proposta.json")
                resultado = comparar_topologias(atual, proposta, "DEV1", "CLOUD")
            except Exception as exc:
                self.enviar_json({"ok": False, "erro": str(exc)}, status=400)
                return

            self.enviar_json(
                {
                    "ok": True,
                    "caminho_atual": list(resultado.caminho_atual),
                    "caminho_proposto": list(resultado.caminho_proposto),
                    "custo_atual_ms": resultado.custo_atual_ms,
                    "custo_proposto_ms": resultado.custo_proposto_ms,
                    "diferenca_ms": resultado.diferenca_ms,
                    "melhoria_percentual": resultado.melhoria_percentual,
                }
            )
            return

        self.send_error(404, "Rota nao encontrada")

    def do_POST(self) -> None:
        url = urlparse(self.path)

        try:
            dados = self.ler_json()
            host = validar_host(str(dados.get("host", "")))
        except Exception as exc:
            self.enviar_json({"ok": False, "erro": str(exc)}, status=400)
            return

        if url.path == "/api/ping":
            self.enviar_json(executar_comando(["ping", "-n", "4", host], timeout=20))
            return

        if url.path == "/api/traceroute":
            self.enviar_json(executar_comando(["tracert", "-d", "-h", "10", host], timeout=30))
            return

        self.send_error(404, "Rota nao encontrada")


def main() -> int:
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", porta), Handler)
    except OSError as exc:
        print(f"Nao foi possivel iniciar na porta {porta}: {exc}")
        print("Tente fechar o servidor antigo com Ctrl+C ou use outra porta:")
        print("python scripts/servidor_testes.py 8001")
        return 1

    print(f"Servidor iniciado em http://127.0.0.1:{porta}")
    print("Pressione Ctrl+C para parar.")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
