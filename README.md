# Sensor Monitoring API — Observabilidade de um endpoint de IA

Checkpoint integrado das disciplinas de **Front-end** e **Governança em IA**.
Expõe o provider de Sensores do Digital Twin **Forzy** (leitura atual e histórico) como
uma API FastAPI que registra, a cada chamada, o processamento completo da requisição —
e consome essa API numa interface Streamlit via `requests`.

## Integrantes

| RM | Nome |
|---|---|
| _preencher_ | _preencher_ |
| _preencher_ | _preencher_ |

## Arquitetura

Três partes, uma pasta cada:

```
.
├── db/                   scripts SQL versionados do sensor_db (MySQL 8)
├── backend/              API FastAPI
├── frontend/             interface Streamlit
└── scripts/              consumo da API via requests, fora da interface
```

O código segue **pacote por camada** (`package-by-layer`): cada pasta é uma camada, não
uma funcionalidade. O fluxo atravessa as camadas sempre na mesma direção e nada pula
etapa — controller nunca toca repositório, repositório nunca conhece DTO, mapper não
valida nem acessa banco.

### Back-end — `backend/`

```
backend/
├── main.py                           monta a aplicação; único arquivo fora de core/
└── core/
    ├── config/                       settings, conexão MySQL, CORS, injeção
    ├── controller/<recurso>/          rotas; zero regra de negócio, zero try/except
    ├── dto/request/ · dto/response/   contratos de entrada e saída
    ├── enums/                        severidade, grandeza, funcionalidade, status
    ├── exception/                    exceções de domínio + handler global
    ├── mapper/                       domínio → DTO; não valida, não acessa banco
    ├── model/                        modelos de domínio, limiares, catálogo de indicadores
    ├── observability/                middleware e contexto da chamada (transversal)
    ├── repository/                   acesso a dado: provider de sensores e MySQL
    └── service/                      regra de negócio e agregação dos indicadores
```

**Fluxo de uma requisição**

```
HTTP → ObservabilityMiddleware → Controller → Service → Repository
                   ↓                                        ↓
       abre a linha em                            enriquece a linha com
       sensor_tb_request_processing               freshness/completude/severidade
                   ↓
       fecha a linha com status, fim e latência
```

O middleware é o único ponto que grava o contrato mínimo de observabilidade. Deixar isso
a cargo de cada controller garantiria que um endpoint novo nascesse sem instrumentação.

### Front-end — `frontend/`

```
frontend/
├── app.py                 navegação; nenhuma chamada HTTP
└── core/
    ├── config/            URL da API, timeout, cores
    ├── types/             espelho dos DTOs do back-end + ApiError
    ├── enums/             valores aceitos em X-Feature
    ├── api/               requests + normalização de erro; uma função por endpoint
    ├── service/           sessão do usuário e formatação
    └── view/              uma tela por arquivo + componentes compartilhados
```

Camadas fixas: `types` → `api` → `service` → `view`. Nenhuma tela importa `requests`, e a
camada `api/` não conhece Streamlit.

### Banco — `db/`

MySQL 8, database `sensor_db`, tabela `sensor_tb_request_processing`. Scripts versionados e
nomeados no padrão Flyway. Decisões de modelagem em [`db/README.md`](db/README.md).

## Como rodar localmente

### 1. Pré-requisitos

- Python 3.11+
- MySQL 8 no `localhost:3306`

### 2. Dependências

```bash
pip install -r backend/requirements.txt -r frontend/requirements.txt
```

| Pacote | Para quê |
|---|---|
| `fastapi` + `uvicorn` | API e servidor ASGI |
| `PyMySQL` | driver MySQL puro Python — não exige compilador no Windows |
| `streamlit` | interface |
| `requests` | consumo da API (exigência da disciplina) |
| `pandas` | tabelas e séries da interface |

### 3. Banco

```bash
mysql -u root -proot < db/V1__schema.sql
```

Opcional, só em ambiente local, para a interface não abrir vazia:

```bash
mysql -u root -proot < db/V2__seed.sql
```

### 4. API

```bash
cd backend && python -m uvicorn main:app --reload --port 8000
```

Documentação interativa em `http://localhost:8000/docs`.

### 5. Interface

```bash
cd frontend && python -m streamlit run app.py
```

Abre em `http://localhost:8501`.

### 6. Consumo via `requests`, fora da interface

```bash
python scripts/consumir_api.py --rodadas 20 --sessao coleta-01
```

Percorre os três endpoints e imprime os indicadores. Com `--rodadas` alto, serve para
gerar o tráfego que embasa o documento da disciplina de Governança — o relatório só tem
o que mostrar depois que houve chamada de verdade.

## Endpoints

| Funcionalidade | Endpoint | Consumo no front |
|---|---|---|
| Ativos | `GET /v1/sensores` | Preenche o seletor de ativo |
| Leitura atual | `GET /v1/sensores/{tag}/leitura-atual` | Exibe a leitura e a severidade |
| Histórico | `GET /v1/sensores/{tag}/historico` | Gráfico de linha e tabela da série |
| Observabilidade | `GET /v1/observabilidade` | Indicadores e registros de chamadas |
| Contrato | `GET /v1/observabilidade/contrato` | Limiar, gráfico sugerido e ação de estouro |
| Healthcheck | `GET /saude` | — (fora do relatório) |

Toda chamada do front envia os headers de contexto **`X-Session-Id`** e **`X-Feature`**, e
recebe de volta **`X-Call-Id`**, que correlaciona a chamada com a linha do relatório.

## Contrato de observabilidade

Cada chamada recebida gera uma linha em `sensor_tb_request_processing` com:

| Grupo | Campos |
|---|---|
| Contexto | `session_id`, `feature`, `method`, `path`, `tag` |
| Processamento | `processing_status`, `http_status`, `started_at`, `finished_at`, `latency_ms` |
| Domínio | `severity`, `freshness_seconds`, `completeness_ratio`, `points` |
| Falha | `error_message` |

Os indicadores agregados — e, para cada um, o limiar, a camada gráfica recomendada e a
ação quando o limiar estoura — vivem em `backend/core/model/indicator.py` e são expostos
por `GET /v1/observabilidade/contrato`. Ficam no código, e não só no documento, porque
limiar que existe apenas no documento envelhece sem ninguém perceber.

| Indicador | Limiar padrão | Camada gráfica |
|---|---|---|
| Volume de chamadas | ≥ 1 | Barra por hora |
| Latência média | ≤ 500 ms | Linha com banda do limiar |
| Latência p95 | ≤ 500 ms | Linha sobreposta à da média |
| Taxa de sucesso | ≥ 99% | Linha com área de erro por status |
| Freshness médio | ≤ 120 s | Linha temporal da idade do dado |
| Taxa de completude de freshness | ≥ 80% | Linha de evolução da taxa |
| Cobertura dos headers de contexto | = 100% | Barra por funcionalidade |

Os limiares são variáveis de ambiente (ver [`.env.example`](.env.example)): recalibrar o
baseline não exige mexer em código.

## Escopo

**Abordado**: provider de Sensores (leitura atual e histórico), headers de contexto,
registro do processamento no MySQL, endpoint de observabilidade, consumo via `requests` e
interface Streamlit.

**Fora do escopo**, por definição do checkpoint: autenticação e autorização; migração dos
providers de Equipamentos e Plantas. Ambos ficam para a Sprint 4 final da disciplina.

## Uso de IA

O desenvolvimento usou assistente de IA para escrever código a partir dos padrões já
adotados pelo grupo. Decisões de modelagem, escolha dos indicadores e definição dos
limiares foram revisadas e validadas pelos integrantes.
