import requests

from core.config.settings import API_BASE_URL, REQUEST_TIMEOUT_SECONDS
from core.types.api import ApiError, FieldError

# Única camada que conhece `requests`: nenhuma view importa esta biblioteca.
_session = requests.Session()


def get(path: str, session_id: str, feature: str, params: dict | None = None) -> dict | list:
    url = f"{API_BASE_URL}{path}"
    headers = {"X-Session-Id": session_id, "X-Feature": feature, "Accept": "application/json"}
    try:
        response = _session.get(
            url, params=params, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.RequestException as exc:
        # Sem resposta do servidor: status 0 com mensagem própria, não exceção crua.
        raise ApiError(
            status=0,
            message=(
                f"Não foi possível falar com a API em {API_BASE_URL}. "
                "Confira se o backend está no ar (uvicorn main:app --reload)."
            ),
            path=path,
            error=type(exc).__name__,
        ) from exc

    if response.status_code >= 400:
        raise _to_api_error(response, path)
    return response.json()


def _to_api_error(response: requests.Response, path: str) -> ApiError:
    try:
        body = response.json()
    except ValueError:
        return ApiError(
            status=response.status_code,
            message=f"A API respondeu {response.status_code} sem corpo interpretável.",
            path=path,
        )
    return ApiError(
        status=body.get("status", response.status_code),
        message=body.get("message", "Erro ao consultar a API."),
        path=body.get("path", path),
        error=body.get("error", ""),
        timestamp=body.get("timestamp", ""),
        field_errors=[
            FieldError(campo=item.get("campo", ""), mensagem=item.get("mensagem", ""))
            for item in body.get("field_errors", [])
        ],
    )
