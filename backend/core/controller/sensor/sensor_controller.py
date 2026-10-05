from fastapi import APIRouter, Depends, Path

from core.config.dependencies import get_sensor_mapper, get_sensor_service
from core.dto.request.history_query import HistoryQuery
from core.dto.response.sensor_response import (
    SensorHistoryResponse,
    SensorReadingResponse,
    SensorSummaryResponse,
)
from core.exception.error_response import ErrorResponse
from core.mapper.sensor_mapper import SensorMapper
from core.service.sensor_service import SensorService

router = APIRouter(prefix="/sensores", tags=["Sensores"])

# Rota literal antes de `/{tag}`, senão `leitura-atual` seria capturado como tag.
_TAG_PATH = Path(description="Tag do ativo monitorado, por exemplo M-101.", examples=["M-101"])

_ERRORS = {404: {"model": ErrorResponse, "description": "Tag inexistente no provider."}}


@router.get(
    "",
    response_model=list[SensorSummaryResponse],
    summary="Lista os ativos monitorados",
)
def list_sensors(
    service: SensorService = Depends(get_sensor_service),
    mapper: SensorMapper = Depends(get_sensor_mapper),
) -> list[SensorSummaryResponse]:
    return [mapper.to_summary(sensor) for sensor in service.list_sensors()]


@router.get(
    "/{tag}/leitura-atual",
    response_model=SensorReadingResponse,
    responses=_ERRORS,
    summary="Leitura atual do ativo, com severidade por grandeza",
)
def get_current_reading(
    tag: str = _TAG_PATH,
    service: SensorService = Depends(get_sensor_service),
    mapper: SensorMapper = Depends(get_sensor_mapper),
) -> SensorReadingResponse:
    return mapper.to_response(service.get_current_reading(tag))


@router.get(
    "/{tag}/historico",
    response_model=SensorHistoryResponse,
    responses=_ERRORS,
    summary="Série histórica do ativo na janela pedida",
)
def get_history(
    tag: str = _TAG_PATH,
    query: HistoryQuery = Depends(),
    service: SensorService = Depends(get_sensor_service),
    mapper: SensorMapper = Depends(get_sensor_mapper),
) -> SensorHistoryResponse:
    sensor, readings = service.get_history(tag, query.hours, query.interval_minutes)
    return mapper.to_history_response(sensor, readings, query.hours, query.interval_minutes)
