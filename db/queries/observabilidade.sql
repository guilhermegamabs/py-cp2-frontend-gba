-- Catalogo de consultas do relatorio: conferencia manual do que o ObservabilityService calcula.

USE sensor_db;

-- Volume de chamadas por hora. Camada grafica sugerida: barra.
SELECT DATE_FORMAT(started_at, '%Y-%m-%d %H:00') AS hora,
       COUNT(*)                                  AS chamadas
  FROM sensor_tb_request_processing
 GROUP BY hora
 ORDER BY hora;

-- Latencia media e percentil 95 aproximado por funcionalidade. Camada grafica: linha.
SELECT feature                     AS funcionalidade,
       COUNT(*)                    AS chamadas,
       ROUND(AVG(latency_ms), 2)   AS latencia_media_ms,
       ROUND(MAX(latency_ms), 2)   AS latencia_maxima_ms
  FROM sensor_tb_request_processing
 WHERE processing_status <> 'EM_PROCESSAMENTO'
 GROUP BY feature
 ORDER BY latencia_media_ms DESC;

-- Taxa de sucesso da janela. Limiar de referencia: 0.99.
SELECT COUNT(*)                                                        AS total,
       SUM(http_status < 400)                                          AS sucesso,
       ROUND(SUM(http_status < 400) / COUNT(*), 4)                     AS taxa_sucesso
  FROM sensor_tb_request_processing
 WHERE http_status IS NOT NULL;

-- Freshness medio e taxa de completude de freshness. Limiares: 120 s e 0.80.
SELECT ROUND(AVG(freshness_seconds), 2)                                        AS freshness_medio_s,
       ROUND(SUM(freshness_seconds <= 120 AND completeness_ratio >= 1) / COUNT(*), 4)
                                                                               AS taxa_completude_freshness
  FROM sensor_tb_request_processing
 WHERE freshness_seconds IS NOT NULL;

-- Cobertura dos headers de contexto. Chamada sem contexto nao e rastreavel.
SELECT ROUND(SUM(session_id <> 'sem-sessao' AND feature <> 'desconhecida') / COUNT(*), 4)
           AS cobertura_contexto
  FROM sensor_tb_request_processing;

-- Severidade retornada por ativo: cruza governanca com o estado real da planta.
SELECT tag, severity, COUNT(*) AS ocorrencias
  FROM sensor_tb_request_processing
 WHERE tag IS NOT NULL AND severity IS NOT NULL
 GROUP BY tag, severity
 ORDER BY tag, ocorrencias DESC;

-- Requisicoes que nunca fecharam. Linha presa em EM_PROCESSAMENTO indica queda no meio do processamento.
SELECT call_id, path, started_at, TIMESTAMPDIFF(SECOND, started_at, NOW()) AS segundos_aberta
  FROM sensor_tb_request_processing
 WHERE processing_status = 'EM_PROCESSAMENTO'
 ORDER BY started_at;
