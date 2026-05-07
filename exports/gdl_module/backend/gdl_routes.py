from pathlib import Path

from flask import Blueprint, jsonify, render_template, request

from .gdl_colonias_loader import cargar_colonias_gdl
from .gdl_mapa_service import calcular_ruta_gdl


GDL_MODULE_DIR = Path(__file__).resolve().parents[1]
MUNICIPIO_DEFAULT = "Guadalajara"

gdl_bp = Blueprint(
    "gdl",
    __name__,
    template_folder=str(GDL_MODULE_DIR / "templates"),
    static_folder=str(GDL_MODULE_DIR / "static"),
    static_url_path="/gdl_static",
)


@gdl_bp.get("/gdl")
def gdl_mapa():
    return render_template("gdl_mapa.html")


@gdl_bp.get("/api/gdl/colonias")
def api_gdl_colonias():
    municipio = request.args.get("municipio") or None
    return jsonify(cargar_colonias_gdl(municipio=municipio))


@gdl_bp.post("/api/gdl/ruta")
def api_gdl_ruta():
    payload = request.get_json(silent=True) or {}
    municipio = payload.get("municipio") or MUNICIPIO_DEFAULT
    colonias = cargar_colonias_gdl(municipio=municipio)

    try:
        resultado = calcular_ruta_gdl(
            origen=payload.get("origen"),
            destino=payload.get("destino"),
            tipo_ruta=payload.get("tipo_ruta", "segura"),
            colonias=colonias,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(resultado)
