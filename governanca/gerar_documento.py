"""Gera o documento ABNT da disciplina de Governanca em IA."""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

SAIDA = Path(__file__).resolve().parent
SAIDA.mkdir(parents=True, exist_ok=True)
ARQUIVO = SAIDA / "Governanca_IA_Observabilidade_Sensor_Monitoring_API.docx"

FONTE = "Arial"
PRETO = RGBColor(0, 0, 0)

AUTORES = [
    "[RM00000] [Nome completo do integrante 1]",
    "[RM00000] [Nome completo do integrante 2]",
    "[RM00000] [Nome completo do integrante 3]",
    "[RM00000] [Nome completo do integrante 4]",
]

doc = Document()


# --------------------------------------------------------------------------- base


def _definir_estilo_base() -> None:
    normal = doc.styles["Normal"]
    normal.font.name = FONTE
    normal.font.size = Pt(12)
    normal.font.color.rgb = PRETO
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(atributo), FONTE)
    paragrafo = normal.paragraph_format
    paragrafo.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    paragrafo.space_before = Pt(0)
    paragrafo.space_after = Pt(0)

    # Estilos de titulo: ABNT numera progressivamente e nao usa cor nem fonte diferente.
    for nome, tamanho, negrito, caixa_alta in [
        ("Heading 1", 12, True, True),
        ("Heading 2", 12, True, False),
        ("Heading 3", 12, False, False),
    ]:
        estilo = doc.styles[nome]
        estilo.font.name = FONTE
        estilo.font.size = Pt(tamanho)
        estilo.font.bold = negrito
        estilo.font.all_caps = caixa_alta
        estilo.font.color.rgb = PRETO
        estilo.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        estilo.paragraph_format.space_before = Pt(18)
        estilo.paragraph_format.space_after = Pt(18)
        estilo.paragraph_format.keep_with_next = True
        rpr = estilo.element.get_or_add_rPr()
        rfonts = rpr.get_or_add_rFonts()
        for atributo in ("w:ascii", "w:hAnsi", "w:cs"):
            rfonts.set(qn(atributo), FONTE)


def _margens(secao) -> None:
    # A4 explicito: o padrao do python-docx e Letter, e a NBR 14724 exige A4.
    secao.page_width = Cm(21.0)
    secao.page_height = Cm(29.7)
    secao.top_margin = Cm(3)
    secao.left_margin = Cm(3)
    secao.bottom_margin = Cm(2)
    secao.right_margin = Cm(2)
    secao.header_distance = Cm(2)
    secao.footer_distance = Cm(2)


def _campo(paragrafo, instrucao: str, tamanho: int = 12):
    """Insere um campo do Word (PAGE, TOC). O Word calcula o valor ao abrir."""
    run = paragrafo.add_run()
    run.font.name = FONTE
    run.font.size = Pt(tamanho)
    inicio = OxmlElement("w:fldChar")
    inicio.set(qn("w:fldCharType"), "begin")
    texto = OxmlElement("w:instrText")
    texto.set(qn("xml:space"), "preserve")
    texto.text = instrucao
    separa = OxmlElement("w:fldChar")
    separa.set(qn("w:fldCharType"), "separate")
    fim = OxmlElement("w:fldChar")
    fim.set(qn("w:fldCharType"), "end")
    for elemento in (inicio, texto, separa, fim):
        run._r.append(elemento)
    return run


def _reiniciar_numeracao(secao, inicio: int) -> None:
    sect_pr = secao._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is None:
        pg_num = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num)
    pg_num.set(qn("w:start"), str(inicio))


def _numeracao_continua(secao) -> None:
    """Remove o reinicio herdado: a secao textual continua a contagem da folha de rosto."""
    sect_pr = secao._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is not None:
        sect_pr.remove(pg_num)


def _atualizar_campos_ao_abrir() -> None:
    """Sem isto o sumario abre vazio: o Word so preenche o TOC se mandarem."""
    configuracoes = doc.settings.element
    atualizar = OxmlElement("w:updateFields")
    atualizar.set(qn("w:val"), "true")
    configuracoes.append(atualizar)


# ----------------------------------------------------------------- paragrafos


def p(texto="", *, alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=True,
      tamanho=12, negrito=False, italico=False, espacamento=None,
      antes=0, depois=0, maiusculas=False):
    paragrafo = doc.add_paragraph()
    paragrafo.alignment = alinhamento
    formato = paragrafo.paragraph_format
    formato.first_line_indent = Cm(1.25) if recuo else Cm(0)
    formato.space_before = Pt(antes)
    formato.space_after = Pt(depois)
    if espacamento is None:
        formato.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    else:
        formato.line_spacing = espacamento
    if texto:
        run = paragrafo.add_run(texto)
        run.font.name = FONTE
        run.font.size = Pt(tamanho)
        run.font.bold = negrito
        run.font.italic = italico
        run.font.all_caps = maiusculas
        run.font.color.rgb = PRETO
    return paragrafo


def centro(texto="", **kwargs):
    kwargs.setdefault("alinhamento", WD_ALIGN_PARAGRAPH.CENTER)
    kwargs.setdefault("recuo", False)
    return p(texto, **kwargs)


def titulo(texto: str, nivel: int = 1):
    paragrafo = doc.add_heading(texto, level=nivel)
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    for run in paragrafo.runs:
        run.font.name = FONTE
        run.font.color.rgb = PRETO
    return paragrafo


def secao_sem_numero(texto: str):
    """Resumo, listas, sumario e referencias: titulo centralizado e sem indicativo."""
    paragrafo = doc.add_heading(texto, level=1)
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    for run in paragrafo.runs:
        run.font.name = FONTE
        run.font.color.rgb = PRETO
    return paragrafo


def quadro(numero: int, legenda: str, cabecalho: list[str], linhas: list[list[str]],
           larguras: list[float], fonte_nota: str = "Elaborado pelos autores (2026)."):
    p(f"Quadro {numero} – {legenda}", alinhamento=WD_ALIGN_PARAGRAPH.LEFT, recuo=False,
      tamanho=10, espacamento=1.0, antes=12, depois=3)

    tabela = doc.add_table(rows=1, cols=len(cabecalho))
    tabela.style = "Table Grid"
    tabela.autofit = False
    for indice, celula in enumerate(tabela.rows[0].cells):
        celula.width = Cm(larguras[indice])
        _escrever_celula(celula, cabecalho[indice], negrito=True)
        _sombrear(celula, "D9D9D9")
    for linha in linhas:
        celulas = tabela.add_row().cells
        for indice, valor in enumerate(linha):
            celulas[indice].width = Cm(larguras[indice])
            _escrever_celula(celulas[indice], valor)

    p(f"Fonte: {fonte_nota}", alinhamento=WD_ALIGN_PARAGRAPH.LEFT, recuo=False,
      tamanho=10, espacamento=1.0, antes=3, depois=12)


def _escrever_celula(celula, texto: str, negrito: bool = False) -> None:
    celula.text = ""
    paragrafo = celula.paragraphs[0]
    paragrafo.paragraph_format.line_spacing = 1.0
    paragrafo.paragraph_format.space_before = Pt(2)
    paragrafo.paragraph_format.space_after = Pt(2)
    paragrafo.paragraph_format.first_line_indent = Cm(0)
    run = paragrafo.add_run(texto)
    run.font.name = FONTE
    run.font.size = Pt(10)
    run.font.bold = negrito
    run.font.color.rgb = PRETO


