# evidencias/

Coleta de observabilidade usada como evidência no documento da disciplina de Governança
em IA. Gerada contra a API rodando localmente, com o banco limpo antes da coleta.

| Arquivo | Conteúdo |
|---|---|
| `coleta_<data>.csv` | Exportação completa de `sensor_tb_request_processing`, `;` como separador |
| `indicadores_<data>.json` | Resposta de `GET /v1/observabilidade` — indicadores com limiar e veredito |

## Como esta coleta foi produzida

```bash
mysql -u root -proot sensor_db -e "TRUNCATE TABLE sensor_tb_request_processing;"
```

Três sessões simultâneas, 12 rodadas cada (leitura atual + histórico por rodada):

```bash
python scripts/consumir_api.py --rodadas 12 --intervalo 1 --sessao coleta-ui-01
```

Mais uma sessão com tráfego deliberadamente fora do contrato:

```bash
python scripts/consumir_api.py --rodadas 2 --sessao coleta-script-02 --anomalias 4
```

## O que é tráfego real e o que foi injetado

Todas as 94 linhas são chamadas reais, medidas como qualquer outra — nenhum número foi
escrito à mão. O que foi **deliberado** é a composição:

- 4 chamadas **sem os headers de contexto**, que aparecem como sessão `sem-sessao` e
  funcionalidade `desconhecida`. São o que derruba a cobertura de contexto abaixo de 100%.
- 4 chamadas com **tag inexistente** (`M-900`…`M-903`), sessão `anomalia-tag-invalida`,
  que respondem 404 e são o que derruba a taxa de sucesso.

Ambas são identificáveis e podem ser separadas da análise filtrando por sessão. As
demais quebras de limiar — freshness e completude — **não** foram injetadas: vêm da
simulação de falha de coleta do provider (6% de grandeza ausente, 8% de dado atrasado),
que existe justamente para que esses dois indicadores tenham o que medir.

## Limitação desta coleta

A janela inteira cabe em cerca de um minuto, então o gráfico de volume por hora tem uma
barra só. Para evidenciar evolução no tempo, a coleta precisa ser repetida em momentos
diferentes do dia — o schema já suporta, porque agrupa por `started_at`.
