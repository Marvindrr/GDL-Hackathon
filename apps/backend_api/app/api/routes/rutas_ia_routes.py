from flask import Blueprint, jsonify, request

from app.infrastructure.db.session import SessionLocal
from app.application.services.rutas_ia_service import RutasIAService


rutas_ia_bp = Blueprint("rutas_ia", __name__, url_prefix="/api/ia-rutas")


def validar_punto(data: dict, nombre: str):
    punto = data.get(nombre)

    if not punto:
        raise ValueError(f"Falta el campo '{nombre}'.")

    if "lat" not in punto or "lon" not in punto:
        raise ValueError(f"El campo '{nombre}' debe tener lat y lon.")

    return {
        "lat": float(punto["lat"]),
        "lon": float(punto["lon"]),
    }


@rutas_ia_bp.route("/ruta-segura", methods=["POST"])
def calcular_ruta_segura():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}

        origen = validar_punto(data, "origen")
        destino = validar_punto(data, "destino")
        guardar = bool(data.get("guardar", True))

        service = RutasIAService(db)

        resultado = service.calcular_ruta_segura_turista(
            origen=origen,
            destino=destino,
            guardar=guardar,
        )

        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({
            "error": str(e),
        }), 400

    except Exception as e:
        db.rollback()
        return jsonify({
            "error": "Error calculando ruta segura.",
            "detalle": str(e),
        }), 500

    finally:
        db.close()


@rutas_ia_bp.route("/ruta-probable-desplazamiento", methods=["POST"])
def calcular_ruta_probable_desplazamiento():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}

        origen = validar_punto(data, "origen")
        radio_m = int(data.get("radio_m", 500))
        guardar = bool(data.get("guardar", True))

        service = RutasIAService(db)

        resultado = service.calcular_rutas_probables_desplazamiento(
            origen=origen,
            radio_m=radio_m,
            guardar=guardar,
        )

        return jsonify(resultado), 200

    except ValueError as e:
        return jsonify({
            "error": str(e),
        }), 400

    except Exception as e:
        db.rollback()
        return jsonify({
            "error": "Error calculando ruta probable de desplazamiento.",
            "detalle": str(e),
        }), 500

    finally:
        db.close()