def _sombrear(celula, cor_hex: str) -> None:
    sombra = OxmlElement("w:shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:color"), "auto")
    sombra.set(qn("w:fill"), cor_hex)
    celula._tc.get_or_add_tcPr().append(sombra)


def referencia(texto: str):
    # Referencia ABNT: espaco simples, alinhada a esquerda, separada por uma linha em branco.
    return p(texto, alinhamento=WD_ALIGN_PARAGRAPH.LEFT, recuo=False,
             espacamento=1.0, depois=12)


def quebra_de_pagina():
    paragrafo = doc.add_paragraph()
    run = paragrafo.add_run()
    quebra = OxmlElement("w:br")
    quebra.set(qn("w:type"), "page")
    run._r.append(quebra)


# ============================================================== pre-textuais

_definir_estilo_base()
_margens(doc.sections[0])

# ------------------------------------------------------------------- 1. CAPA
centro("FIAP — FACULDADE DE INFORMÁTICA E ADMINISTRAÇÃO PAULISTA", negrito=True, depois=0)
centro("TECNÓLOGO EM INTELIGÊNCIA ARTIFICIAL", negrito=True)
for _ in range(4):
    centro()
for autor in AUTORES:
    centro(autor)
for _ in range(5):
    centro()
centro("OBSERVABILIDADE DE UM ENDPOINT DE IA:", negrito=True)
centro("CONTRATO DE INDICADORES, LIMIARES E RESPOSTA A DESVIOS", negrito=True)
centro("NA SENSOR MONITORING API DO DIGITAL TWIN FORZY", negrito=True)
for _ in range(9):
    centro()
centro("São Paulo")
centro("2026")

# -------------------------------------------------- 2. FOLHA DE ROSTO (p. 1)
secao = doc.add_section(WD_SECTION.NEW_PAGE)
_margens(secao)
_reiniciar_numeracao(secao, 1)
secao.different_first_page_header_footer = False

for autor in AUTORES:
    centro(autor)
for _ in range(5):
    centro()
centro("OBSERVABILIDADE DE UM ENDPOINT DE IA:", negrito=True)
centro("CONTRATO DE INDICADORES, LIMIARES E RESPOSTA A DESVIOS", negrito=True)
centro("NA SENSOR MONITORING API DO DIGITAL TWIN FORZY", negrito=True)
for _ in range(3):
    centro()

# Natureza do trabalho: recuo de 8 cm a partir da margem, espaco simples (NBR 14724).
natureza = p(
    "Checkpoint integrado apresentado às disciplinas de Governança em IA e Front-end do "
    "curso de Tecnólogo em Inteligência Artificial da FIAP, como requisito parcial para "
    "avaliação do segundo checkpoint.",
    alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=False, espacamento=1.0,
)
natureza.paragraph_format.left_indent = Cm(8)
natureza_orientador = p(
    "Orientador: Prof. [nome do professor].",
    alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY, recuo=False, espacamento=1.0, antes=12,
)
natureza_orientador.paragraph_format.left_indent = Cm(8)

for _ in range(7):
    centro()
centro("São Paulo")
centro("2026")

# ---------------------------------------------------------------- 3. RESUMO
quebra_de_pagina()
secao_sem_numero("RESUMO")
p(
    "Este trabalho define e valida um contrato mínimo de observabilidade para o endpoint de "
    "leitura de sensores da Sensor Monitoring API, construída sobre o provider de Sensores do "
    "Digital Twin Forzy. O problema tratado é a ausência de rastreabilidade em serviços de "
    "monitoramento: sem registro do que ocorreu em cada chamada, não é possível auditar o "
    "comportamento do sistema nem distinguir uma falha de coleta de uma leitura legítima. O "
    "objetivo foi mapear quais indicadores são efetivamente capturáveis nesse processo, "
    "estabelecer limiares e baselines para cada um, propor a camada gráfica adequada à sua "
    "leitura e determinar a ação devida quando o limiar é rompido. O método consistiu em "
    "instrumentar a borda da API com um middleware que registra, por chamada, os headers de "
    "contexto X-Session-Id e X-Feature, o instante de início e fim, a latência medida por "
    "relógio monotônico e os atributos de qualidade do dado devolvido — severidade, freshness e "
    "taxa de completude —, persistindo-os em banco relacional e expondo-os em endpoint próprio. "
    "Sobre esse registro foram definidos sete indicadores, agrupados em quatro dimensões: uso e "
    "disponibilidade, desempenho, qualidade do dado e rastreabilidade. O contrato foi validado "
    "contra uma coleta real de 95 chamadas, produzida em 5 de outubro de 2026 a partir de sete "
    "sessões distintas. Os resultados mostram conformidade nos indicadores de desempenho "
    "(latência média de 102,26 ms e percentil 95 de 251,29 ms, ambos sob o limiar de 500 ms) e "
    "rompimento em quatro indicadores: taxa de sucesso (95,74% contra 99%), freshness médio "
    "(183,28 s contra 120 s), taxa de completude de freshness (27,50% contra 80%) e cobertura "
    "dos headers de contexto (95,79% contra 100%). Conclui-se que o contrato é operante, no "
    "sentido de que cada limiar rompido pôde ser atribuído a uma causa identificável na própria "
    "evidência, e que a maior fragilidade observada não está no desempenho do serviço, mas na "
    "qualidade do dado que ele entrega.",
    recuo=False, espacamento=1.0, alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY,
)
p()
p(
    "Palavras-chave: Observabilidade. Governança em IA. Qualidade de dados. Indicadores de "
    "serviço. Digital Twin.",
    recuo=False, espacamento=1.0, alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY,
)

# ------------------------------------------------------- 4. LISTA DE QUADROS
quebra_de_pagina()
secao_sem_numero("LISTA DE QUADROS")
for item in [
    "Quadro 1 – Campos do contrato mínimo de observabilidade",
    "Quadro 2 – Indicadores mapeados, por dimensão",
    "Quadro 3 – Limiares, baselines e origem de cada número",
    "Quadro 4 – Camada gráfica recomendada por indicador",
    "Quadro 5 – Classificação de severidade do desvio",
    "Quadro 6 – Plano de resposta ao rompimento de limiar",
    "Quadro 7 – Resultado da coleta de 5 de outubro de 2026",
    "Quadro 8 – Composição do tráfego da coleta, por sessão",
]:
    p(item, recuo=False, espacamento=1.0, alinhamento=WD_ALIGN_PARAGRAPH.LEFT)

# -------------------------------------------------------- 5. LISTA DE SIGLAS
quebra_de_pagina()
secao_sem_numero("LISTA DE ABREVIATURAS E SIGLAS")
for sigla, significado in [
    ("ABNT", "Associação Brasileira de Normas Técnicas"),
    ("API", "Application Programming Interface"),
    ("HTTP", "Hypertext Transfer Protocol"),
    ("IA", "Inteligência Artificial"),
    ("ISO", "International Organization for Standardization"),
    ("JSON", "JavaScript Object Notation"),
    ("NBR", "Norma Brasileira"),
    ("p95", "Percentil 95"),
    ("REST", "Representational State Transfer"),
    ("SLO", "Service Level Objective"),
    ("SQL", "Structured Query Language"),
    ("UTC", "Coordinated Universal Time"),
]:
    p(f"{sigla}\t{significado}", recuo=False, espacamento=1.0,
      alinhamento=WD_ALIGN_PARAGRAPH.LEFT)

