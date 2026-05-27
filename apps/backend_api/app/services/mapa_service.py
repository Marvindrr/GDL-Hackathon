# Este módulo contiene la lógica para manejar las zonas de riesgo, 
# puntos de escape y resúmenes relacionados al mapa.
# No debe contener lógica de entrenamiento, generación de HTML o apertura de navegador.

from app.data.mapa_demo_data import PUNTOS_ZONAS, DATOS_RIESGO, PUNTOS_ESCAPE
from app.services.route_geo_utils import obtener_punto_escape_mas_cercano


def obtener_color_y_radio_por_riesgo(riesgo: int):
    """
    Define color y radio visual según nivel de riesgo.
    """
    if riesgo >= 60:
        return {
            "nivel": "alto",
            "color": "red",
            "radio": 450,
        }

    if 40 <= riesgo < 60:
        return {
            "nivel": "medio",
            "color": "orange",
            "radio": 350,
        }

    return {
        "nivel": "bajo",
        "color": "green",
        "radio": 250,
    }


def listar_zonas_riesgo():
    """
    Regresa las zonas con coordenadas, riesgo, nivel, color y ruta de escape sugerida.
    Esta función es segura para usarse desde FastAPI.
    No entrena modelos, no genera HTML y no abre navegador.
    """
    zonas = []

    for nombre_zona, coordenadas in PUNTOS_ZONAS.items():
        riesgo = DATOS_RIESGO.get(nombre_zona, 0)
        estilo = obtener_color_y_radio_por_riesgo(riesgo)

        zona = {
            "zona": nombre_zona,
            "latitud": coordenadas[0],
            "longitud": coordenadas[1],
            "riesgo": riesgo,
            "nivel": estilo["nivel"],
            "color": estilo["color"],
            "radio": estilo["radio"],
            "escape_sugerido": None,
        }

        if riesgo >= 60:
            zona["escape_sugerido"] = obtener_punto_escape_mas_cercano(
                coordenadas_origen=coordenadas,
                puntos_escape=PUNTOS_ESCAPE,
            )

        zonas.append(zona)

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
    Regresa un resumen simple para dashboard o pruebas.
    """
    zonas = listar_zonas_riesgo()

    total_zonas = len(zonas)
    total_alto = len([zona for zona in zonas if zona["nivel"] == "alto"])
    total_medio = len([zona for zona in zonas if zona["nivel"] == "medio"])
    total_bajo = len([zona for zona in zonas if zona["nivel"] == "bajo"])

    return {
        "total_zonas": total_zonas,
        "zonas_alto_riesgo": total_alto,
        "zonas_riesgo_medio": total_medio,
        "zonas_bajo_riesgo": total_bajo,
    }