# Este módulo contiene la lógica para manejar las zonas de riesgo, 
# puntos de escape y resúmenes relacionados al mapa.
# No debe contener lógica de entrenamiento, generación de HTML o apertura de navegador.

from sqlalchemy import func

from app.data.mapa_demo_data import PUNTOS_ZONAS, DATOS_RIESGO, PUNTOS_ESCAPE
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import Zona, Municipio
from app.infrastructure.db.models.security_point_models import PuntoSeguridad
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

def listar_zonas_riesgo_desde_bd():
    db = None

    try:
        db = SessionLocal()

        rows = (
            db.query(
                Zona.id_zona,
                Zona.nombre,
                Zona.tipo,
                Zona.riesgo_base,
                Municipio.nombre.label("municipio"),
                func.ST_Y(Zona.centro).label("latitud"),
                func.ST_X(Zona.centro).label("longitud"),
            )
            .outerjoin(Municipio, Municipio.id_municipio == Zona.id_municipio)
            .filter(Zona.centro.isnot(None))
            .order_by(Zona.nombre.asc())
            .all()
        )

        zonas = []

        for row in rows:
            riesgo = int(float(row.riesgo_base or 0))
            estilo = obtener_color_y_radio_por_riesgo(riesgo)

            zonas.append({
                "id_zona": row.id_zona,
                "zona": row.nombre,
                "nombre": row.nombre,
                "municipio": row.municipio,
                "tipo": row.tipo,
                "latitud": float(row.latitud),
                "longitud": float(row.longitud),
                "riesgo": riesgo,
                "nivel": estilo["nivel"],
                "nivel_riesgo": estilo["nivel"],
                "color": estilo["color"],
                "radio": estilo["radio"],
                "escape_sugerido": None,
                "fuente": "bd",
            })

        return zonas

    except Exception as error:
        print(f"[mapa_service] Error cargando zonas desde BD: {error}")
        return []

    finally:
        if db:
            db.close()

def listar_zonas_riesgo_demo():
    zonas = []

    for nombre_zona, coordenadas in PUNTOS_ZONAS.items():
        riesgo = DATOS_RIESGO.get(nombre_zona, 0)
        estilo = obtener_color_y_radio_por_riesgo(riesgo)

        zona = {
            "zona": nombre_zona,
            "nombre": nombre_zona,
            "latitud": coordenadas[0],
            "longitud": coordenadas[1],
            "riesgo": riesgo,
            "nivel": estilo["nivel"],
            "nivel_riesgo": estilo["nivel"],
            "color": estilo["color"],
            "radio": estilo["radio"],
            "escape_sugerido": None,
            "fuente": "demo",
        }

        if riesgo >= 60:
            zona["escape_sugerido"] = obtener_punto_escape_mas_cercano(
                coordenadas_origen=coordenadas,
                puntos_escape=PUNTOS_ESCAPE,
            )

        zonas.append(zona)

    return zonas


def listar_zonas_riesgo():
    zonas_bd = listar_zonas_riesgo_desde_bd()

    if zonas_bd:
        return zonas_bd

    return listar_zonas_riesgo_demo()


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