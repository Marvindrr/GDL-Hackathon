from pathlib import Path

from flask import Flask, jsonify, render_template, request

from apps.backend_api.app.applications.services.colonias_loader import (
    cargar_colonias_desde_json,
)
from apps.backend_api.app.applications.services.mapa_gdl import calcular_ruta


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_DIR = PROJECT_ROOT / "apps" / "frontend_web"

ARCHIVO_COLONIAS = "colonias_jalisco.json"
MUNICIPIO_DEFAULT = "Guadalajara"


app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static"),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/colonias")
def api_colonias():
    municipio = request.args.get("municipio") or None

    colonias = cargar_colonias_desde_json(
        ARCHIVO_COLONIAS,
        municipio=municipio,
    )

    return jsonify(colonias)


@app.post("/api/ruta")
def api_ruta():
    payload = request.get_json(silent=True) or {}
    municipio = payload.get("municipio") or MUNICIPIO_DEFAULT

    colonias = cargar_colonias_desde_json(
        ARCHIVO_COLONIAS,
        municipio=municipio,
    )

    try:
        resultado = calcular_ruta(
            origen=payload.get("origen"),
            destino=payload.get("destino"),
            tipo_ruta=payload.get("tipo_ruta", "segura"),
            colonias=colonias,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)
