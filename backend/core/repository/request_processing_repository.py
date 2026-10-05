from datetime import datetime, timezone

from core.config.database import connection
from core.enums.processing_status import ProcessingStatus
from core.model.request_processing import RequestProcessing

_INSERT = """
INSERT INTO sensor_tb_request_processing
       (call_id, session_id, feature, method, path, tag, processing_status, started_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

_UPDATE_FINISH = """
UPDATE sensor_tb_request_processing
   SET processing_status  = %s,
       http_status        = %s,
       finished_at        = %s,
       latency_ms         = %s,
       tag                = %s,
       severity           = %s,
       freshness_seconds  = %s,
       completeness_ratio = %s,
       points             = %s,
       error_message      = %s
 WHERE call_id = %s
"""

_COLUMNS = """
       call_id, session_id, feature, method, path, tag, processing_status, http_status,
       started_at, finished_at, latency_ms, severity, freshness_seconds,
       completeness_ratio, points, error_message
"""

# Filtro opcional `(%s IS NULL OR coluna = %s)`: sem montar SQL por concatenação.
_WHERE = """
 WHERE (%s IS NULL OR session_id = %s)
   AND (%s IS NULL OR feature = %s)
   AND (%s IS NULL OR tag = %s)
   AND (%s IS NULL OR started_at >= %s)
"""


class RequestProcessingRepository:
    def start(self, processing: RequestProcessing) -> None:
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    _INSERT,
                    (
                        processing.call_id,
                        processing.session_id,
                        processing.feature,
                        processing.method,
                        processing.path,
                        processing.tag,
                        ProcessingStatus.IN_PROGRESS.value,
                        self._to_db(processing.started_at),
                    ),
                )

    def finish(self, processing: RequestProcessing) -> None:
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    _UPDATE_FINISH,
                    (
                        processing.processing_status.value,
                        processing.http_status,
                        self._to_db(processing.finished_at),
                        processing.latency_ms,
                        processing.tag,
                        processing.severity,
                        processing.freshness_seconds,
                        processing.completeness_ratio,
                        processing.points,
                        processing.error_message,
                        processing.call_id,
                    ),
                )

    def find_all(
        self,
        session_id: str | None = None,
        feature: str | None = None,
        tag: str | None = None,
        since: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> list[RequestProcessing]:
        sql = f"SELECT {_COLUMNS} FROM sensor_tb_request_processing {_WHERE} ORDER BY started_at DESC LIMIT %s OFFSET %s"
        params = (*self._filter_params(session_id, feature, tag, since), limit, offset)
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        return [self._to_model(row) for row in rows]

    def count(
        self,
        session_id: str | None = None,
        feature: str | None = None,
        tag: str | None = None,
        since: datetime | None = None,
    ) -> int:
        sql = f"SELECT COUNT(*) AS total FROM sensor_tb_request_processing {_WHERE}"
        with connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, self._filter_params(session_id, feature, tag, since))
                row = cursor.fetchone()
        return int(row["total"])

    @classmethod
    def _filter_params(cls, session_id, feature, tag, since) -> tuple:
        moment = cls._to_db(since)
        return (session_id, session_id, feature, feature, tag, tag, moment, moment)

    @staticmethod
    def _to_db(moment: datetime | None) -> datetime | None:
        if moment is None:
            return None
        if moment.tzinfo is None:
            return moment
        return moment.astimezone(timezone.utc).replace(tzinfo=None)

    @staticmethod
    def _from_db(moment: datetime | None) -> datetime | None:
        return moment.replace(tzinfo=timezone.utc) if moment else None

    @classmethod
    def _to_model(cls, row: dict) -> RequestProcessing:
        return RequestProcessing(
            call_id=row["call_id"],
            session_id=row["session_id"],
            feature=row["feature"],
            method=row["method"],
            path=row["path"],
            started_at=cls._from_db(row["started_at"]),
            processing_status=ProcessingStatus(row["processing_status"]),
            tag=row["tag"],
            http_status=row["http_status"],
            finished_at=cls._from_db(row["finished_at"]),
            # DECIMAL volta como Decimal; o DTO é float e o JSON não serializa Decimal.
            latency_ms=float(row["latency_ms"]) if row["latency_ms"] is not None else None,
            severity=row["severity"],
            freshness_seconds=(
                float(row["freshness_seconds"]) if row["freshness_seconds"] is not None else None
            ),
            completeness_ratio=(
                float(row["completeness_ratio"]) if row["completeness_ratio"] is not None else None
            ),
            points=row["points"],
            error_message=row["error_message"],
        )
