# Este módulo contiene la lógica para manejar las zonas de riesgo, 
# puntos de escape y resúmenes relacionados al mapa.
# No debe contener lógica de entrenamiento, generación de HTML o apertura de navegador.

import json
import os
from pathlib import Path

from app.data.mapa_demo_data import PUNTOS_ESCAPE
from app.services.route_geo_utils import obtener_punto_escape_mas_cercano


def obtener_archivo_colonias() -> Path:
    """
    Localiza el catálogo de colonias.
    En Docker utiliza DATA_DIR=/workspace/data.
    """
    candidatos = []

    data_dir = os.getenv("DATA_DIR")
    if data_dir:
        candidatos.append(
            Path(data_dir) / "geo" / "colonias_gdl.json"
        )

    project_root = os.getenv("PROJECT_ROOT")
    if project_root:
        candidatos.append(
            Path(project_root) / "data" / "geo" / "colonias_gdl.json"
        )

    # Fallback para ejecución local.
    for parent in Path(__file__).resolve().parents:
        candidatos.append(
            parent / "data" / "geo" / "colonias_gdl.json"
        )

    for ruta in candidatos:
        if ruta.is_file():
            return ruta

    raise FileNotFoundError(
        "No se encontró data/geo/colonias_gdl.json. "
        f"Rutas revisadas: {candidatos}"
    )


def cargar_colonias():
    """
    Carga las 285 colonias y sus datos de riesgo.
    """
    ruta = obtener_archivo_colonias()

    with ruta.open("r", encoding="utf-8") as archivo:
        colonias = json.load(archivo)

    if not isinstance(colonias, list):
        raise ValueError("El catálogo de colonias debe ser una lista.")

    return colonias


def obtener_color_y_radio_por_riesgo(riesgo: int):
    """
    Mantiene los cuatro niveles de riesgo del frontend.
    """
    if riesgo >= 76:
        return {
            "nivel": "muy_alto",
            "color": "red",
            "radio": 550,
        }

    if riesgo >= 51:
        return {
            "nivel": "alto",
            "color": "orange",
            "radio": 450,
        }

    if riesgo >= 26:
        return {
            "nivel": "moderado",
            "color": "yellow",
            "radio": 350,
        }

    return {
        "nivel": "bajo",
        "color": "green",
        "radio": 250,
    }


def listar_zonas_riesgo():
    """
    Devuelve todas las colonias del catálogo con:
    coordenadas, riesgo, nivel, color y escape sugerido.
    """
    colonias = cargar_colonias()
    zonas = []

    for index, colonia in enumerate(colonias):
        nombre = colonia.get("nombre_colonia")
        centro = colonia.get("centro")
        riesgo = colonia.get("riesgo")

        if not nombre or not isinstance(centro, list) or len(centro) != 2:
            raise ValueError(
                f"Registro inválido en el catálogo, posición {index}: {colonia}"
            )

        # El JSON guarda las coordenadas como [longitud, latitud].
        longitud, latitud = map(float, centro)
        riesgo = int(round(float(riesgo)))

        if not 0 <= riesgo <= 100:
            raise ValueError(
                f"Riesgo inválido para {nombre}: {riesgo}"
            )

        estilo = obtener_color_y_radio_por_riesgo(riesgo)

        escape_sugerido = None

        if riesgo >= 51:
            escape_sugerido = obtener_punto_escape_mas_cercano(
                coordenadas_origen=(latitud, longitud),
                puntos_escape=PUNTOS_ESCAPE,
            )

        zonas.append({
            "zona": nombre,
            "nombre": nombre,
            "latitud": latitud,
            "longitud": longitud,
            "riesgo": riesgo,
            "nivel": estilo["nivel"],
            "color": estilo["color"],
            "radio": estilo["radio"],
            "escape_sugerido": escape_sugerido,
        })

    return zonas


def listar_puntos_escape():
    """
    Regresa los puntos de escape disponibles.
    """
    return [
        {
            "nombre": nombre,
            "latitud": coordenadas[0],
            "longitud": coordenadas[1],
        }
        for nombre, coordenadas in PUNTOS_ESCAPE.items()
    ]


def obtener_resumen_mapa():
    """
    Resumen de las zonas según su nivel de riesgo.
    """
    zonas = listar_zonas_riesgo()

    total_muy_alto = sum(
        zona["nivel"] == "muy_alto" for zona in zonas
    )
    total_alto = sum(
        zona["nivel"] == "alto" for zona in zonas
    )
    total_moderado = sum(
        zona["nivel"] == "moderado" for zona in zonas
    )
    total_bajo = sum(
        zona["nivel"] == "bajo" for zona in zonas
    )

    return {
        "total_zonas": len(zonas),
        "zonas_alto_riesgo": total_alto + total_muy_alto,
        "zonas_muy_alto_riesgo": total_muy_alto,
        "zonas_riesgo_medio": total_moderado,
        "zonas_bajo_riesgo": total_bajo,
    }
