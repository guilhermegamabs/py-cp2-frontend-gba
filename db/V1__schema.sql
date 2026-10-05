-- Cria o database sensor_db e a tabela de processamento das requisicoes.

CREATE DATABASE IF NOT EXISTS sensor_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE sensor_db;

-- Sem IF NOT EXISTS de proposito: falhar alto e melhor que aplicar pela metade.
CREATE TABLE sensor_tb_request_processing (
    id                 BIGINT        NOT NULL AUTO_INCREMENT,

    -- Identificador da chamada gerado na borda e devolvido no header X-Call-Id.
    call_id            CHAR(36)      NOT NULL,

    -- Contrato minimo de contexto: headers X-Session-Id e X-Feature enviados pelo front.
    session_id         VARCHAR(64)   NOT NULL,
    feature            VARCHAR(32)   NOT NULL,

    method             VARCHAR(10)   NOT NULL,
    path               VARCHAR(255)  NOT NULL,
    tag                VARCHAR(16)   NULL,

    -- Estado do processamento. VARCHAR + CHECK no lugar de ENUM: valor novo nao exige ALTER.
    processing_status  VARCHAR(20)   NOT NULL DEFAULT 'EM_PROCESSAMENTO',

    -- Status HTTP so existe depois da resposta montada, por isso e anulavel.
    http_status        SMALLINT      NULL,

    -- Data do fato: inicio e fim do processamento, em UTC, com milissegundo.
    started_at         DATETIME(3)   NOT NULL,
    finished_at        DATETIME(3)   NULL,

    -- Latencia medida por relogio monotonico na aplicacao, nao derivada dos timestamps.
    latency_ms         DECIMAL(10,2) NULL,

    -- Indicadores de dominio da resposta devolvida, insumo direto da Governanca.
    severity           VARCHAR(16)   NULL,
    freshness_seconds  DECIMAL(10,2) NULL,
    completeness_ratio DECIMAL(5,4)  NULL,
    points             INT           NULL,

    error_message      VARCHAR(500)  NULL,

    -- Data do registro, preenchida pelo banco. Relatorio agrupa por started_at, nao por aqui.
    created_at         TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Reprocessar a mesma chamada nao pode duplicar linha.
    CONSTRAINT uk_sensor_tb_request_processing_call_id UNIQUE (call_id),

    CONSTRAINT ck_sensor_tb_request_processing_status CHECK (
        processing_status IN ('EM_PROCESSAMENTO', 'CONCLUIDA', 'FALHA')
    ),
    CONSTRAINT ck_sensor_tb_request_processing_completeness CHECK (
        completeness_ratio IS NULL OR (completeness_ratio >= 0 AND completeness_ratio <= 1)
    )
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;

-- Indice em toda coluna usada como filtro frequente do relatorio de observabilidade.
CREATE INDEX ix_sensor_tb_request_processing_started_at ON sensor_tb_request_processing (started_at);
CREATE INDEX ix_sensor_tb_request_processing_feature    ON sensor_tb_request_processing (feature);
CREATE INDEX ix_sensor_tb_request_processing_session_id ON sensor_tb_request_processing (session_id);
CREATE INDEX ix_sensor_tb_request_processing_tag        ON sensor_tb_request_processing (tag);
CREATE INDEX ix_sensor_tb_request_processing_status     ON sensor_tb_request_processing (processing_status);
