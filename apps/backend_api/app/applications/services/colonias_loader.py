import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent


def cargar_colonias_desde_json(nombre_archivo: str, estado: str | None = None, municipio: str | None = None):
    ruta_json = DATA_DIR / nombre_archivo

    with open(ruta_json, "r", encoding="utf-8") as f:
        colonias = json.load(f)

    colonias_limpias = []

    for colonia in colonias:
        try:
            item = {
                "id": int(colonia["id"]),
                "estado": str(colonia["estado"]).strip(),
                "municipio": str(colonia["municipio"]).strip(),
                "nombre_colonia": str(colonia["nombre_colonia"]).strip(),
                "lat": float(colonia["lat"]),
                "lon": float(colonia["lon"]),
                "riesgo": float(colonia["riesgo"]),
            }
        except (KeyError, TypeError, ValueError):
            continue

        if estado and item["estado"].lower() != estado.lower():
            continue

        if municipio and item["municipio"].lower() != municipio.lower():
            continue

        colonias_limpias.append(item)

    return colonias_limpias


def cargar_todas_las_colonias():
    colonias_totales = []

    for archivo in DATA_DIR.glob("*.json"):
        try:
            colonias_totales.extend(cargar_colonias_desde_json(archivo.name))
        except Exception:
            continue

    return colonias_totales