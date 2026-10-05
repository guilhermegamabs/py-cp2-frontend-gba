-- Dados de teste, so em ambiente local. Reexecutavel: ON DUPLICATE KEY nao duplica.

USE sensor_db;

INSERT INTO sensor_tb_request_processing (
    call_id, session_id, feature, method, path, tag,
    processing_status, http_status, started_at, finished_at, latency_ms,
    severity, freshness_seconds, completeness_ratio, points
) VALUES
    ('11111111-1111-4111-8111-111111111111', 'sessao-demo-01', 'leitura-atual', 'GET',
     '/v1/sensores/M-101/leitura-atual', 'M-101',
     'CONCLUIDA', 200, '2026-10-05 12:00:00.000', '2026-10-05 12:00:00.142', 142.00,
     'ok', 11.40, 1.0000, 1),
    ('22222222-2222-4222-8222-222222222222', 'sessao-demo-01', 'historico', 'GET',
     '/v1/sensores/M-202/historico', 'M-202',
     'CONCLUIDA', 200, '2026-10-05 12:01:10.000', '2026-10-05 12:01:10.488', 488.00,
     'crit', 96.20, 0.9200, 24),
    -- Chamada com grandeza faltando: e o caso que faz a taxa de completude sair de 100%.
    ('33333333-3333-4333-8333-333333333333', 'sessao-demo-02', 'leitura-atual', 'GET',
     '/v1/sensores/M-303/leitura-atual', 'M-303',
     'CONCLUIDA', 200, '2026-10-05 12:02:05.000', '2026-10-05 12:02:05.097', 97.00,
     'warn', 318.70, 0.6000, 1),
    -- Tag inexistente: alimenta a taxa de sucesso com um 404 legitimo.
    ('44444444-4444-4444-8444-444444444444', 'sessao-demo-02', 'leitura-atual', 'GET',
     '/v1/sensores/M-999/leitura-atual', NULL,
     'FALHA', 404, '2026-10-05 12:03:00.000', '2026-10-05 12:03:00.031', 31.00,
     NULL, NULL, NULL, NULL),
    -- Chamada sem os headers de contexto: alimenta o indicador de cobertura de contexto.
    ('55555555-5555-4555-8555-555555555555', 'sem-sessao', 'desconhecida', 'GET',
     '/v1/sensores/M-101/leitura-atual', 'M-101',
     'CONCLUIDA', 200, '2026-10-05 12:04:00.000', '2026-10-05 12:04:00.120', 120.00,
     'ok', 9.80, 1.0000, 1)
ON DUPLICATE KEY UPDATE call_id = VALUES(call_id);
