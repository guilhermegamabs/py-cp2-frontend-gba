# db/

Schema do `sensor_db` — MySQL 8. Scripts manuais versionados, nomeados no padrão Flyway
(`V<n>__<descricao>.sql`) para permitir adoção de migration automática depois sem retrabalho.

## Ordem de execução

```bash
mysql -u root -proot < db/V1__schema.sql
```

```bash
mysql -u root -proot < db/V2__seed.sql
```

Conferir:

```bash
mysql -u root -proot sensor_db -e "DESCRIBE sensor_tb_request_processing;"
```

| Script | O que faz | Reexecutável |
|---|---|---|
| `V1__schema.sql` | Cria `sensor_db` e `sensor_tb_request_processing` | Não — `CREATE TABLE` sem `IF NOT EXISTS`, de propósito |
| `V2__seed.sql` | Cinco chamadas de exemplo, só local | Sim — `ON DUPLICATE KEY` |
| `queries/observabilidade.sql` | Catálogo de consultas do relatório | Sim — somente `SELECT` |
| `reset.sql` | **Destrutivo**: dropa o database | — |

## O que é destrutivo

- `reset.sql` apaga o database e com ele todo o histórico de chamadas. Nunca rodar antes de
  extrair as evidências que vão para o documento ABNT da disciplina de Governança.

## Decisões de modelagem

- **`sensor_tb_request_processing` não é append-only.** É a exceção à regra do padrão, e de propósito:
  a linha nasce em `EM_PROCESSAMENTO` com `started_at` quando a requisição entra e é fechada
  com `finished_at`, `http_status` e `latency_ms` quando a resposta sai. Gravar só no fim
  seria mais simples, mas requisição que morre no meio não deixaria rastro nenhum — e é
  justamente essa a falha que a observabilidade existe para enxergar. Linha presa em
  `EM_PROCESSAMENTO` é o sintoma.
- **`latency_ms` é medida, não derivada.** Vem de relógio monotônico na aplicação, não de
  `finished_at - started_at`: ajuste de relógio durante a requisição corromperia a subtração.
- **`started_at` (data do fato) ≠ `created_at` (data do registro).** O relatório agrupa pela
  primeira. Ambas em UTC.
- **`DATETIME(3)`, não `TIMESTAMP`, para o fato.** Precisão de milissegundo e sem conversão
  implícita de fuso pelo servidor; `created_at`/`updated_at` seguem `TIMESTAMP`, preenchidos
  pelo banco.
- **Indicador não é gravado calculado.** Só o insumo bruto por chamada (`freshness_seconds`,
  `completeness_ratio`, `severity`). A agregação vive em um único lugar, o
  `ObservabilityService` — fórmula duplicada faz duas telas mostrarem números diferentes.
- **`VARCHAR` + `CHECK` no lugar de `ENUM`** em `processing_status`: estado novo não exige
  `ALTER TABLE` reescrevendo a tabela.
- **O catálogo de sensores não está no banco.** Ele é dado do provider (leitura de campo),
  não dado da aplicação, e hoje vive em `backend/core/repository/sensor_seed.py`. Quando
  entrar o coletor real, a origem passa a ser o provider — não uma tabela nossa. O que o
  `sensor_db` guarda é só o que a nossa API produz: o processamento das requisições.
