from core.api import http_client
from core.enums.feature import Feature
from core.types.sensor import SensorHistory, SensorReading, SensorSummary


def list_sensors(session_id: str) -> list[SensorSummary]:
    return http_client.get("/sensores", session_id, Feature.CURRENT_READING)


def get_current_reading(session_id: str, tag: str) -> SensorReading:
    return http_client.get(f"/sensores/{tag}/leitura-atual", session_id, Feature.CURRENT_READING)


def get_history(session_id: str, tag: str, hours: int, interval_minutes: int) -> SensorHistory:
    # Nome do parâmetro é o alias que a API declara, não o nome interno dela.
    return http_client.get(
        f"/sensores/{tag}/historico",
        session_id,
        Feature.HISTORY,
        params={"hours": hours, "intervalo_minutos": interval_minutes},
    )
