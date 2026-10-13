"""Aplica os scripts SQL versionados usando o driver do projeto.

Existe porque o cliente `mysql` não está no PATH numa instalação padrão do MySQL no
Windows, e sem ele o passo 3 do README falha na máquina de avaliação. O PyMySQL já é
dependência do back-end, então não acrescenta nada ao ambiente.

    python db/aplicar_schema.py           # só o schema
    python db/aplicar_schema.py --seed    # schema + dados de exemplo
"""

import argparse
import os
import sys
from pathlib import Path

import pymysql

_SCRIPTS = Path(__file__).resolve().parent


def _statements(path: Path) -> list[str]:
    # Linha de comentário fora: `--` no início de um bloco faria o split engolir o comando.
    sql = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.strip().startswith("--")
    )
    return [statement.strip() for statement in sql.split(";") if statement.strip()]


def _run(path: Path) -> None:
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            for statement in _statements(path):
                cursor.execute(statement)
    finally:
        connection.close()
    print(f"OK  {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Aplica os scripts SQL do sensor_db.")
    parser.add_argument("--seed", action="store_true", help="Também aplica V2__seed.sql.")
    args = parser.parse_args()

    scripts = [_SCRIPTS / "V1__schema.sql"]
    if args.seed:
        scripts.append(_SCRIPTS / "V2__seed.sql")

    for script in scripts:
        try:
            _run(script)
        except Exception as exc:
            # V1 não é reexecutável de propósito: dizer isso evita "erro" que não é erro.
            print(f"ERRO ao aplicar {script.name}: {exc}", file=sys.stderr)
            print(
                "Se a tabela já existe, o schema já foi aplicado. Para recomeçar do zero: "
                "mysql -u root -proot < db/reset.sql (DESTRUTIVO).",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
