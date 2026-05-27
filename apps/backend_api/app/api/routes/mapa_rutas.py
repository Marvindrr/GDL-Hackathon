import json
import unicodedata
from difflib import get_close_matches
from pathlib import Path

from flask import Blueprint, jsonify, request

from app.services.mapa_service import (
    listar_zonas_riesgo,
    listar_puntos_escape as listar_puntos_escape_service,
)
from app.services.route_geo_utils import distancia_haversine


mapa_bp = Blueprint("mapa", __name__, url_prefix="/api/mapa")


def get_project_root():
    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "apps").exists() and (parent / "data").exists():
            return parent

    raise RuntimeError("No se encontró la raíz del proyecto.")


def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(char for char in texto if unicodedata.category(char) != "Mn")
    return texto


def crear_id(texto):
    return normalizar_texto(texto).replace(" ", "_")


def listar_zonas():
    """
    Adapta la respuesta del nuevo mapa_service al formato que ya usaba el frontend.
    """
    zonas_service = listar_zonas_riesgo()
    zonas = []

    for zona in zonas_service:
        nombre = zona.get("zona") or zona.get("nombre")

        zonas.append({
            "id": crear_id(nombre),
            "nombre": nombre,
            "latitud": float(zona["latitud"]),
            "longitud": float(zona["longitud"]),
            "riesgo": int(zona["riesgo"]),
            "nivel_riesgo": zona.get("nivel") or zona.get("nivel_riesgo"),
            "color": zona["color"],
            "radio": zona["radio"],
            "escape_sugerido": zona.get("escape_sugerido"),
        })

    return zonas


def listar_puntos_escape():
    """
    Adapta los puntos de escape al formato que ya usaba el frontend.
    """
    puntos_service = listar_puntos_escape_service()
    puntos = []

    for punto in puntos_service:
        nombre = punto["nombre"]

        puntos.append({
            "id": crear_id(nombre),
            "nombre": nombre,
            "latitud": float(punto["latitud"]),
            "longitud": float(punto["longitud"]),
        })

    return puntos


def buscar_zona_por_nombre(nombre):
    if not nombre:
        return None

    zonas = listar_zonas()
    query = normalizar_texto(nombre)

    for zona in zonas:
        if normalizar_texto(zona["nombre"]) == query:
            return zona

    for zona in zonas:
        if query in normalizar_texto(zona["nombre"]):
            return zona

    nombres = [zona["nombre"] for zona in zonas]

    coincidencias = get_close_matches(
        nombre,
        nombres,
        n=1,
        cutoff=0.45,
    )

    if coincidencias:
        nombre_encontrado = coincidencias[0]

        for zona in zonas:
            if zona["nombre"] == nombre_encontrado:
                return zona

    return None


def obtener_escape_mas_cercano(latitud, longitud):
    puntos_escape = listar_puntos_escape()

    mejor = None
    mejor_distancia = float("inf")

    for punto in puntos_escape:
        distancia = distancia_haversine(
            latitud,
            longitud,
            punto["latitud"],
            punto["longitud"],
        )

        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor = {
                "id": punto["id"],
                "nombre": punto["nombre"],
                "latitud": punto["latitud"],
                "longitud": punto["longitud"],
                "distancia_km": round(distancia, 2),
            }

    return mejor


def calcular_ruta_escape(origen):
    latitud = origen.get("latitud") or origen.get("lat")
    longitud = origen.get("longitud") or origen.get("lng") or origen.get("lon")

    if latitud is None or longitud is None:
        return None

    latitud = float(latitud)
    longitud = float(longitud)

    escape = obtener_escape_mas_cercano(latitud, longitud)

    if not escape:
        return None

    return {
        "destino": escape,
        "ruta": [
            [latitud, longitud],
            [escape["latitud"], escape["longitud"]],
        ],
        "instrucciones": [
            "Mantén la calma y avanza hacia la ruta marcada.",
            f"Dirígete hacia {escape['nombre']}.",
            f"Distancia aproximada: {escape['distancia_km']} km.",
            "Evita zonas marcadas en rojo o con riesgo alto.",
        ],
    }


def normalizar_camaras(camaras):
    resultado = []

    if not isinstance(camaras, list):
        return resultado

    for index, camara in enumerate(camaras):
        latitud = (
            camara.get("latitud")
            or camara.get("lat")
            or camara.get("latitude")
        )

        longitud = (
            camara.get("longitud")
            or camara.get("lng")
            or camara.get("lon")
            or camara.get("longitude")
        )

        if latitud is None or longitud is None:
            continue

        resultado.append({
            "id": camara.get("id") or camara.get("camara_id") or f"cam_{index + 1:03d}",
            "nombre": camara.get("nombre") or camara.get("name") or f"Cámara {index + 1}",
            "zona": camara.get("zona"),
            "activa": camara.get("activa", True),
            "latitud": float(latitud),
            "longitud": float(longitud),
        })

    return resultado


def cargar_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@mapa_bp.route("/zonas", methods=["GET"])
def obtener_zonas():
    return jsonify(listar_zonas())


@mapa_bp.route("/puntos-escape", methods=["GET"])
def obtener_puntos_escape():
    return jsonify(listar_puntos_escape())


@mapa_bp.route("/buscar-zona", methods=["GET"])
def buscar_zona_endpoint():
    nombre = request.args.get("nombre", "")

    zona = buscar_zona_por_nombre(nombre)

    if not zona:
        return jsonify({
            "message": "No se encontró la zona",
            "query": nombre,
        }), 404

    return jsonify(zona)


@mapa_bp.route("/ruta-escape", methods=["POST"])
def calcular_ruta_escape_endpoint():
    data = request.get_json(silent=True) or {}

    zona_nombre = data.get("zona") or data.get("nombre_zona")

    if zona_nombre:
        zona = buscar_zona_por_nombre(zona_nombre)

        if not zona:
            return jsonify({
                "message": "No se encontró la zona para calcular ruta",
            }), 404

        resultado = calcular_ruta_escape({
            "latitud": zona["latitud"],
            "longitud": zona["longitud"],
        })
    else:
        origen = data.get("origen") or data
        resultado = calcular_ruta_escape(origen)

    if not resultado:
        return jsonify({
            "message": "No se pudo calcular la ruta de escape",
        }), 400

    return jsonify(resultado)


@mapa_bp.route("/camaras", methods=["GET"])
def obtener_camaras_mapa():
    root = get_project_root()

    camaras_sistema_path = root / "data" / "camaras" / "camaras.json"
    camaras_geo_path = root / "data" / "geo" / "ubicaciones_camaras.json"

    camaras_sistema = cargar_json(camaras_sistema_path) or []
    camaras_normalizadas = normalizar_camaras(camaras_sistema)

    if camaras_normalizadas:
        return jsonify(camaras_normalizadas)

    camaras_geo = cargar_json(camaras_geo_path) or []

    return jsonify(normalizar_camaras(camaras_geo))