# --------------------------------------------------------------- 6. SUMARIO
quebra_de_pagina()
secao_sem_numero("SUMÁRIO")
sumario = p("", recuo=False)
_campo(sumario, r'TOC \o "1-3" \h \z \u')
p(
    "[Se o sumário aparecer vazio ao abrir o arquivo, selecione tudo com Ctrl+A e pressione F9 "
    "para o Word calcular as páginas. Depois apague este aviso.]",
    recuo=False, italico=True, tamanho=10, espacamento=1.0, antes=12,
)


# ================================================= parte textual (numerada)

secao_textual = doc.add_section(WD_SECTION.NEW_PAGE)
_margens(secao_textual)
_numeracao_continua(secao_textual)
secao_textual.header.is_linked_to_previous = False
cabecalho = secao_textual.header.paragraphs[0]
cabecalho.alignment = WD_ALIGN_PARAGRAPH.RIGHT
cabecalho.paragraph_format.first_line_indent = Cm(0)
_campo(cabecalho, "PAGE", tamanho=10)

# ------------------------------------------------------------ 1 INTRODUCAO
titulo("1 INTRODUÇÃO", 1)
p(
    "Sistemas de monitoramento industrial são frequentemente avaliados por aquilo que "
    "mostram: a leitura de um sensor, a severidade de um ativo, a curva de uma grandeza ao "
    "longo do tempo. Essa avaliação é incompleta. Uma leitura exibida na tela não informa se "
    "foi coletada há dois segundos ou há dez minutos, se todas as grandezas do ativo "
    "responderam ou se metade delas falhou, nem de qual funcionalidade partiu a consulta que "
    "a produziu. Sem esse segundo plano de informação, o sistema continua funcionando e deixa "
    "de ser auditável."
)
p(
    "Governança em IA trata exatamente dessa distância entre funcionar e poder ser "
    "verificado. A ISO/IEC 23894 (2023) orienta que o risco em sistemas de inteligência "
    "artificial seja gerido a partir de evidência sobre o comportamento efetivo do sistema, e "
    "não sobre o comportamento pretendido no projeto. Transportado para um serviço de "
    "monitoramento, o princípio impõe uma exigência concreta: toda chamada precisa deixar "
    "rastro, e esse rastro precisa ser suficiente para responder quem chamou, quando, a "
    "partir de qual funcionalidade, quanto tempo a operação levou e com que qualidade o dado "
    "foi entregue."
)
p(
    "Este trabalho aplica esse princípio ao endpoint de leitura de sensores da Sensor "
    "Monitoring API, construída na disciplina de Front-end sobre o provider de Sensores do "
    "Digital Twin Forzy. O escopo é deliberadamente estreito — apenas leitura atual e "
    "histórico, sem autenticação e sem os demais providers da solução —, o que permite "
    "observar uma única fatia da API com profundidade em vez de instrumentar superficialmente "
    "o conjunto."
)
p(
    "O objetivo é definir um contrato mínimo de observabilidade para esse endpoint e validar, "
    "a partir dos registros efetivamente coletados pelo back-end, se o contrato está sendo "
    "cumprido. Quatro perguntas organizam o desenvolvimento: quais indicadores são "
    "capturáveis nesse processo; quais são seus limiares e baselines; qual camada gráfica "
    "expõe melhor cada um; e o que deve ser feito quando um limiar é rompido."
)
p(
    "O documento está organizado em dez seções. A seção 2 delimita o objeto observado. A "
    "seção 3 descreve o contrato mínimo registrado por chamada. A seção 4 mapeia os "
    "indicadores. A seção 5 estabelece limiares e baselines. A seção 6 propõe a camada "
    "gráfica. A seção 7 define o plano de resposta a desvios. A seção 8 confronta o contrato "
    "com uma coleta real. A seção 9 apresenta a conclusão e a seção 10 declara o uso de "
    "inteligência artificial na elaboração do trabalho."
)

# -------------------------------------------------- 2 CONTEXTO E ESCOPO
titulo("2 CONTEXTO E DELIMITAÇÃO DO OBJETO OBSERVADO", 1)

titulo("2.1 A solução Forzy e o provider de Sensores", 2)
p(
    "O Forzy é um Digital Twin de planta industrial: representa, em software, o estado de "
    "ativos físicos monitorados. Entre seus providers, o de Sensores é responsável por "
    "publicar as grandezas elétricas e mecânicas de cada ativo — tensão, corrente, "
    "temperatura, rotação e vibração — tanto no instante atual quanto ao longo de uma janela "
    "histórica."
)
p(
    "O catálogo observado reúne sete ativos, distribuídos em três setores da planta, com "
    "estados distintos por construção: cinco em operação normal ou sob atenção, um em estado "
    "crítico e um desligado. A presença deliberada de um ativo desligado importa para a "
    "governança: corrente igual a zero num motor parado não é anomalia, e tratá-la como tal "
    "produziria alarme falso recorrente. O classificador de severidade trata esse caso como "
    "categoria própria, distinta tanto de operação normal quanto de ausência de dado."
)

titulo("2.2 O que é observado e o que não é", 2)
p(
    "O objeto de observação deste trabalho não é o sensor, é a chamada. O que se mede é o "
    "comportamento do serviço que entrega a leitura: com que rapidez responde, com que taxa "
    "de êxito, com que idade e completude o dado chega ao consumidor, e se a chamada carrega "
    "contexto suficiente para ser atribuída a uma funcionalidade."
)
p(
    "Ficam fora do escopo, por definição do checkpoint, a autenticação e a autorização das "
    "chamadas e a instrumentação dos providers de Equipamentos e de Plantas. A delimitação "
    "tem consequência metodológica: como não há identidade autenticada, a unidade de "
    "atribuição disponível é a sessão declarada pelo cliente, não o usuário. Esse limite é "
    "assumido explicitamente e volta a ser discutido na seção 4.5."
)

# ----------------------------------------------- 3 CONTRATO MINIMO
titulo("3 O CONTRATO MÍNIMO DE OBSERVABILIDADE", 1)

titulo("3.1 Onde o registro é produzido", 2)
p(
    "O registro é produzido na borda da aplicação, por um middleware que intercepta toda "
    "requisição antes de ela alcançar o controlador e volta a atuar depois que a resposta é "
    "montada. A escolha é de governança, não de arquitetura: atribuir o registro a cada "
    "controlador individualmente garantiria que todo endpoint criado no futuro nascesse sem "
    "instrumentação, e a lacuna só apareceria quando alguém sentisse falta do dado."
)
p(
    "A linha de registro nasce no momento em que a requisição entra, no estado "
    "EM_PROCESSAMENTO, e é fechada quando a resposta sai, com o status final e a latência "
    "medida. Gravar apenas ao fim seria mais simples e produziria um ponto cego: requisição "
    "que morre no meio do processamento não deixaria rastro algum. Uma linha presa em "
    "EM_PROCESSAMENTO é, portanto, informação — indica interrupção, não ausência de uso."
)
p(
    "A latência é medida por relógio monotônico, e não pela diferença entre os dois "
    "timestamps gravados. A distinção é relevante para a confiabilidade da evidência: ajuste "
    "do relógio do sistema durante a chamada distorceria a diferença entre timestamps, "
    "enquanto o contador monotônico é imune a esse efeito."
)
p(
    "Por fim, falha ao gravar o registro não derruba a requisição: o erro é logado e a "
    "resposta segue. Perder um rastro é um prejuízo de auditoria; devolver erro ao usuário "
    "por causa da instrumentação seria transformar o instrumento de medição em fonte de "
    "indisponibilidade."
)

