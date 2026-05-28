import json
from datetime import datetime

from flask import Blueprint, jsonify, request
from geoalchemy2 import WKTElement
from sqlalchemy import func

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.camera_models import Camara
from app.infrastructure.db.models.ai_models import (
    ModeloIA,
    DeteccionCamara,
    TrackObjeto,
    TrackObservacion,
)
from app.infrastructure.db.models.event_models import EventoSeguridad
from app.services.rutas_ia_service import RutasIAService


detecciones_bp = Blueprint("detecciones", __name__, url_prefix="/api/detecciones")


def point_wkt(lon, lat):
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def get_or_create_modelo(db) -> ModeloIA:
    modelo = (
        db.query(ModeloIA)
        .filter(ModeloIA.nombre == "YOLO26_OBJECT_DETECTION")
        .first()
    )

    if modelo:
        return modelo

    modelo = ModeloIA(
        nombre="YOLO26_OBJECT_DETECTION",
        version="0.1.0",
        tipo_modelo="deteccion_objetos",
        proveedor="SeguryTech",
        descripcion="Modelo base para detectar personas, vehículos, motos y objetos relevantes.",
        activo=True,
    )

    db.add(modelo)
    db.flush()

    return modelo


def get_or_create_track(db, tracking_id: str, tipo_objeto: str, lat: float, lon: float):
    track = (
        db.query(TrackObjeto)
        .filter(TrackObjeto.tracking_id == tracking_id)
        .first()
    )

    if track:
        track.estado = "activo"
        track.ultima_ubicacion = point_wkt(lon, lat)
        return track

    track = TrackObjeto(
        tracking_id=tracking_id,
        tipo_objeto=tipo_objeto,
        estado="activo",
        confianza_global=0.75,
        ultima_ubicacion=point_wkt(lon, lat),
    )

    db.add(track)
    db.flush()

    return track


@detecciones_bp.route("/persona", methods=["POST"])
def registrar_deteccion_persona():
    db = SessionLocal()

    try:
        data = request.get_json(silent=True) or {}

        codigo_camara = data.get("codigo_camara", "WEBCAM_LAPTOP_LAB")

        camara = (
            db.query(Camara)
            .filter(Camara.codigo_externo == codigo_camara)
            .first()
        )

        if not camara:
            return jsonify({
                "error": f"No existe la cámara con código {codigo_camara}."
            }), 404

        lat = float(data.get("lat", camara.lat))
        lon = float(data.get("lon", camara.lon))

        clase_detectada = data.get("clase_detectada", "person")
        confianza = float(data.get("confianza", 0.75))
        color_dominante = data.get("color_dominante")
        bbox = data.get("bbox")
        keypoints = data.get("keypoints")

        tracking_id = data.get("tracking_id") or f"{codigo_camara}_person_demo"

        modelo = get_or_create_modelo(db)

        track = get_or_create_track(
            db=db,
            tracking_id=tracking_id,
            tipo_objeto=clase_detectada,
            lat=lat,
            lon=lon,
        )

        evento = EventoSeguridad(
            id_zona=camara.id_zona,
            id_track=track.id_track,
            tipo_evento="deteccion_persona",
            descripcion=f"Persona detectada desde cámara {camara.nombre}.",
            estado="activo",
            severidad=int(data.get("severidad", 1)),
            lat=lat,
            lon=lon,
            ubicacion=point_wkt(lon, lat),
        )

        db.add(evento)
        db.flush()

        deteccion = DeteccionCamara(
            id_camara=camara.id_camara,
            id_modelo=modelo.id_modelo,
            id_evento=evento.id_evento,
            clase_detectada=clase_detectada,
            confianza=confianza,
            tracking_id_externo=tracking_id,
            bbox=bbox,
            keypoints=keypoints,
            extra_metadata={
                "color_dominante": color_dominante,
                "source": data.get("source", "webcam_laptop"),
                "payload_original": data,
            },
            fecha_deteccion=datetime.utcnow(),
            lat=lat,
            lon=lon,
            ubicacion=point_wkt(lon, lat),
        )

        db.add(deteccion)
        db.flush()

        observacion = TrackObservacion(
            id_track=track.id_track,
            id_deteccion=deteccion.id_deteccion,
            id_camara=camara.id_camara,
            lat=lat,
            lon=lon,
            ubicacion=point_wkt(lon, lat),
            extra_metadata={
                "color_dominante": color_dominante,
                "bbox": bbox,
            },
        )

        db.add(observacion)
        db.commit()

        calcular_ruta = bool(data.get("calcular_ruta", True))

        ruta_resultado = None

        if calcular_ruta:
            service = RutasIAService(db)

            ruta_resultado = service.calcular_rutas_probables_desplazamiento(
                origen={
                    "lat": lat,
                    "lon": lon,
                },
                radio_m=int(data.get("radio_m", 500)),
                guardar=True,
            )

        return jsonify({
            "message": "Detección registrada correctamente.",
            "id_camara": camara.id_camara,
            "id_evento": evento.id_evento,
            "id_deteccion": deteccion.id_deteccion,
            "id_track": track.id_track,
            "tracking_id": tracking_id,
            "ubicacion": {
                "lat": lat,
                "lon": lon,
            },
            "color_dominante": color_dominante,
            "ruta_probable": ruta_resultado,
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({
            "error": "Error registrando detección.",
            "detalle": str(e),
        }), 500

    finally:
        db.close()


@detecciones_bp.route("/recientes", methods=["GET"])
def obtener_detecciones_recientes():
    db = SessionLocal()

    try:
        limit = int(request.args.get("limit", 20))

        rows = (
            db.query(
                DeteccionCamara.id_deteccion,
                DeteccionCamara.clase_detectada,
                DeteccionCamara.confianza,
                DeteccionCamara.tracking_id_externo,
                DeteccionCamara.extra_metadata,
                DeteccionCamara.fecha_deteccion,
                Camara.nombre.label("camara_nombre"),
                Camara.codigo_externo.label("codigo_camara"),
                func.ST_AsGeoJSON(DeteccionCamara.ubicacion).label("ubicacion_geojson"),
            )
            .join(Camara, Camara.id_camara == DeteccionCamara.id_camara)
            .order_by(DeteccionCamara.fecha_deteccion.desc())
            .limit(limit)
            .all()
        )

        items = []

        for row in rows:
            ubicacion = json.loads(row.ubicacion_geojson) if row.ubicacion_geojson else None

            items.append({
                "id_deteccion": row.id_deteccion,
                "codigo_camara": row.codigo_camara,
                "camara_nombre": row.camara_nombre,
                "clase_detectada": row.clase_detectada,
                "confianza": float(row.confianza) if row.confianza is not None else None,
                "tracking_id": row.tracking_id_externo,
                "metadata": row.extra_metadata,
                "fecha_deteccion": row.fecha_deteccion.isoformat() if row.fecha_deteccion else None,
                "ubicacion": ubicacion,
            })

        return jsonify({
            "total": len(items),
            "items": items,
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error consultando detecciones recientes.",
            "detalle": str(e),
        }), 500

    finally:
        db.close()