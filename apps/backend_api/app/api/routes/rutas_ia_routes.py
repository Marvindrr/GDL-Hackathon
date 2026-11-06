import json

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.infrastructure.db.session import SessionLocal
from app.services.rutas_ia_service import RutasIAService
from app.infrastructure.db.models.route_models import RutaCalculada


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


def ruta_to_response(row):
    geom = json.loads(row.geom_geojson) if row.geom_geojson else None
    origen = json.loads(row.origen_geojson) if row.origen_geojson else None
    destino = json.loads(row.destino_geojson) if row.destino_geojson else None

    return {
        "id_ruta": row.id_ruta,
        "tipo_ruta": row.tipo_ruta,
        "score_riesgo": float(row.score_riesgo) if row.score_riesgo is not None else None,
        "score_confianza": float(row.score_confianza) if row.score_confianza is not None else None,
        "distancia_m": float(row.distancia_m) if row.distancia_m is not None else None,
        "duracion_estimada_seg": float(row.duracion_estimada_seg) if row.duracion_estimada_seg is not None else None,
        "algoritmo": row.algoritmo,
        "parametros": row.parametros,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "origen": origen,
        "destino": destino,
        "geom": geom,
        "geojson": {
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "id_ruta": row.id_ruta,
                "tipo_ruta": row.tipo_ruta,
                "score_riesgo": float(row.score_riesgo) if row.score_riesgo is not None else None,
                "distancia_m": float(row.distancia_m) if row.distancia_m is not None else None,
                "algoritmo": row.algoritmo,
            },
        } if geom else None,
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


@rutas_ia_bp.route("/rutas-recientes", methods=["GET"])
def obtener_rutas_recientes():
    db = SessionLocal()

    try:
        limit = int(request.args.get("limit", 10))
        tipo_ruta = request.args.get("tipo_ruta")

        query = (
            db.query(
                RutaCalculada.id_ruta,
                RutaCalculada.tipo_ruta,
                RutaCalculada.score_riesgo,
                RutaCalculada.score_confianza,
                RutaCalculada.distancia_m,
                RutaCalculada.duracion_estimada_seg,
                RutaCalculada.algoritmo,
                RutaCalculada.parametros,
                RutaCalculada.created_at,
                func.ST_AsGeoJSON(RutaCalculada.geom).label("geom_geojson"),
                func.ST_AsGeoJSON(RutaCalculada.origen).label("origen_geojson"),
                func.ST_AsGeoJSON(RutaCalculada.destino).label("destino_geojson"),
            )
            .order_by(RutaCalculada.created_at.desc())
        )

        if tipo_ruta:
            query = query.filter(RutaCalculada.tipo_ruta == tipo_ruta)

        rows = query.limit(limit).all()

        return jsonify({
            "total": len(rows),
            "items": [ruta_to_response(row) for row in rows],
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error consultando rutas recientes.",
            "detalle": str(e),
        }), 500

    finally:
        db.close()


@rutas_ia_bp.route("/rutas/<int:id_ruta>", methods=["GET"])
def obtener_ruta_por_id(id_ruta: int):
    db = SessionLocal()

    try:
        row = (
            db.query(
                RutaCalculada.id_ruta,
                RutaCalculada.tipo_ruta,
                RutaCalculada.score_riesgo,
                RutaCalculada.score_confianza,
                RutaCalculada.distancia_m,
                RutaCalculada.duracion_estimada_seg,
                RutaCalculada.algoritmo,
                RutaCalculada.parametros,
                RutaCalculada.created_at,
                func.ST_AsGeoJSON(RutaCalculada.geom).label("geom_geojson"),
                func.ST_AsGeoJSON(RutaCalculada.origen).label("origen_geojson"),
                func.ST_AsGeoJSON(RutaCalculada.destino).label("destino_geojson"),
            )
            .filter(RutaCalculada.id_ruta == id_ruta)
            .first()
        )

        if not row:
            return jsonify({
                "error": "Ruta no encontrada.",
            }), 404

        return jsonify(ruta_to_response(row)), 200

    except Exception as e:
        return jsonify({
            "error": "Error consultando ruta.",
            "detalle": str(e),
        }), 500

    finally:
        db.close()


@rutas_ia_bp.route("/ping", methods=["GET"])
def ping_rutas_ia():
    return jsonify({
        "message": "rutas_ia activo"
    }), 200