titulo("3.2 Campos registrados por chamada", 2)
p(
    "O contrato mínimo reúne os campos descritos no Quadro 1, agrupados em quatro blocos. O "
    "bloco de contexto responde de onde a chamada veio; o de processamento, como ela correu; "
    "o de domínio, com que qualidade o dado foi entregue; e o de falha, por que não correu "
    "bem quando foi o caso."
)
quadro(
    1, "Campos do contrato mínimo de observabilidade",
    ["Bloco", "Campo", "Por que é registrado"],
    [
        ["Contexto", "call_id",
         "Identificador único da chamada, devolvido ao cliente no header X-Call-Id; é o que "
         "permite correlacionar o que o usuário viu com a linha do relatório."],
        ["Contexto", "session_id",
         "Recebido em X-Session-Id. Unidade de atribuição disponível na ausência de "
         "autenticação; isola uma coleta das demais."],
        ["Contexto", "feature",
         "Recebido em X-Feature. Diz de qual funcionalidade partiu a chamada, permitindo "
         "atribuir desempenho e qualidade a uma tela específica."],
        ["Contexto", "method, path, tag",
         "Identificam a operação e o ativo consultado, viabilizando recorte por rota e por "
         "equipamento."],
        ["Processamento", "processing_status",
         "EM_PROCESSAMENTO, CONCLUIDA ou FALHA. Distingue chamada que falhou de chamada que "
         "nunca terminou."],
        ["Processamento", "http_status",
         "Separa erro de contrato do cliente (4xx) de falha do serviço (5xx), o que muda a "
         "ação devida."],
        ["Processamento", "started_at, finished_at",
         "Instantes de início e fim em UTC, com precisão de milissegundo; base de todo "
         "agrupamento temporal."],
        ["Processamento", "latency_ms",
         "Duração medida por relógio monotônico; insumo dos indicadores de desempenho."],
        ["Domínio", "severity",
         "Pior severidade entre as grandezas do ativo no instante da resposta; liga a "
         "observabilidade ao estado real da planta."],
        ["Domínio", "freshness_seconds",
         "Idade da grandeza mais antiga do snapshot entregue; mede se o dado estava atual."],
        ["Domínio", "completeness_ratio",
         "Fração de grandezas efetivamente coletadas; mede se o snapshot estava completo."],
        ["Domínio", "points",
         "Quantidade de pontos devolvidos; distingue leitura pontual de série longa ao "
         "comparar latências."],
        ["Falha", "error_message",
         "Mensagem da exceção, truncada; permite agrupar falhas por causa sem expor rastro "
         "de pilha ao cliente."],
    ],
    [2.2, 3.4, 10.4],
)

titulo("3.3 O que o contrato deliberadamente não registra", 2)
p(
    "Três ausências são escolhas, não omissões. Rastro de pilha não é devolvido ao cliente, "
    "apenas registrado em log do servidor, porque detalhe interno de implementação exposto em "
    "resposta é superfície de ataque. O conteúdo integral da resposta não é persistido, "
    "porque duplicaria o dado do provider sem acrescentar capacidade de auditoria. Identidade "
    "pessoal não é coletada, porque o escopo não inclui autenticação e registrar "
    "identificador pessoal sem finalidade declarada contraria o princípio da minimização de "
    "dados."
)


# ------------------------------------------------- 4 MAPEAMENTO DOS INDICADORES
titulo("4 MAPEAMENTO DOS INDICADORES", 1)

titulo("4.1 Critério de seleção", 2)
p(
    "Nem toda métrica concebível é um indicador útil. Adotou-se aqui um critério de três "
    "condições, inspirado na distinção que Beyer et al. (2016) fazem entre métricas que "
    "descrevem o sistema e métricas que sustentam decisão. Um indicador só entra no contrato "
    "se for, cumulativamente: capturável a partir do que já existe no registro, sem instrumentação "
    "adicional; interpretável contra um limiar declarado, de modo que seu valor permita dizer "
    "conforme ou não conforme; e acionável, isto é, associado a uma conduta definida quando o "
    "limiar é rompido."
)
p(
    "A terceira condição é a mais restritiva e a que mais eliminou candidatos. Indicador sem "
    "ação associada é instrumentação decorativa: produz painel, não produz governança. Por "
    "esse critério foram descartadas, por exemplo, a contagem de bytes trafegados e a "
    "distribuição de métodos HTTP, ambas capturáveis e nenhuma delas acionável neste escopo."
)
p(
    "Os sete indicadores aprovados distribuem-se por quatro dimensões, apresentadas no Quadro "
    "2 e detalhadas nas subseções seguintes."
)
quadro(
    2, "Indicadores mapeados, por dimensão",
    ["Dimensão", "Indicador", "Pergunta que responde", "Fonte no registro"],
    [
        ["Uso e disponibilidade", "Volume de chamadas na janela",
         "O serviço está sendo usado?", "Contagem de linhas"],
        ["Uso e disponibilidade", "Taxa de sucesso",
         "As chamadas estão sendo atendidas?", "http_status < 400"],
        ["Desempenho", "Latência média",
         "O serviço responde rápido no caso típico?", "latency_ms"],
        ["Desempenho", "Latência no percentil 95",
         "E no caso ruim?", "latency_ms"],
        ["Qualidade do dado", "Freshness médio",
         "O dado entregue estava atual?", "freshness_seconds"],
        ["Qualidade do dado", "Taxa de completude de freshness",
         "Quantas entregas foram simultaneamente atuais e completas?",
         "freshness_seconds e completeness_ratio"],
        ["Rastreabilidade", "Cobertura dos headers de contexto",
         "As chamadas são atribuíveis a uma origem?", "session_id e feature"],
    ],
    [3.0, 3.6, 5.4, 4.0],
)

titulo("4.2 Dimensão de uso e disponibilidade", 2)
p(
    "O volume de chamadas na janela é o indicador de precedência lógica sobre todos os "
    "demais. Seu papel não é medir desempenho, e sim validar a própria medição: janela sem "
    "chamada produz todos os outros indicadores vazios, e vazio não é conformidade. Tratá-lo "
    "como indicador explícito evita o erro de leitura mais comum em painéis de "
    "observabilidade, que é interpretar ausência de erro como ausência de problema quando a "
    "causa real é ausência de tráfego."
)
p(
    "A taxa de sucesso é a fração de chamadas encerradas com status HTTP inferior a 400. Duas "
    "decisões de cálculo merecem registro. A primeira é que chamadas ainda em processamento "
    "são excluídas do denominador: contá-las como falha inventaria erro que não ocorreu. A "
    "segunda é que erros 4xx entram no cálculo junto com 5xx, ainda que tenham causas opostas "
    "— o 4xx aponta contrato mal cumprido pelo cliente e o 5xx aponta defeito no serviço. A "
    "separação entre os dois não se faz no indicador, e sim na ação, conforme a seção 7."
)

titulo("4.3 Dimensão de desempenho", 2)
p(
    "A latência média responde pelo caso típico e é insuficiente sozinha, porque a média "
    "absorve a cauda. Um serviço cuja maioria das chamadas responde em 50 ms e cuja minoria "
    "responde em 3 s pode exibir média confortável enquanto entrega experiência ruim a uma "
    "parcela dos usuários."
)
p(
    "Por isso o contrato inclui também o percentil 95, que responde pelo caso ruim. A leitura "
    "conjunta dos dois é mais informativa que a de qualquer um isolado: média e p95 próximos "
    "indicam distribuição homogênea; p95 muito acima da média indica lentidão intermitente, "
    "cuja investigação exige identificar as chamadas lentas individualmente, e não revisar o "
    "serviço como um todo."
)
p(
    "O percentil é calculado pelo método do vizinho mais próximo, sem interpolação. A escolha "
    "é conservadora e deliberada: interpolar entre dois valores observados produziria um "
    "número que nenhuma chamada efetivamente apresentou, sugerindo precisão que uma amostra "
    "desta ordem de grandeza não sustenta."
)

