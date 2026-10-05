import os
from dataclasses import dataclass, field


def _env_float(name: str, default: float) -> float:
    return float(os.getenv(name, default))


def _env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class DatabaseSettings:
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "3306")))
    user: str = field(default_factory=lambda: os.getenv("DB_USERNAME", "root"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", "root"))
    database: str = field(default_factory=lambda: os.getenv("DB_NAME", "sensor_db"))


@dataclass(frozen=True)
class ObservabilitySlo:
    # Acima disso a leitura é considerada velha (indicador de freshness).
    max_freshness_seconds: float = field(
        default_factory=lambda: _env_float("SLO_MAX_FRESHNESS_SECONDS", 120.0)
    )
    # Abaixo disso o snapshot é considerado incompleto (indicador de completude).
    min_completeness_ratio: float = field(
        default_factory=lambda: _env_float("SLO_MIN_COMPLETENESS_RATIO", 0.80)
    )
    # Acima disso a chamada é considerada lenta (indicador de latência).
    max_latency_ms: float = field(
        default_factory=lambda: _env_float("SLO_MAX_LATENCY_MS", 500.0)
    )
    # Abaixo disso a disponibilidade da janela é considerada degradada.
    min_success_ratio: float = field(
        default_factory=lambda: _env_float("SLO_MIN_SUCCESS_RATIO", 0.99)
    )
    # Toda chamada tem de chegar com X-Session-Id e X-Feature: o limiar é 100%.
    min_context_coverage: float = field(
        default_factory=lambda: _env_float("SLO_MIN_CONTEXT_COVERAGE", 1.0)
    )


@dataclass(frozen=True)
class Settings:
    app_name: str = "sensor-monitoring-api"
    api_prefix: str = "/v1"
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    # Nunca `*`: com credencial o navegador recusa curinga.
    cors_allowed_origins: list[str] = field(
        default_factory=lambda: _env_list(
            "CORS_ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501"
        )
    )
    slo: ObservabilitySlo = field(default_factory=ObservabilitySlo)


settings = Settings()
