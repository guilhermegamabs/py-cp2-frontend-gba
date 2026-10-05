import argparse
import random
import sys
import time
import uuid
from pathlib import Path

import requests

# O script vive fora de `frontend/`, então o pacote `core` precisa entrar no path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "frontend"))

from core.api import observability_api, sensor_api  # noqa: E402
from core.config.settings import API_BASE_URL  # noqa: E402
from core.types.api import ApiError  # noqa: E402


def main() -> int:
    args = _parse_args()
    session_id = args.sessao or f"script-{uuid.uuid4().hex[:8]}"

    print(f"API:    {API_BASE_URL}")
    print(f"Sessão: {session_id}")
    print("-" * 72)

    try:
        sensors = sensor_api.list_sensors(session_id)
    except ApiError as error:
        print(f"[ERRO {error.status}] {error.message}")
        return 1

    tags = [sensor["tag"] for sensor in sensors]
    print(f"Ativos monitorados ({len(tags)}): {', '.join(tags)}\n")

    for round_number in range(1, args.rodadas + 1):
        tag = random.choice(tags)
        _consume_current_reading(session_id, tag, round_number)
        _consume_history(session_id, tag, round_number)
        if round_number < args.rodadas:
            # Espaça as chamadas: série com um instante só não mostra tendência.
            time.sleep(args.intervalo)

    if args.anomalias:
        _generate_anomalies(args.anomalias)

    _consume_observability(session_id)
    return 0


def _generate_anomalies(quantity: int) -> None:
    print("-" * 72)
    print(f"Injetando {quantity} chamada(s) sem headers de contexto e {quantity} com tag inexistente")

    for _ in range(quantity):
        # Cliente que não instrumenta: derruba o indicador de cobertura de contexto.
        requests.get(f"{API_BASE_URL}/sensores/M-101/leitura-atual", timeout=10)

    for index in range(quantity):
        # Tag inexistente: 404 legítimo, alimenta a taxa de sucesso.
        requests.get(
            f"{API_BASE_URL}/sensores/M-{900 + index}/leitura-atual",
            headers={"X-Session-Id": "anomalia-tag-invalida", "X-Feature": "leitura-atual"},
            timeout=10,
        )


def _consume_current_reading(session_id: str, tag: str, round_number: int) -> None:
    try:
        reading = sensor_api.get_current_reading(session_id, tag)
    except ApiError as error:
        print(f"[{round_number:>3}] leitura-atual  {tag}  ERRO {error.status}: {error.message}")
        return
    print(
        f"[{round_number:>3}] leitura-atual  {reading['tag']}  "
        f"severidade={reading['severidade']:<12} "
        f"completude={reading['taxa_completude']:.0%}  "
        f"freshness={reading['freshness_segundos']:.0f}s"
    )


def _consume_history(session_id: str, tag: str, round_number: int) -> None:
    try:
        history = sensor_api.get_history(session_id, tag, hours=24, interval_minutes=60)
    except ApiError as error:
        print(f"[{round_number:>3}] historico      {tag}  ERRO {error.status}: {error.message}")
        return
    severities = [point["severidade"] for point in history["pontos"]]
    criticals = sum(1 for severity in severities if severity == "crit")
    print(
        f"[{round_number:>3}] historico      {history['tag']}  "
        f"pontos={history['total_pontos']:<4} pontos_criticos={criticals}"
    )


def _consume_observability(session_id: str) -> None:
    print("-" * 72)
    try:
        report = observability_api.get_report(session_id, limit=5)
    except ApiError as error:
        print(f"[ERRO {error.status}] {error.message}")
        return

    print(f"Relatório de observabilidade — {report['total_chamadas']} chamadas na base\n")
    for indicator in report["indicadores"]:
        verdict = {True: "conforme", False: "ESTOURADO", None: "sem dado"}[indicator["conforme"]]
        value = "—" if indicator["valor"] is None else f"{indicator['valor']:g}"
        print(
            f"  {indicator['codigo']:<28} {value:>10} {indicator['unidade']:<9} "
            f"{indicator['operador']} {indicator['limiar']:<8} {verdict}"
        )

    print("\n  Chamadas por funcionalidade:")
    for feature, total in sorted(report["chamadas_por_funcionalidade"].items()):
        print(f"    {feature:<20} {total}")

    print("\n  Últimos registros:")
    for record in report["registros"]:
        print(
            f"    {record['iniciado_em']}  {record['funcionalidade']:<16} "
            f"{record['status_processamento']:<18} http={record['status_http']}  "
            f"{record['latencia_ms']} ms"
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consome os endpoints da Sensor Monitoring API.")
    parser.add_argument("--rodadas", type=int, default=1, help="Quantas passadas de consumo.")
    parser.add_argument("--intervalo", type=float, default=1.0, help="Pausa entre rodadas, em s.")
    parser.add_argument("--sessao", type=str, default=None, help="Valor fixo para X-Session-Id.")
    parser.add_argument(
        "--anomalias", type=int, default=0,
        help="Chamadas fora do contrato (sem headers e com tag inexistente), para a coleta.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