titulo("4.4 Dimensão de qualidade do dado", 2)
p(
    "Esta é a dimensão que distingue um contrato de observabilidade de um painel de "
    "infraestrutura. Um serviço pode responder rápido, com status 200, e entregar um dado "
    "velho e incompleto. Do ponto de vista de disponibilidade, nada aconteceu; do ponto de "
    "vista de governança, uma decisão de manutenção pode ter sido tomada sobre informação que "
    "não descrevia o estado atual do ativo. A ISO/IEC 25012 (2008) formaliza essa "
    "preocupação ao tratar atualidade e completude como características de qualidade "
    "independentes da disponibilidade do sistema."
)
p(
    "O freshness é definido como a idade, em segundos, da grandeza mais antiga do snapshot "
    "entregue, medida contra o instante de referência da resposta. A opção pela grandeza mais "
    "antiga, e não pela média das idades, é conservadora: um snapshot é tão atual quanto seu "
    "componente mais velho, e usar a média permitiria que uma grandeza coletada há dez "
    "minutos fosse mascarada por quatro grandezas coletadas há dois segundos."
)
p(
    "A taxa de completude de freshness é um indicador composto, e sua composição é o ponto "
    "central desta subseção. Ela mede a fração de entregas que foram simultaneamente atuais "
    "— freshness dentro do limiar — e completas — taxa de completude dentro do limiar. A "
    "justificativa para compor em vez de medir separadamente é que os dois defeitos se "
    "escondem um atrás do outro: um snapshot pode estar completo e velho, ou atual e pela "
    "metade, e em ambos os casos é impróprio para embasar decisão. Medir a conjunção força "
    "que ambos os critérios sejam satisfeitos para que a entrega conte como boa."
)
p(
    "A contrapartida desse desenho é que o indicador composto é, por construção, mais severo "
    "que seus componentes isolados, e cairá mais rápido que eles. Isso é intencional, mas "
    "exige que a leitura do indicador seja sempre acompanhada da inspeção de qual dos dois "
    "componentes o puxou para baixo — exigência que se traduz em ação concreta na seção 7."
)

titulo("4.5 Dimensão de rastreabilidade", 2)
p(
    "A cobertura dos headers de contexto mede a fração de chamadas que chegaram com "
    "X-Session-Id e X-Feature preenchidos com valores do contrato. É o indicador de "
    "precedência sobre a atribuição: chamada sem contexto é registrada, mas não pode ser "
    "imputada a nenhuma funcionalidade, de modo que todo recorte por tela se torna "
    "parcialmente cego."
)
p(
    "A instrumentação não corrige a falta em silêncio. Header ausente é registrado como "
    "sessão sem-sessao, e valor fora do contrato é registrado como funcionalidade "
    "desconhecida. A alternativa — atribuir um valor padrão plausível — produziria um "
    "relatório cosmeticamente íntegro e factualmente falso, no qual a lacuna de "
    "instrumentação desapareceria exatamente do lugar onde deveria aparecer."
)
p(
    "Cabe registrar o limite já antecipado na seção 2.2: o identificador de sessão é "
    "declarado pelo cliente e não é verificado. Ele serve para isolar coletas e atribuir "
    "tráfego a uma origem declarada, não para autenticar quem chamou. Enquanto a "
    "autenticação permanecer fora de escopo, este indicador mede disciplina de "
    "instrumentação, não identidade."
)

# -------------------------------------------- 5 LIMIARES E BASELINES
titulo("5 LIMIARES E BASELINES", 1)

titulo("5.1 Distinção entre baseline e limiar", 2)
p(
    "Baseline e limiar são coisas diferentes e tratá-los como sinônimos é fonte frequente de "
    "alarme mal calibrado. Baseline é o comportamento observado do sistema em condição "
    "considerada normal; é descritivo e obtido por medição. Limiar é o valor a partir do qual "
    "o comportamento passa a ser considerado inaceitável; é normativo e obtido por decisão. O "
    "baseline informa a decisão, não a substitui."
)
p(
    "Neste trabalho, os baselines de desempenho foram obtidos por medição direta, a partir da "
    "coleta descrita na seção 8. Os limiares de qualidade do dado e de rastreabilidade, por "
    "sua vez, não foram derivados do observado, e sim fixados a partir do uso pretendido do "
    "sistema — procedimento necessário porque derivar limiar do comportamento atual "
    "normalizaria o defeito existente, tornando o indicador incapaz de acusá-lo."
)

titulo("5.2 Limiares adotados e origem de cada número", 2)
p(
    "O Quadro 3 reúne os limiares, o baseline correspondente quando existe e a justificativa "
    "de cada valor. Todos são parametrizáveis por variável de ambiente, de modo que "
    "recalibrar a régua não exige alteração de código — propriedade relevante para "
    "governança, porque mantém o limiar auditável e versionado sem acoplá-lo ao ciclo de "
    "desenvolvimento."
)
quadro(
    3, "Limiares, baselines e origem de cada número",
    ["Indicador", "Limiar", "Baseline observado", "Origem do limiar"],
    [
        ["Volume de chamadas", "≥ 1 na janela", "95 chamadas em 50 s",
         "Valor de sanidade: existe para acusar janela sem tráfego, não para medir demanda."],
        ["Latência média", "≤ 500 ms", "102,26 ms",
         "Cerca de cinco vezes o baseline. Folga deliberada: o limiar deve acusar degradação "
         "estrutural, não variação normal de carga."],
        ["Latência p95", "≤ 500 ms", "251,29 ms",
         "Mesmo valor da média, por decisão: p95 acima de 500 ms já compromete a percepção "
         "de resposta imediata na interface."],
        ["Taxa de sucesso", "≥ 99%", "95,74%",
         "Objetivo de nível de serviço usual para leitura não crítica; admite uma falha a "
         "cada cem chamadas."],
        ["Freshness médio", "≤ 120 s", "183,28 s",
         "Decorre do uso: leitura com mais de dois minutos não sustenta decisão de "
         "manutenção sobre ativo em operação."],
        ["Taxa de completude de freshness", "≥ 80%", "27,50%",
         "Admite uma em cada cinco entregas degradada; abaixo disso a série perde "
         "representatividade para análise de tendência."],
        ["Cobertura de contexto", "= 100%", "95,79%",
         "Único limiar sem tolerância: chamada não rastreável invalida a atribuição de todos "
         "os demais indicadores."],
    ],
    [3.2, 2.2, 2.8, 7.8],
)

