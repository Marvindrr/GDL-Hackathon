from flask import Blueprint, render_template, jsonify
from .gdl_mapa_service import GdlMapaService


gdl_turismo_bp = Blueprint(
    "gdl_turismo",
    __name__,
    url_prefix="/gdl-turismo"
)


@gdl_turismo_bp.route("/")
def gdl_mapa():
    return render_template("modules/gdl_turismo/gdl_mapa.html")


@gdl_turismo_bp.route("/api/resumen")
def obtener_resumen():
    try:
        data = GdlMapaService.obtener_resumen_modulo()
        return jsonify(data)
    except Exception as error:
        return jsonify({
            "error": True,
            "message": str(error)
        }), 500


@gdl_turismo_bp.route("/api/colonias")
def obtener_colonias():
    try:
        data = GdlMapaService.obtener_colonias()
        return jsonify(data)
    except Exception as error:
        return jsonify({
            "error": True,
            "message": str(error)
        }), 500


@gdl_turismo_bp.route("/api/puntos-turisticos")
def obtener_puntos_turisticos():
    try:
        data = GdlMapaService.obtener_puntos_turisticos()
        return jsonify(data)
    except Exception as error:
        return jsonify({
            "error": True,
            "message": str(error)
        }), 500


@gdl_turismo_bp.route("/api/zonas-turisticas")
def obtener_zonas_turisticas():
    try:
        data = GdlMapaService.obtener_zonas_turisticas()
        return jsonify(data)
    except Exception as error:
        return jsonify({
            "error": True,
            "message": str(error)
        }), 500