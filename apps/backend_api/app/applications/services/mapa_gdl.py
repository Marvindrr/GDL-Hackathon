import math
from typing import Any


Coord = tuple[float, float]


def calcular_distancia_km(coord1: Coord, coord2: Coord) -> float:
    radio_tierra_km = 6371
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return radio_tierra_km * c


def calcular_ruta(
    origen: dict[str, Any] | None,
    destino: dict[str, Any] | None,
    tipo_ruta: str,
    colonias: list[dict[str, Any]],
) -> dict[str, Any]:
    punto_origen = _normalizar_punto(origen, "origen")
    punto_destino = _normalizar_punto(destino, "destino")
    tipo = _normalizar_tipo_ruta(tipo_ruta)

    ruta = _construir_ruta_demo(punto_origen, punto_destino, tipo)
    distancia = calcular_distancia_km(
        (punto_origen["lat"], punto_origen["lon"]),
        (punto_destino["lat"], punto_destino["lon"]),
    )
    tiempo_min = _estimar_tiempo_min(distancia, tipo)
    riesgo = _estimar_riesgo(punto_origen, punto_destino, tipo)
    colonias_criticas = _colonias_criticas_cercanas(ruta, colonias)

    return {
        "origen": punto_origen["nombre"],
        "destino": punto_destino["nombre"],
        "tipo_ruta": tipo,
        "riesgo_total": _etiqueta_riesgo(riesgo),
        "riesgo_valor": round(riesgo, 1),
        "distancia": f"{distancia:.2f} km",
        "distancia_km": round(distancia, 2),
        "tiempo": f"{tiempo_min} min",
        "tiempo_min": tiempo_min,
        "colonias_criticas": colonias_criticas,
        "ruta": ruta,
    }


def _normalizar_punto(punto: dict[str, Any] | None, campo: str) -> dict[str, Any]:
    if not isinstance(punto, dict):
        raise ValueError(f"Falta el punto de {campo}.")

    try:
        lat = float(punto["lat"])
        lon_valor = punto.get("lon")
        if lon_valor is None:
            lon_valor = punto.get("lng")
        lon = float(lon_valor)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"El punto de {campo} no tiene coordenadas validas.") from exc

    nombre = str(punto.get("nombre") or punto.get("nombre_colonia") or campo).strip()
    if not nombre:
        nombre = campo

    return {
        "nombre": nombre,
        "lat": lat,
        "lon": lon,
        "riesgo": _numero_o_none(punto.get("riesgo")),
    }


def _normalizar_tipo_ruta(tipo_ruta: str | None) -> str:
    tipo = (tipo_ruta or "segura").strip().lower()
    if tipo not in {"segura", "rapida"}:
        raise ValueError("El tipo de ruta debe ser 'segura' o 'rapida'.")
    return tipo


def _construir_ruta_demo(origen: dict[str, Any], destino: dict[str, Any], tipo: str):
    mid_lat = (origen["lat"] + destino["lat"]) / 2
    mid_lon = (origen["lon"] + destino["lon"]) / 2
    offset = 0.015 if tipo == "segura" else -0.008

    return [
        [origen["lat"], origen["lon"]],
        [mid_lat + offset, mid_lon - offset],
        [destino["lat"], destino["lon"]],
    ]


def _estimar_tiempo_min(distancia_km: float, tipo: str) -> int:
    factor = 3.9 if tipo == "segura" else 3.2
    return max(5, round(distancia_km * factor))


def _estimar_riesgo(origen: dict[str, Any], destino: dict[str, Any], tipo: str) -> float:
    riesgos = [
        riesgo
        for riesgo in (origen.get("riesgo"), destino.get("riesgo"))
        if riesgo is not None
    ]
    base = sum(riesgos) / len(riesgos) if riesgos else 45.0

    if tipo == "segura":
        return max(0.0, base * 0.85)

    return min(100.0, base * 1.08)


def _etiqueta_riesgo(riesgo: float) -> str:
    if riesgo <= 25:
        return "Bajo"
    if riesgo <= 50:
        return "Moderado"
    if riesgo <= 75:
        return "Alto"
    return "Muy alto"


def _colonias_criticas_cercanas(
    ruta: list[list[float]],
    colonias: list[dict[str, Any]],
    radio_km: float = 1.5,
):
    candidatas = []

    for colonia in colonias:
        riesgo = _numero_o_none(colonia.get("riesgo"))
        if riesgo is None or riesgo < 51:
            continue

        try:
            coord_colonia = (float(colonia["lat"]), float(colonia["lon"]))
        except (KeyError, TypeError, ValueError):
            continue

        distancia_minima = min(
            calcular_distancia_km((float(lat), float(lon)), coord_colonia)
            for lat, lon in ruta
        )

        if distancia_minima <= radio_km:
            candidatas.append(
                {
                    "nombre": colonia["nombre_colonia"],
                    "riesgo": riesgo,
                    "distancia": distancia_minima,
                }
            )

    candidatas.sort(key=lambda item: (-item["riesgo"], item["distancia"]))

    return [item["nombre"] for item in candidatas[:3]]


def _numero_o_none(valor: Any) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None
