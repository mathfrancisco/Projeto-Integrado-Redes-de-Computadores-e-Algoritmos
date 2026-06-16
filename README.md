# Diagnóstico e Melhoria da Rede Corporativa

Projeto Integrado de **Redes de Computadores e Algoritmos**, desenvolvido para a **MF Tecnologia e Sistemas**.

## Objetivo

Analisar a infraestrutura de rede atual da empresa, identificar riscos, gargalos e pontos únicos de falha e propor uma arquitetura mais segura, segmentada e resiliente.

A rede será representada como um grafo:

* dispositivos serão os nós;
* conexões serão as arestas;
* a latência será o peso das arestas;
* o algoritmo de Dijkstra será usado para encontrar caminhos de menor latência.

A solução proposta será validada pelo **relatório visual em HTML**, executado por
um servidor local Python. A página permite testar o algoritmo de Dijkstra,
comparar topologias e executar testes de conectividade da máquina.

## Etapas

1. Inventariar os dispositivos.
2. Medir latência e perda de pacotes.
3. Desenhar a topologia atual.
4. Modelar a rede como grafo.
5. Executar o algoritmo de Dijkstra.
6. Identificar gargalos e pontos críticos.
7. Criar uma nova arquitetura com VLANs, regras de acesso, firewall e VPN.
8. Testar a proposta pelo relatório HTML interativo.
9. Comparar a rede atual com a rede proposta.

## Arquitetura proposta

| VLAN | Setor           | Rede              |
| ---: | --------------- | ----------------- |
|   10 | Administração   | `192.168.10.0/24` |
|   20 | Desenvolvimento | `192.168.20.0/24` |
|   30 | Servidores      | `192.168.30.0/24` |
|   40 | IoT             | `192.168.40.0/24` |
|   50 | Visitantes      | `192.168.50.0/24` |
|   99 | Gerenciamento   | `192.168.99.0/24` |

## Funcionamento geral

```mermaid
flowchart LR
    A[Inventário da rede] --> B[Medições de latência e perda]
    B --> C[Topologia atual]
    C --> D[Modelagem em grafo]
    D --> E[Algoritmo de Dijkstra]
    E --> F[Identificação de caminhos e pontos críticos]
    F --> G[Projeto da nova arquitetura]
    G --> H[Relatório HTML interativo]
    H --> I[Testes de algoritmo e conectividade]
    I --> J[Comparação e conclusão]
```

## Como testar

Para usar o relatório visual dinâmico com botões de teste, execute:

```bash
python scripts/servidor_testes.py
```

Depois abra `http://127.0.0.1:8000` no navegador.

Se a porta `8000` ja estiver ocupada, use outra porta:

```bash
python scripts/servidor_testes.py 8001
```

Depois abra `http://127.0.0.1:8001`.

O relatório carrega automaticamente os arquivos `data/topologia_atual.json` e
`data/topologia_proposta.json`, preenche as opções de origem/destino e permite
testar Dijkstra, comparação entre topologias, ping, traceroute e dados da rede
local da máquina.

## Documentação

* [Relatório visual em HTML](docs/relatorio_visual.html)
* [Guia de testes pelo HTML](docs/guia_testes_html.md)
* [Topologia atual](docs/topologia_atual.mmd)
* [Topologia proposta](docs/topologia_proposta.mmd)
* [Funcionamento da rede proposta](docs/funcionamento_rede_proposta.mmd)
* [Fluxograma do Dijkstra](docs/fluxograma_dijkstra.mmd)
* [Visão geral do projeto](docs/visao_geral_projeto.mmd)

## ODS

O projeto está relacionado ao **ODS 9 — Indústria, Inovação e Infraestrutura**, por propor melhoria da infraestrutura tecnológica, da segurança e da disponibilidade dos serviços.

## Observação

Os endereços, equipamentos e valores apresentados inicialmente são uma proposta de laboratório. Antes da entrega, deverão ser ajustados conforme o inventário e as medições reais da empresa.
