from dataclasses import dataclass


@dataclass(frozen=True)
class IndicatorDefinition:
    code: str
    label: str
    unit: str
    operator: str  # '<=' ou '>=', comparação do valor observado contra o limiar
    suggested_chart: str
    breach_action: str


INDICATOR_CATALOG: dict[str, IndicatorDefinition] = {
    "total_chamadas": IndicatorDefinition(
        code="total_chamadas",
        label="Volume de chamadas na janela",
        unit="chamadas",
        operator=">=",
        suggested_chart="Barra por hora — mostra concentração de uso e janelas sem tráfego",
        breach_action="Volume zero por mais de uma janela indica front sem instrumentação "
                      "ou API fora do ar: validar o cliente antes de concluir qualquer indicador.",
    ),
    "latencia_media_ms": IndicatorDefinition(
        code="latencia_media_ms",
        label="Latência média",
        unit="ms",
        operator="<=",
        suggested_chart="Linha temporal com banda do limiar — evidencia degradação gradual",
        breach_action="Acima do limiar, verificar o provider de sensores antes da API: medir a "
                      "latência do coletor e, se confirmada, reduzir a janela padrão do histórico.",
    ),
    "latencia_p95_ms": IndicatorDefinition(
        code="latencia_p95_ms",
        label="Latência no percentil 95",
        unit="ms",
        operator="<=",
        suggested_chart="Linha do p95 sobreposta à da média — a distância entre as duas "
                        "revela cauda longa que a média esconde",
        breach_action="P95 estourado com média conforme indica lentidão intermitente: "
                      "investigar as chamadas lentas pelo id e correlacionar por funcionalidade.",
    ),
    "taxa_sucesso": IndicatorDefinition(
        code="taxa_sucesso",
        label="Taxa de sucesso das chamadas",
        unit="fração",
        operator=">=",
        suggested_chart="Linha temporal com área de erro empilhada por status",
        breach_action="Abaixo do limiar, classificar os erros por status: 4xx aponta contrato "
                      "errado no front; 5xx aponta falha na API e exige correção antes de novo uso.",
    ),
    "freshness_medio_s": IndicatorDefinition(
        code="freshness_medio_s",
        label="Freshness médio do dado entregue",
        unit="s",
        operator="<=",
        suggested_chart="Linha temporal da idade média do dado",
        breach_action="Dado mais velho que o limiar deve ser exibido na interface com marca de "
                      "desatualizado, e a leitura não pode embasar decisão de manutenção até "
                      "que o coletor seja verificado.",
    ),
    "taxa_completude_freshness": IndicatorDefinition(
        code="taxa_completude_freshness",
        label="Taxa de completude de freshness",
        unit="fração",
        operator=">=",
        suggested_chart="Linha de evolução da taxa — é a forma de ver se a coleta degrada no tempo",
        breach_action="Abaixo do limiar, identificar quais grandezas faltaram por ativo: falha "
                      "concentrada num sensor é troca de hardware; espalhada é problema de rede "
                      "ou do coletor.",
    ),
    "cobertura_contexto": IndicatorDefinition(
        code="cobertura_contexto",
        label="Cobertura dos headers de contexto",
        unit="fração",
        operator=">=",
        suggested_chart="Barra por funcionalidade — isola qual tela não envia contexto",
        breach_action="Chamada sem X-Session-Id ou X-Feature não é rastreável. Abaixo do limiar, "
                      "corrigir o cliente: sem contexto, nenhum outro indicador pode ser "
                      "atribuído a uma funcionalidade.",
    ),
}


@dataclass(frozen=True)
class Indicator:
    definition: IndicatorDefinition
    value: float | None
    threshold: float | None

    @property
    def compliant(self) -> bool | None:
        if self.value is None or self.threshold is None:
            return None
        if self.definition.operator == "<=":
            return self.value <= self.threshold
        return self.value >= self.threshold
