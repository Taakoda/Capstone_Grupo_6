# scripts/ci/check_engine_creation.py
"""Falla si create_async_engine() aparece fuera de db.py (KC-BE-01-1)."""

import pathlib
import sys

RAICES = ["apps", "packages"]
ARCHIVO_PERMITIDO = "db.py"


def main() -> int:
    errores = []
    for raiz in RAICES:
        for path in pathlib.Path(raiz).rglob("*.py"):
            if path.name == ARCHIVO_PERMITIDO:
                continue
            if "__pycache__" in path.parts:
                continue
            for i, linea in enumerate(path.read_text().splitlines(), 1):
                if "create_async_engine(" in linea:
                    errores.append(
                        f"{path}:{i}: create_async_engine() debe estar solo en {ARCHIVO_PERMITIDO}"
                    )
    if errores:
        print("\n".join(errores))
        return 1
    print("OK: create_async_engine() solo aparece en db.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