titulo("5.3 Por que três baselines ficam abaixo do limiar", 2)
p(
    "Três dos baselines medidos — taxa de sucesso, freshness e completude — situam-se fora do "
    "limiar adotado. A discrepância é esperada e não indica erro de calibração, por duas "
    "razões distintas."
)
p(
    "No caso da taxa de sucesso e da cobertura de contexto, a coleta incluiu tráfego "
    "deliberadamente fora do contrato, injetado para que os indicadores tivessem o que medir. "
    "Um baseline extraído de coleta sem nenhuma anomalia mediria apenas o caminho feliz e "
    "nada diria sobre a capacidade do contrato de detectar desvio."
)
p(
    "No caso do freshness e da completude, a discrepância é substantiva: o provider simula "
    "falha de coleta a taxas fixas, e são essas falhas que o indicador está acusando. "
    "Rebaixar o limiar até acomodá-las seria exatamente o erro que a seção 5.1 descreve — "
    "normalizar o defeito pela via da régua. A leitura correta é a inversa: o indicador está "
    "funcionando, e o que ele acusa é um problema de coleta a ser tratado, conforme a seção 7."
)

# ------------------------------------------------- 6 CAMADA GRAFICA
titulo("6 CAMADA GRÁFICA RECOMENDADA POR INDICADOR", 1)

titulo("6.1 Critério de escolha da forma gráfica", 2)
p(
    "A escolha da representação gráfica não é estética; é uma decisão sobre qual pergunta o "
    "gráfico deve tornar respondível em um olhar. Adotou-se aqui um critério por natureza da "
    "pergunta: evolução ao longo do tempo pede linha, porque a continuidade visual é o que "
    "torna tendência perceptível; comparação entre categorias discretas pede barra, porque o "
    "comprimento é lido com mais precisão que a inclinação; e verificação de conformidade "
    "contra um valor fixo pede que o limiar apareça no próprio gráfico, como banda ou linha "
    "de referência."
)
p(
    "Essa última recomendação é a que mais diferencia um painel de governança de um painel "
    "operacional. Um gráfico de latência sem a banda do limiar exige que o leitor conheça o "
    "limiar de memória para julgar o que está vendo; com a banda desenhada, o julgamento é "
    "imediato e não depende de conhecimento prévio."
)

titulo("6.2 Recomendação por indicador", 2)
p(
    "O Quadro 4 apresenta a camada gráfica recomendada para cada indicador e a razão da "
    "escolha. As recomendações não residem apenas neste documento: estão declaradas no "
    "catálogo de indicadores da própria API e são devolvidas pelo endpoint de contrato, de "
    "modo que a interface e o documento partem da mesma fonte."
)
quadro(
    4, "Camada gráfica recomendada por indicador",
    ["Indicador", "Camada gráfica", "Por que esta e não outra"],
    [
        ["Volume de chamadas", "Barra, agrupada por hora",
         "Mostra concentração de uso e, sobretudo, janelas sem tráfego — que em linha "
         "apareceriam como queda contínua, não como ausência."],
        ["Latência média", "Linha temporal com banda do limiar",
         "Degradação de desempenho é gradual; a linha revela a inclinação, e a banda dispensa "
         "o leitor de lembrar o limiar."],
        ["Latência p95", "Linha sobreposta à da média",
         "O que informa não é o p95 isolado, e sim a distância entre as duas curvas, que "
         "revela a cauda que a média esconde."],
        ["Taxa de sucesso", "Linha temporal com área de erro empilhada por status",
         "A linha responde se há falha; a área empilhada por status responde de que tipo, que "
         "é o que determina a ação."],
        ["Freshness médio", "Linha temporal da idade média do dado",
         "Atraso de coleta costuma crescer progressivamente; a linha permite antecipar o "
         "rompimento antes que ele ocorra."],
        ["Taxa de completude de freshness", "Linha de evolução da taxa",
         "É um indicador de degradação lenta; a leitura que importa é a tendência entre "
         "coletas, não o valor pontual."],
        ["Cobertura de contexto", "Barra por funcionalidade",
         "A pergunta é qual tela não envia contexto; a barra isola o responsável, o que uma "
         "série temporal não faria."],
    ],
    [3.2, 4.2, 8.6],
)

titulo("6.3 Granularidade e limite da amostra", 2)
p(
    "Toda recomendação de série temporal pressupõe janela suficiente para que haja série. A "
    "coleta de validação deste trabalho concentra-se em cerca de cinquenta segundos, o que "
    "reduz o gráfico de volume por hora a uma única barra e torna as linhas de evolução pouco "
    "informativas. A limitação é da coleta, não do contrato: o registro é agrupado por "
    "instante de início da chamada e suporta qualquer granularidade, bastando que as coletas "
    "sejam repetidas em momentos distintos do dia."
)


# ------------------------------------------- 7 PLANO DE RESPOSTA
titulo("7 PLANO DE RESPOSTA AO ROMPIMENTO DE LIMIAR", 1)

titulo("7.1 Por que o plano precede o alarme", 2)
p(
    "Indicador cujo rompimento não tem conduta associada acaba sendo silenciado. É um padrão "
    "conhecido: o alarme dispara, ninguém sabe o que fazer, o alarme é desativado, e a "
    "medição que o sustentava perde propósito. Por isso a conduta foi definida junto com o "
    "indicador e reside no mesmo catálogo, e não em documento apartado — limiar que existe "
    "apenas no documento envelhece sem que ninguém perceba."
)

titulo("7.2 Classificação de severidade do desvio", 2)
p(
    "Nem todo rompimento merece a mesma reação. Adotou-se uma escala de três níveis, "
    "determinada pela distância ao limiar e pela persistência do desvio, apresentada no "
    "Quadro 5. A persistência importa tanto quanto a magnitude: um rompimento isolado pode "
    "ser ruído de medição, enquanto o mesmo valor repetido em janelas consecutivas é sinal."
)
quadro(
    5, "Classificação de severidade do desvio",
    ["Nível", "Critério", "Prazo de resposta"],
    [
        ["Atenção", "Rompimento em uma janela, com desvio de até 20% em relação ao limiar.",
         "Registrar e observar a janela seguinte antes de agir."],
        ["Relevante",
         "Rompimento em duas janelas consecutivas, ou desvio superior a 20% em uma janela.",
         "Investigar a causa na mesma sessão de trabalho."],
        ["Crítico",
         "Rompimento de cobertura de contexto, qualquer presença de status 5xx, ou "
         "rompimento persistente por três janelas.",
         "Interromper o uso do indicador afetado para decisão até a causa ser identificada."],
    ],
    [2.4, 8.2, 5.4],
)
p(
    "O rompimento da cobertura de contexto é classificado como crítico independentemente da "
    "magnitude, e a razão é de precedência lógica: enquanto houver chamada não atribuível, "
    "todo recorte por funcionalidade está incompleto, de modo que os demais indicadores "
    "perdem parte de sua validade como evidência."
)

