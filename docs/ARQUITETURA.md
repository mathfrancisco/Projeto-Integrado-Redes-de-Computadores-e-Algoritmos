# Arquitetura do Projeto

Documento de apoio que explica **como as partes se encaixam** e **o que cada uma faz**.
Para um índice rápido de arquivos, veja a seção "Estrutura do projeto" no
[README](../README.md).

## Visão geral

O projeto resolve um problema de rede com uma ideia central: **representar a rede
como um grafo e usar o algoritmo de Dijkstra** para comparar a infraestrutura
atual com uma proposta melhor.

```
Medição real (ping)          Topologias (JSON)
   medir_rede.py        data/topologia_atual.json
        |               data/topologia_proposta.json
        v                         |
  data/medicoes.csv               v
                            src/grafo.py  (carrega e valida)
                                  |
                                  v
                          src/dijkstra.py  (menor caminho)
                                  |
                                  v
                          src/analise.py  (compara e acha gargalos)
                            /            \
                      main.py        servidor_testes.py
                      (CLI)          (API + relatório HTML)
```

## Camadas

### 1. Dados de entrada

- **`data/topologia_atual.json` / `data/topologia_proposta.json`** — descrevem a
  rede como listas de `nos` (dispositivos) e `arestas` (conexões com
  `latencia_ms`). São a "fonte da verdade" do grafo.
- **`data/medicoes.csv`** — resultados reais de latência/perda, gerados pelo
  `medir_rede.py`. Servem para substituir os valores simulados por medidos.

### 2. Núcleo (pasta `src/`)

- **`grafo.py`** — define `Grafo` (lista de adjacência) e `Aresta`. Faz toda a
  validação: nó duplicado, aresta sem campos, peso negativo, JSON inválido. Se a
  topologia estiver errada, levanta `ErroTopologia` aqui — antes do algoritmo
  rodar.
- **`dijkstra.py`** — implementa Dijkstra com fila de prioridade (`heapq`).
  Retorna um `ResultadoCaminho` com o caminho, o custo total e se é alcançável.
- **`analise.py`** — usa o Dijkstra para duas coisas:
  - `comparar_topologias()` mede a diferença de custo entre atual e proposta;
  - `concentracao_de_rotas()` conta por quais nós passam mais caminhos mínimos,
    revelando **pontos únicos de falha**.

### 3. Interfaces

- **`main.py` (CLI)** — uso por terminal:
  - `caminho` — menor caminho entre origem e destino;
  - `gargalos` — ranking de nós mais usados;
  - `comparar` — atual × proposta para o mesmo trajeto.
- **`scripts/servidor_testes.py`** — servidor HTTP local que serve o relatório
  visual e expõe uma API (`/api/dijkstra`, `/api/comparar`, `/api/ping`,
  `/api/traceroute`, `/api/rede-local`). É o que torna o relatório HTML
  interativo. `validar_host()` impede injeção de comando nos endpoints de ping.
- **`scripts/medir_rede.py`** — utilitário separado que roda `ping`, interpreta a
  saída (Windows/Linux) e acumula medições no CSV.

## Por que Dijkstra

A rede tem latências **não negativas**, então Dijkstra é o algoritmo correto e
eficiente (`O((V+E) log V)`). Pesos negativos são rejeitados na carga do grafo,
justamente porque quebrariam a garantia do algoritmo.

## Decisões de projeto

- **Topologia em JSON, não no código** — trocar a rede é editar um arquivo de
  dados, sem mexer no algoritmo.
- **Validação concentrada em `grafo.py`** — uma única porta de entrada para dados,
  com mensagens de erro claras.
- **Núcleo (`src`) sem dependências de I/O de rede** — fácil de testar; o `ping`
  real fica isolado em `scripts/`.

## Testes

Cada módulo tem testes em `tests/`:

| Arquivo de teste | Cobre |
| --- | --- |
| `test_dijkstra.py` | menor caminho, inalcançável, origem=destino, nós inexistentes, peso negativo. |
| `test_grafo.py` | carga, validações e integridade da topologia. |
| `test_analise.py` | comparação, melhoria percentual e gargalos. |
| `test_medir_rede.py` | interpretação da saída de `ping` (EN/PT/Linux). |
| `test_servidor.py` | validação de host da API. |

Rode com `python -m pytest` a partir da raiz.
