from dataclasses import dataclass
from datetime import datetime

from core.enums.processing_status import ProcessingStatus


@dataclass
class RequestProcessing:
    call_id: str
    session_id: str
    feature: str
    method: str
    path: str
    started_at: datetime
    processing_status: ProcessingStatus = ProcessingStatus.IN_PROGRESS
    tag: str | None = None
    http_status: int | None = None
    finished_at: datetime | None = None
    latency_ms: float | None = None
    severity: str | None = None
    freshness_seconds: float | None = None
    completeness_ratio: float | None = None
    points: int | None = None
    error_message: str | None = None
