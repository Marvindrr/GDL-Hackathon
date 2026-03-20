import json
from pathlib import Path


def cargar_colonias_desde_json():
    ruta_json = Path(__file__).resolve().parent.parent / "data" / "colonias_gdl.json"

    with open(ruta_json, "r", encoding="utf-8") as f:
        colonias = json.load(f)

    colonias_limpias = []

    for colonia in colonias:
        nombre = colonia.get("nombre_colonia")
        centro = colonia.get("centro")
        riesgo = colonia.get("riesgo")

        if not nombre or not centro or riesgo is None:
            continue

        if not isinstance(centro, list) or len(centro) != 2:
            continue

        lon, lat = centro

        colonias_limpias.append({
            "nombre_colonia": nombre,
            "lat": lat,
            "lon": lon,
            "riesgo": riesgo
        })

    return colonias_limpias