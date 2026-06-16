# Guia de testes pelo HTML

Este projeto nao depende de simulador externo. A validacao e feita por uma pagina
HTML servida por Python.

## 1. Iniciar o servidor

No terminal, dentro da pasta do projeto:

```bash
python scripts/servidor_testes.py
```

Abra no navegador:

```text
http://127.0.0.1:8000
```

Se a porta estiver ocupada:

```bash
python scripts/servidor_testes.py 8001
```

Abra:

```text
http://127.0.0.1:8001
```

## 2. Resumo

Mostra os principais indicadores do projeto:

- custo da rota na topologia atual;
- custo da rota na topologia proposta;
- melhoria percentual estimada;
- quantidade de VLANs propostas.

Esses valores ajudam a explicar rapidamente se a proposta melhora a rede.

## 3. Topologias

Mostra os dispositivos e conexoes carregados dos arquivos:

- `data/topologia_atual.json`;
- `data/topologia_proposta.json`.

Cada linha representa uma conexao e cada numero em `ms` representa a latencia
usada pelo algoritmo.

## 4. VLANs

Mostra a segmentacao proposta da rede:

- VLAN 10: Administracao;
- VLAN 20: Desenvolvimento;
- VLAN 30: Servidores;
- VLAN 40: IoT;
- VLAN 50: Visitantes;
- VLAN 99: Gerenciamento.

A separacao por VLAN reduz acesso indevido entre setores e organiza melhor a
infraestrutura.

## 5. Matriz de testes

Mostra o que deve ser permitido ou bloqueado. Exemplos:

- Administracao acessa servidores: permitido;
- visitantes acessam servidores internos: bloqueado;
- visitantes acessam servicos externos: permitido;
- IoT acessa apenas servicos autorizados: permitido.

## 6. Testes interativos

Os botoes da pagina executam testes reais:

- `Executar Dijkstra`: calcula o menor caminho entre origem e destino.
- `Comparar topologias`: compara atual e proposta.
- `Ping`: testa conectividade com um host ou IP.
- `Tracert`: mostra o caminho de rede ate o destino.
- `Ver minha rede`: mostra a configuracao local da maquina com `ipconfig /all`.

Para testar a rede local, clique em `Ver minha rede`, copie o gateway padrao e
use esse IP no campo `Host ou IP`.
