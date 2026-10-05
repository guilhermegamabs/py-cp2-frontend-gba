import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config.cors_config import configure_cors
from core.config.database import check_connection
from core.config.settings import settings
from core.controller.observability.observability_controller import router as observability_router
from core.controller.sensor.sensor_controller import router as sensor_router
from core.exception.exception_handlers import register_exception_handlers
from core.observability.observability_middleware import ObservabilityMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Falha alto: sem banco, a API perderia todo registro em silêncio.
    check_connection()
    yield


app = FastAPI(
    title="Sensor Monitoring API",
    version="1.0.0",
    description=(
        "Expõe o provider de Sensores do Digital Twin Forzy (leitura atual e histórico) e "
        "o relatório de observabilidade das chamadas recebidas."
    ),
    lifespan=lifespan,
)

configure_cors(app)
# Depois do CORS, portanto por dentro dele: o preflight não vira registro.
app.add_middleware(ObservabilityMiddleware)
register_exception_handlers(app)

app.include_router(sensor_router, prefix=settings.api_prefix)
app.include_router(observability_router, prefix=settings.api_prefix)


@app.get("/saude", tags=["Infraestrutura"], summary="Healthcheck")
def health() -> dict:
    return {"status": "ok", "aplicacao": settings.app_name}
