from contextvars import ContextVar

from core.model.request_processing import RequestProcessing

_CURRENT: ContextVar[RequestProcessing | None] = ContextVar("current_processing", default=None)


def bind(processing: RequestProcessing) -> None:
    _CURRENT.set(processing)


def current() -> RequestProcessing | None:
    return _CURRENT.get()


def describe(
    tag: str | None = None,
    severity: str | None = None,
    freshness_seconds: float | None = None,
    completeness_ratio: float | None = None,
    points: int | None = None,
) -> None:
    processing = _CURRENT.get()
    if processing is None:
        return
    if tag is not None:
        processing.tag = tag
    if severity is not None:
        processing.severity = severity
    if freshness_seconds is not None:
        processing.freshness_seconds = freshness_seconds
    if completeness_ratio is not None:
        processing.completeness_ratio = completeness_ratio
    if points is not None:
        processing.points = points
