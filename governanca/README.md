# governanca/

Entrega da disciplina de **Governança em IA**. É uma entrega separada da do Front-end:
vai no Teams da disciplina, não é avaliada pelo repositório. Fica versionada aqui porque o
documento depende das evidências em [`../evidencias/`](../evidencias/) e dos limiares
declarados em `backend/core/model/indicator.py` — separar os dois faria o documento
envelhecer sem aviso.

| Arquivo | O que é |
|---|---|
| `Governanca_IA_Observabilidade_Sensor_Monitoring_API.docx` | Documento final, formatado em ABNT |
| `gerar_documento.py` | Gera o `.docx` acima a partir do código, para refazer sem reformatar à mão |

## O que falta preencher antes de entregar

O documento está completo em conteúdo e formatação, e tem **três lacunas deliberadas**.
Todas aparecem no texto entre colchetes e em negrito.

1. **Capa e folha de rosto** — RM e nome completo de cada integrante, e o nome do
   professor orientador. Estão como `[RM00000] [Nome completo do integrante N]`.
2. **Seção 9, Conclusão** — tem de ser escrita pelo grupo, **sem IA**. O critério de
   avaliação exige as palavras e percepções dos integrantes e vale 3,0 pontos. No lugar do
   texto há um bloco de perguntas para orientar a escrita; apagar o bloco inteiro depois.
3. **Seção 10, Uso de IA** — a declaração está redigida, mas precisa ser conferida e
   ajustada ao que o grupo efetivamente fez. Declaração falsa é pior que declaração
   ausente.

## Ao abrir o arquivo pela primeira vez

O sumário é um campo do Word, não uma lista digitada — ele se preenche sozinho com os
números de página corretos. Se abrir vazio, selecionar tudo com `Ctrl+A` e apertar `F9`.
Depois apagar o aviso em itálico logo abaixo do sumário.

Conferir também, no Word, antes de entregar: o número de página deve aparecer no canto
superior direito **a partir da Introdução**, e a contagem deve começar na folha de rosto
(a capa não é contada). É o que a NBR 14724 pede.

## Para refazer o documento

```bash
pip install python-docx
```

```bash
python governanca/gerar_documento.py
```

Sobrescreve o `.docx`. **Atenção**: regerar apaga a conclusão escrita pelo grupo e os
nomes preenchidos, porque o script reconstrói o arquivo do zero. Depois que o documento
começar a ser editado no Word, editar no Word — o script serve para refazer a estrutura,
não para manter o texto final.

## De onde vêm os números

Todos os valores da seção 8 saem de [`../evidencias/`](../evidencias/), que é a coleta de
5 de outubro de 2026 — 95 chamadas reais medidas pelo próprio middleware, sem nenhum
número escrito à mão. Os limiares da seção 5 são os mesmos que a API aplica, declarados em
`.env.example` e expostos por `GET /v1/observabilidade/contrato`.

Se a coleta for refeita, os números do documento mudam e as seções 5.2, 8.2 e 8.3 precisam
ser atualizadas junto.