titulo("7.3 Conduta por indicador", 2)
p(
    "O Quadro 6 define, para cada indicador, a primeira verificação a ser feita e a conduta "
    "decorrente. A sequência importa: cada conduta começa por distinguir hipóteses "
    "concorrentes antes de propor correção, porque agir sobre a hipótese errada consome tempo "
    "e produz a impressão falsa de que o problema foi tratado."
)
quadro(
    6, "Plano de resposta ao rompimento de limiar",
    ["Indicador", "Primeira verificação", "Conduta"],
    [
        ["Volume de chamadas",
         "Distinguir ausência de uso de ausência de instrumentação.",
         "Validar que o cliente está no ar e enviando contexto antes de concluir qualquer "
         "outro indicador da janela; volume zero invalida a leitura dos demais."],
        ["Latência média",
         "Medir a latência do provider de sensores isoladamente.",
         "Se a lentidão vier do coletor, tratar na origem; se vier da API, reduzir a janela "
         "padrão do histórico, que é a operação de maior custo."],
        ["Latência p95",
         "Comparar p95 com a média da mesma janela.",
         "P95 rompido com média conforme indica lentidão intermitente: localizar as chamadas "
         "lentas pelo identificador e correlacioná-las por funcionalidade e por ativo, em vez "
         "de revisar o serviço inteiro."],
        ["Taxa de sucesso",
         "Classificar as falhas por status HTTP.",
         "Predomínio de 4xx aponta contrato mal cumprido pelo cliente e exige correção no "
         "front; qualquer 5xx aponta defeito na API e exige correção antes de novo uso do "
         "endpoint para decisão."],
        ["Freshness médio",
         "Verificar se o atraso é geral ou concentrado em ativos específicos.",
         "Marcar a leitura como desatualizada na interface e suspender seu uso como base para "
         "decisão de manutenção até que o coletor seja verificado."],
        ["Taxa de completude de freshness",
         "Identificar qual componente — atualidade ou completude — puxou o indicador, e quais "
         "grandezas faltaram por ativo.",
         "Falha concentrada em um sensor indica substituição de hardware; falha espalhada "
         "entre ativos indica problema de rede ou do coletor."],
        ["Cobertura de contexto",
         "Identificar, pelo gráfico por funcionalidade, qual tela não envia os headers.",
         "Corrigir o cliente. Enquanto a cobertura não retornar a 100%, registrar nos "
         "relatórios que a atribuição por funcionalidade está incompleta."],
    ],
    [3.0, 5.0, 8.0],
)

titulo("7.4 Responsabilidade e periodicidade", 2)
p(
    "A conduta só se efetiva se houver quem responda por ela. Propõe-se que a verificação dos "
    "indicadores seja feita a cada ciclo de desenvolvimento pela equipe responsável pela API, "
    "com dois desdobramentos. Rompimentos de desempenho e disponibilidade são tratados pela "
    "própria equipe de desenvolvimento. Rompimentos de qualidade do dado escapam ao software "
    "— têm origem no coletor ou no equipamento — e devem ser encaminhados à manutenção, com a "
    "evidência da coleta anexada. O rompimento de cobertura de contexto é sempre de "
    "responsabilidade de quem desenvolve o cliente que originou a chamada."
)

# ----------------------------------------------- 8 VALIDACAO
titulo("8 VALIDAÇÃO DO CONTRATO COM DADOS REAIS", 1)

titulo("8.1 Procedimento de coleta", 2)
p(
    "A validação foi feita contra tráfego real, produzido em 5 de outubro de 2026 contra a "
    "API em execução local, com a tabela de registros esvaziada imediatamente antes do "
    "início. Nenhum valor apresentado nesta seção foi escrito manualmente: todos foram "
    "medidos pelo mesmo middleware que opera em condição normal."
)
p(
    "Foram executadas sessões simultâneas de consumo, combinando a interface e o script de "
    "consumo externo, cada rodada percorrendo leitura atual e histórico. A composição do "
    "tráfego por sessão está no Quadro 8. A coleta resultou em 95 chamadas registradas na "
    "janela do relatório, das quais 94 constam da exportação em arquivo — a diferença é a "
    "própria chamada que gerou o relatório, ainda em processamento no instante da exportação, "
    "que é exatamente o comportamento descrito na seção 3.1."
)
p(
    "Duas classes de anomalia foram injetadas de propósito e são identificáveis: quatro "
    "chamadas sem os headers de contexto, registradas sob a sessão sem-sessao, e quatro "
    "chamadas a uma tag inexistente, registradas sob a sessão anomalia-tag-invalida. Ambas "
    "podem ser isoladas da análise por filtro de sessão. As demais quebras de limiar não "
    "foram injetadas: decorrem da simulação de falha de coleta do provider."
)

titulo("8.2 Resultados observados", 2)
p(
    "O Quadro 7 apresenta o valor medido de cada indicador, o limiar aplicado e o veredito de "
    "conformidade apurado pela própria API."
)
quadro(
    7, "Resultado da coleta de 5 de outubro de 2026",
    ["Indicador", "Valor medido", "Limiar", "Veredito"],
    [
        ["Volume de chamadas", "95 chamadas", "≥ 1", "Conforme"],
        ["Latência média", "102,26 ms", "≤ 500 ms", "Conforme"],
        ["Latência p95", "251,29 ms", "≤ 500 ms", "Conforme"],
        ["Taxa de sucesso", "95,74%", "≥ 99%", "Rompido"],
        ["Freshness médio", "183,28 s", "≤ 120 s", "Rompido"],
        ["Taxa de completude de freshness", "27,50%", "≥ 80%", "Rompido"],
        ["Cobertura de contexto", "95,79%", "= 100%", "Rompido"],
    ],
    [5.4, 3.4, 2.6, 2.6],
    fonte_nota="Dados de evidencias/indicadores_2026-10-05.json, gerados pela própria API.",
)
quadro(
    8, "Composição do tráfego da coleta, por sessão",
    ["Sessão", "Chamadas", "Natureza"],
    [
        ["coleta-ui-01", "26", "Consumo regular, via interface"],
        ["coleta-ui-02", "26", "Consumo regular, via interface"],
        ["coleta-script-01", "26", "Consumo regular, via script externo"],
        ["coleta-script-02", "6", "Consumo regular, via script externo"],
        ["sem-sessao", "4", "Anomalia injetada: chamadas sem headers de contexto"],
        ["anomalia-tag-invalida", "4", "Anomalia injetada: chamadas a tag inexistente"],
        ["relatorio-final", "2", "Geração do relatório de encerramento da coleta"],
    ],
    [5.0, 2.4, 6.6],
    fonte_nota="Dados de evidencias/coleta_2026-10-05.csv (94 linhas exportadas).",
)

titulo("8.3 Leitura dos rompimentos", 2)
p(
    "A taxa de sucesso de 95,74% corresponde a 90 chamadas bem-sucedidas em 94 encerradas. As "
    "quatro falhas são integralmente os 404 injetados contra tags inexistentes. Pela conduta "
    "do Quadro 6, a classificação por status é o primeiro passo: todas são 4xx e nenhuma é "
    "5xx, o que caracteriza contrato mal cumprido pelo cliente, não defeito do serviço. O "
    "rompimento é, portanto, explicado integralmente pela anomalia deliberada."
)
p(
    "A cobertura de contexto de 95,79% corresponde a 91 chamadas atribuíveis em 95. As quatro "
    "não atribuíveis são exatamente as chamadas injetadas sem headers. A evidência confirma "
    "que a instrumentação não corrige a lacuna em silêncio, que era o comportamento desejado "
    "descrito na seção 4.5."
)
p(
    "O freshness médio de 183,28 s rompe o limiar de 120 s, com valores individuais entre "
    "6,69 s e 528,96 s. A dispersão é informativa: a maior parte das entregas é recente e uma "
    "minoria é muito antiga, o que corresponde ao padrão de falha intermitente de coleta e "
    "não a um atraso sistemático. Pela conduta prevista, trata-se de caso a encaminhar à "
    "verificação do coletor, com suspensão do uso dessas leituras para decisão de manutenção."
)
p(
    "A taxa de completude de freshness de 27,50% é o rompimento mais severo e o mais "
    "instrutivo. Tomada isoladamente, a completude média das entregas é de 95,67% — valor "
    "que, sozinho, seria lido como adequado. É a composição com a atualidade que revela o "
    "problema: apenas 22 das 80 entregas com dado de qualidade registrado foram "
    "simultaneamente completas e dentro do limiar de freshness. O indicador composto fez "
    "exatamente aquilo que a seção 4.4 previu — expôs um defeito que seus componentes "
    "isolados mascaravam."
)
p(
    "Os três indicadores conformes também informam. A latência média de 102,26 ms e o p95 de "
    "251,29 ms mantêm a razão entre p95 e média em aproximadamente 2,5, o que indica "
    "distribuição com cauda moderada e ausência de lentidão intermitente relevante. O "
    "desempenho do serviço, portanto, não é o ponto frágil da solução."
)

