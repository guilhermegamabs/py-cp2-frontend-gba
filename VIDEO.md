# Roteiro do vídeo

Vídeo simples, de base, exigido pelo checkpoint: serve para o avaliador ver o projeto
funcionando caso ele não suba na máquina de avaliação. Não é apresentação — é prova de
execução.

**Alvo: 4 a 6 minutos.** Gravar a tela inteira com áudio. OBS Studio, Xbox Game Bar
(`Win+G`) ou a própria gravação do Teams servem.

## Antes de gravar

Deixar tudo pronto e **fechar** o que não entra no vídeo. Checklist:

```bash
python db/aplicar_schema.py
```

```bash
cd backend && python -m uvicorn main:app --reload --port 8000
```

```bash
cd frontend && python -m streamlit run app.py
```

- Banco **vazio** antes de começar (`TRUNCATE TABLE sensor_tb_request_processing`). O
  relatório precisa começar zerado para que as chamadas feitas no vídeo apareçam nascendo.
- Três terminais abertos e posicionados: API, interface, script.
- Navegador em `http://localhost:8501`, aba única, zoom em 100%.
- Fechar Discord, WhatsApp, notificação de e-mail.

## Blocos

### 1 — Abertura (20 s)

Dizer, sem ler slide: nome dos integrantes, disciplina, e o que o projeto é em uma frase —
*"API FastAPI que expõe o provider de Sensores do Digital Twin Forzy e registra a
observabilidade de cada chamada, consumida por uma interface Streamlit"*.

### 2 — Estrutura do repositório (40 s)

Mostrar a árvore de pastas no editor. Dizer o que cada uma é, sem abrir arquivo:

- `db/` — schema versionado do MySQL
- `backend/` — API, organizada por camada
- `frontend/` — interface
- `scripts/` — consumo via `requests`, fora da interface
- `evidencias/` — a coleta que embasa o documento de Governança

Abrir **um** arquivo só: `backend/core/observability/observability_middleware.py`. É o
ponto que justifica o projeto. Dizer em voz alta: *"é aqui que toda chamada vira registro —
um lugar só, para que endpoint novo já nasça instrumentado"*.

### 3 — API no ar (50 s)

Mostrar o terminal da API subindo, com a linha de log confirmando conexão ao MySQL.

Abrir `http://localhost:8000/docs`. Executar **pelo Swagger**:

1. `GET /v1/sensores` — lista dos sete ativos.
2. `GET /v1/sensores/{tag}/leitura-atual` com `M-202` — apontar a severidade `crit`.
3. `GET /v1/sensores/{tag}/leitura-atual` com `M-999` — mostrar o 404 com corpo padronizado.

Na resposta da primeira chamada, abrir os *response headers* e **apontar o `X-Call-Id`**.
Dizer que é o que liga a chamada à linha do relatório.

### 4 — Interface (2 min)

Ir para `http://localhost:8501`.

**Leitura atual** — selecionar `M-202`, consultar. Apontar severidade, completude e
freshness. Se alguma grandeza vier vazia, parar nela: *"a coleta falhou nesta grandeza, e é
isso que derruba a taxa de completude — o front mostra como ausência, não como zero"*.

**Histórico** — janela de 24 h, intervalo de 60 min. Mostrar os gráficos de linha e abrir a
tabela da série.

**Observabilidade** — a tela que importa. Nesta ordem:

1. Os sete indicadores, com limiar e veredito. Apontar pelo menos um **estourado** e dizer
   por quê.
2. Os gráficos de chamadas por funcionalidade e por sessão.
3. A tabela de registros — mostrar que as chamadas feitas nos blocos anteriores estão lá.
4. A linha em `EM_PROCESSAMENTO`: é a consulta do próprio relatório, que só fecha depois
   que a resposta sai.
5. Abrir o expander **Contrato de observabilidade** e ler **um** indicador por inteiro:
   limiar, camada gráfica sugerida e ação ao estourar. Dizer que vem de
   `GET /v1/observabilidade/contrato`, ou seja, do código — não de um documento à parte.

### 5 — Consumo via `requests` (50 s)

Terminal:

```bash
python scripts/consumir_api.py --rodadas 5 --intervalo 1 --sessao demo-video --anomalias 2
```

Enquanto roda, dizer que isto é o consumo exigido pela disciplina, feito fora da interface.
Quando terminar, apontar no resumo os indicadores **estourados** e explicar que as
anomalias foram injetadas de propósito — chamadas sem header de contexto e com tag
inexistente — para que cobertura de contexto e taxa de sucesso tenham o que medir.

Voltar à tela de Observabilidade, recarregar, e mostrar o volume subindo e a sessão
`demo-video` aparecendo no gráfico por sessão.

### 6 — Fechamento (20 s)

Dizer o que ficou **fora** do escopo por definição do checkpoint: autenticação e migração
dos providers de Equipamentos e Plantas, ambos na Sprint 4 final. Mostrar o repositório no
GitHub.

## Erros que estragam a gravação

- Começar com o banco cheio: ninguém vê registro nascendo.
- Narrar código linha a linha. Mostrar funcionando vale mais.
- Esquecer de apontar o `X-Call-Id` — é o elo entre as duas disciplinas.
- Mostrar só indicador conforme. O estouro é o que prova que a medição funciona.
- Áudio do sistema mudo ou microfone no lugar errado: gravar 15 s de teste antes.

## Depois de gravar

Subir no YouTube como **não listado**, ou no Drive com link aberto para quem tem o link.
Colar a URL no `README.md`, no lugar de `_preencher_`, e commitar.
