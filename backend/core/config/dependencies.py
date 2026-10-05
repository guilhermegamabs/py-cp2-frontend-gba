from core.mapper.observability_mapper import ObservabilityMapper
from core.mapper.sensor_mapper import SensorMapper
from core.service.observability_service import ObservabilityService
from core.service.sensor_service import SensorService

# Instância única por processo: nada aqui guarda estado de requisição.
_sensor_service = SensorService()
_sensor_mapper = SensorMapper()
_observability_service = ObservabilityService()
_observability_mapper = ObservabilityMapper()


def get_sensor_service() -> SensorService:
    return _sensor_service


def get_sensor_mapper() -> SensorMapper:
    return _sensor_mapper


def get_observability_service() -> ObservabilityService:
    return _observability_service


def get_observability_mapper() -> ObservabilityMapper:
    return _observability_mapper
