# governanca/

Entrega da disciplina de **Governança em IA**. É uma entrega separada da do Front-end:
vai no Teams da disciplina, não é avaliada pelo repositório. Fica versionada aqui porque o
documento depende das evidências em [`../evidencias/`](../evidencias/) e dos limiares
declarados em `backend/core/model/indicator.py` — separar os dois faria o documento
envelhecer sem aviso.

| Arquivo | O que é |
|---|---|
| `Governanca_IA_Observabilidade_Sensor_Monitoring_API.pdf` | **Documento final entregue**, em ABNT, com a conclusão escrita pelo grupo |
| `gerar_documento.py` | Gera o esqueleto do documento em `.docx`, para refazer a estrutura sem reformatar à mão |

## O documento final

O PDF é a versão entregue: 25 páginas, com capa, folha de rosto, resumo, lista de quadros,
lista de siglas, sumário paginado, dez seções numeradas e referências.

A conclusão (seção 9) e a declaração de uso de IA (seção 10) foram escritas pelos
integrantes. O sumário é uma página estática, com os números de página conferidos contra o
PDF renderizado — não é campo do Word e não precisa de atualização.

## Para refazer a estrutura

```bash
pip install python-docx
```

```bash
python governanca/gerar_documento.py
```

Gera um `.docx` novo a partir do código. **Atenção**: o script reconstrói o arquivo do
zero, então o resultado **não** contém a conclusão escrita pelo grupo nem o sumário
paginado — serve para refazer a formatação base, não para regerar a entrega. O documento
entregue é o PDF acima.

## De onde vêm os números

Todos os valores da seção 8 saem de [`../evidencias/`](../evidencias/), que é a coleta de
5 de outubro de 2026 — 95 chamadas reais medidas pelo próprio middleware, sem nenhum
número escrito à mão. Os limiares da seção 5 são os mesmos que a API aplica, declarados em
`.env.example` e expostos por `GET /v1/observabilidade/contrato`.

Se a coleta for refeita, os números do documento mudam e as seções 5.2, 8.2 e 8.3 precisam
ser atualizadas junto.
