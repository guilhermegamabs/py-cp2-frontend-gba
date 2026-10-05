import os

# Base da API. Sem barra no fim: a camada `api/` monta o caminho a partir daqui.
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/v1").rstrip("/")

# Timeout de toda chamada. Sem ele, API pendurada travaria a interface sem mensagem.
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))

# Só para colorir a tela; a autoridade sobre limiar é a API.
SEVERITY_COLORS = {
    "ok": "#22C55E",
    "warn": "#EAB308",
    "crit": "#EF4444",
    "off": "#A3A3A3",
    "desconhecida": "#3B82F6",
}