titulo("8.4 Limitações da validação", 2)
p(
    "Três limitações delimitam o alcance destes resultados. A primeira é a janela: cerca de "
    "cinquenta segundos de tráfego não permitem avaliar tendência, apenas estado. A segunda é "
    "o ambiente: a coleta ocorreu em execução local, de modo que as latências medidas não "
    "incluem rede entre cliente e servidor e devem ser lidas como piso, não como estimativa "
    "de produção. A terceira é a origem dos dados de sensor: o provider simula leitura, e as "
    "taxas de ausência e atraso são parâmetros conhecidos da simulação — o que valida a "
    "capacidade de detecção do contrato, mas não equivale a medir a confiabilidade de um "
    "coletor real."
)

# ------------------------------------------------------ 9 CONCLUSAO
titulo("9 CONCLUSÃO", 1)
p(
    "[ESTA SEÇÃO DEVE SER ESCRITA PELO GRUPO, SEM USO DE IA. O critério de avaliação exige "
    "que a conclusão seja elaborada com as palavras e percepções dos integrantes, e vale 3,0 "
    "pontos. Apague integralmente este bloco e escreva o texto de vocês no lugar.]",
    negrito=True, recuo=False, antes=6, depois=12,
)
p(
    "Perguntas que podem orientar a escrita — responder com as próprias palavras, em texto "
    "corrido, sem transformá-las em lista:",
    recuo=False, italico=True, depois=6,
)
for pergunta in [
    "O que surpreendeu o grupo ao ver os indicadores calculados sobre tráfego real pela "
    "primeira vez?",
    "Qual dos sete indicadores vocês consideram o mais difícil de defender, e por quê?",
    "A decisão de compor atualidade e completude num indicador único se mostrou acertada na "
    "prática, ou produziu um número severo demais para ser usado no dia a dia?",
    "O que mudaria na forma de construir uma API depois de ter feito a instrumentação na "
    "borda em vez de endpoint a endpoint?",
    "Que limite deste trabalho vocês mais sentiram, e o que fariam diferente com mais tempo?",
    "O que desta experiência vocês levariam para a Sprint 4 da disciplina?",
]:
    p(f"— {pergunta}", recuo=False, italico=True, espacamento=1.0, depois=6)

# ---------------------------------------------------- 10 USO DE IA
titulo("10 USO DE INTELIGÊNCIA ARTIFICIAL", 1)
p(
    "Esta seção declara o uso de ferramentas de inteligência artificial generativa na "
    "elaboração do trabalho, em atendimento à exigência do checkpoint."
)
p(
    "[CONFIRMAR E AJUSTAR ESTE TEXTO CONFORME O QUE O GRUPO EFETIVAMENTE FEZ, antes da "
    "entrega. A declaração precisa ser verdadeira.]",
    negrito=True, recuo=False, antes=6, depois=12,
)
p(
    "Foi utilizado assistente de IA generativa em duas frentes. Na implementação, para "
    "escrever código a partir dos padrões de projeto já adotados pelo grupo e para revisar a "
    "consistência entre a definição dos indicadores e seu cálculo efetivo na API. Na redação, "
    "para estruturar o documento segundo a norma ABNT e para organizar a argumentação das "
    "seções descritivas."
)
p(
    "As decisões substantivas do trabalho não foram delegadas à ferramenta. A escolha de "
    "quais indicadores integram o contrato, a fixação de cada limiar, a definição da camada "
    "gráfica e a determinação das condutas de resposta foram tomadas e validadas pelos "
    "integrantes, que respondem por elas. Os dados apresentados na seção 8 não foram gerados "
    "por IA: resultam da execução efetiva da API, com os valores medidos pelo próprio "
    "middleware de observabilidade e exportados do banco de dados, e podem ser conferidos nos "
    "arquivos de evidência do repositório."
)
p(
    "A conclusão apresentada na seção 9 foi redigida integralmente pelos integrantes do "
    "grupo, sem uso de ferramenta de IA, conforme exigido pelo critério de avaliação."
)
p(
    "O grupo revisou todo o conteúdo produzido com apoio da ferramenta e assume "
    "responsabilidade pela exatidão das afirmações, dos dados e das referências aqui "
    "apresentados."
)

# ------------------------------------------------------ REFERENCIAS
quebra_de_pagina()
secao_sem_numero("REFERÊNCIAS")
for item in [
    "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. NBR 5410: Instalações elétricas de baixa "
    "tensão. Rio de Janeiro: ABNT, 2004.",

    "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. NBR 6023: Informação e documentação — "
    "Referências — Elaboração. Rio de Janeiro: ABNT, 2018.",

    "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. NBR 6027: Informação e documentação — Sumário "
    "— Apresentação. Rio de Janeiro: ABNT, 2012.",

    "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. NBR 6028: Informação e documentação — Resumo, "
    "resenha e recensão — Apresentação. Rio de Janeiro: ABNT, 2021.",

    "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. NBR 14724: Informação e documentação — "
    "Trabalhos acadêmicos — Apresentação. Rio de Janeiro: ABNT, 2011.",

    "BEYER, Betsy; JONES, Chris; PETOFF, Jennifer; MURPHY, Niall Richard. Site Reliability "
    "Engineering: how Google runs production systems. Sebastopol: O'Reilly Media, 2016.",

    "INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. ISO 10816-3: Mechanical vibration — "
    "Evaluation of machine vibration by measurements on non-rotating parts — Part 3: "
    "Industrial machines with nominal power above 15 kW and nominal speeds between 120 r/min "
    "and 15 000 r/min when measured in situ. Geneva: ISO, 2009.",

    "INTERNATIONAL ORGANIZATION FOR STANDARDIZATION; INTERNATIONAL ELECTROTECHNICAL "
    "COMMISSION. ISO/IEC 25012: Software engineering — Software product Quality Requirements "
    "and Evaluation (SQuaRE) — Data quality model. Geneva: ISO/IEC, 2008.",

    "INTERNATIONAL ORGANIZATION FOR STANDARDIZATION; INTERNATIONAL ELECTROTECHNICAL "
    "COMMISSION. ISO/IEC 23894: Information technology — Artificial intelligence — Guidance "
    "on risk management. Geneva: ISO/IEC, 2023.",

    "INTERNATIONAL ORGANIZATION FOR STANDARDIZATION; INTERNATIONAL ELECTROTECHNICAL "
    "COMMISSION. ISO/IEC 42001: Information technology — Artificial intelligence — Management "
    "system. Geneva: ISO/IEC, 2023.",

    "MAJORS, Charity; FONG-JONES, Liz; MIRANDA, George. Observability Engineering: achieving "
    "production excellence. Sebastopol: O'Reilly Media, 2022.",

    "NATIONAL INSTITUTE OF STANDARDS AND TECHNOLOGY. Artificial Intelligence Risk Management "
    "Framework (AI RMF 1.0). Gaithersburg: NIST, 2023.",
]:
    referencia(item)

_atualizar_campos_ao_abrir()
doc.save(ARQUIVO)
print(f"gerado: {ARQUIVO}")
