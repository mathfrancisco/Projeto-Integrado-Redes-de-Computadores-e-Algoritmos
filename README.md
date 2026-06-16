# Diagnóstico e Melhoria da Rede Corporativa

Projeto Integrado de **Redes de Computadores e Algoritmos**, desenvolvido para a **MF Tecnologia e Sistemas**.

## Objetivo

Analisar a infraestrutura de rede atual da empresa, identificar riscos, gargalos e pontos únicos de falha e propor uma arquitetura mais segura, segmentada e resiliente.

A rede será representada como um grafo:

* dispositivos serão os nós;
* conexões serão as arestas;
* a latência será o peso das arestas;
* o algoritmo de Dijkstra será usado para encontrar caminhos de menor latência.

A solução proposta será validada no **Cisco Packet Tracer**.

## Etapas

1. Inventariar os dispositivos.
2. Medir latência e perda de pacotes.
3. Desenhar a topologia atual.
4. Modelar a rede como grafo.
5. Executar o algoritmo de Dijkstra.
6. Identificar gargalos e pontos críticos.
7. Criar uma nova arquitetura com VLANs, ACLs, firewall e VPN.
8. Simular e testar a proposta no Cisco Packet Tracer.
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
    G --> H[Simulação no Packet Tracer]
    H --> I[Testes de conectividade e segurança]
    I --> J[Comparação e conclusão]
```

## Documentação

* [Planejamento](docs/PLANEJAMENTO.md)
* [Metodologia](docs/METODOLOGIA.md)
* [Pseudocódigo](docs/PSEUDOCODIGO.md)
* [Plano de endereçamento](docs/PLANO_ENDERECAMENTO.md)
* [Regras de firewall](docs/REGRAS_FIREWALL.md)
* [Diagramas Mermaid](docs/diagramas)

## ODS

O projeto está relacionado ao **ODS 9 — Indústria, Inovação e Infraestrutura**, por propor melhoria da infraestrutura tecnológica, da segurança e da disponibilidade dos serviços.

## Observação

Os endereços, equipamentos e valores apresentados inicialmente são uma proposta de laboratório. Antes da entrega, deverão ser ajustados conforme o inventário e as medições reais da empresa.
