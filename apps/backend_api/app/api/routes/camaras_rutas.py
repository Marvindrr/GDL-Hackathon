import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp"
    "|stimeout;10000000"
    "|max_delay;500000"
)

import cv2
import json
import time
from pathlib import Path

from flask import Blueprint, jsonify, send_file, Response, abort, request


camaras_bp = Blueprint("camaras", __name__, url_prefix="/api/camaras")


def get_project_root():
    project_root = os.getenv("PROJECT_ROOT")

    if project_root:
        path = Path(project_root)

        if path.exists():
            return path

    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "apps").exists() and (parent / "data").exists():
            return parent

    docker_root = Path("/workspace")

    if docker_root.exists():
        return docker_root

    raise RuntimeError("No se encontró la raíz del proyecto.")


def cargar_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    
FILTROS_DETECCION_DEFAULT = {
    "activo": False,
    "tipo_ropa": "cualquiera",
    "color_ropa": "cualquiera",
    "confianza_color_minima": 0.08,
}


def guardar_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def obtener_ruta_filtros_deteccion():
    root = get_project_root()
    return root / "data" / "camaras" / "filtros_deteccion.json"


def normalizar_filtros_deteccion(data):
    if not isinstance(data, dict):
        return FILTROS_DETECCION_DEFAULT.copy()

    filtros = FILTROS_DETECCION_DEFAULT.copy()

    filtros["activo"] = bool(data.get("activo", filtros["activo"]))
    filtros["tipo_ropa"] = data.get("tipo_ropa") or filtros["tipo_ropa"]
    filtros["color_ropa"] = data.get("color_ropa") or filtros["color_ropa"]

    try:
        filtros["confianza_color_minima"] = float(
            data.get(
                "confianza_color_minima",
                filtros["confianza_color_minima"]
            )
        )
    except (TypeError, ValueError):
        filtros["confianza_color_minima"] = FILTROS_DETECCION_DEFAULT[
            "confianza_color_minima"
        ]

    return filtros


def normalizar_fuente_video(fuente):
    """
    Convierte "0", "1", "2" a número entero para webcams locales.
    Si es RTSP o HTTP, lo deja como string.
    """

    if isinstance(fuente, int):
        return fuente

    if isinstance(fuente, str) and fuente.isdigit():
        return int(fuente)

    return fuente


def cargar_camaras():
    root = get_project_root()
    path = root / "data" / "camaras" / "camaras.json"

    return cargar_json(path) or []


def obtener_camara_por_id(camara_id):
    camaras = cargar_camaras()

    for camara in camaras:
        if camara["id"] == camara_id:
            return camara

    return None


@camaras_bp.route("")
def listar_camaras():
    camaras = cargar_camaras()

    camaras_publicas = []

    for camara in camaras:
        camaras_publicas.append({
            "id": camara["id"],
            "nombre": camara.get("nombre", camara["id"]),
            "activa": camara.get("activa", True),
            "zona": camara.get("zona"),
            "latitud": camara.get("latitud"),
            "longitud": camara.get("longitud")
        })

    return jsonify(camaras_publicas)

@camaras_bp.route("/filtros-deteccion", methods=["GET"])
def obtener_filtros_deteccion():
    path = obtener_ruta_filtros_deteccion()
    filtros = cargar_json(path) or FILTROS_DETECCION_DEFAULT.copy()

    return jsonify(normalizar_filtros_deteccion(filtros))


@camaras_bp.route("/filtros-deteccion", methods=["POST"])
def actualizar_filtros_deteccion():
    data = request.get_json(silent=True) or {}
    filtros = normalizar_filtros_deteccion(data)

    path = obtener_ruta_filtros_deteccion()
    guardar_json(path, filtros)

    return jsonify({
        "ok": True,
        "filtros": filtros,
    })


@camaras_bp.route("/eventos")
def obtener_eventos():
    root = get_project_root()
    path = root / "data" / "camaras" / "eventos_actuales.json"

    eventos = cargar_json(path) or {}

    ahora = time.time()
    eventos_recientes = []

    for evento in eventos.values():
        if ahora - evento.get("timestamp", 0) <= 60:
            eventos_recientes.append(evento)

    eventos_recientes.sort(
        key=lambda item: item.get("timestamp", 0),
        reverse=True
    )

    return jsonify(eventos_recientes)


@camaras_bp.route("/<camara_id>/ultimo-frame")
def obtener_ultimo_frame(camara_id):
    root = get_project_root()
    path = root / "data" / "camaras" / "frames" / f"{camara_id}.jpg"

    if not path.exists():
        abort(404)

    return send_file(path, mimetype="image/jpeg")


def abrir_stream(fuente):
    fuente = normalizar_fuente_video(fuente)

    print(f"[STREAM] Fuente normalizada: {fuente}")

    if isinstance(fuente, int):
        backends = [
            cv2.CAP_DSHOW,
            cv2.CAP_MSMF,
            cv2.CAP_ANY,
        ]
    else:
        backends = [
            cv2.CAP_FFMPEG,
            cv2.CAP_ANY,
        ]

    cap = None

    for backend in backends:
        print(f"[STREAM] Probando backend: {backend}")

        cap = cv2.VideoCapture(fuente, backend)

        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)
        except Exception:
            pass

        if cap is not None and cap.isOpened():
            print(f"[STREAM] Fuente abierta con backend: {backend}")

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)

            return cap

        if cap is not None:
            cap.release()

    print(f"[STREAM] Ningún backend pudo abrir la fuente: {fuente}")

    return None


def crear_frame_error(texto):
    import numpy as np

    frame = np.zeros((450, 800, 3), dtype=np.uint8)

    cv2.putText(
        frame,
        texto,
        (40, 225),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )

    return frame


def frame_a_mjpeg(frame):
    ok, buffer = cv2.imencode(".jpg", frame)

    if not ok:
        return None

    frame_bytes = buffer.tobytes()

    return (
        b"--frame\r\n"
        b"Content-Type: image/jpeg\r\n\r\n" +
        frame_bytes +
        b"\r\n"
    )


def generar_mjpeg(fuente):
    print(f"[STREAM] Intentando abrir fuente: {fuente}")

    cap = abrir_stream(fuente)

    if cap is None or not cap.isOpened():
        print(f"[STREAM] No se pudo abrir la fuente: {fuente}")

        frame_error = crear_frame_error("No se pudo abrir la camara")

        while True:
            paquete = frame_a_mjpeg(frame_error)

            if paquete:
                yield paquete

            time.sleep(1)

    print(f"[STREAM] Fuente abierta correctamente: {fuente}")

    try:
        while True:
            ret, frame = cap.read()

            if not ret or frame is None:
                print("[STREAM] No se pudo leer frame")

                frame_error = crear_frame_error("Sin senal de camara")
                paquete = frame_a_mjpeg(frame_error)

                if paquete:
                    yield paquete

                time.sleep(1)
                continue

            frame = cv2.resize(frame, (800, 450))

            paquete = frame_a_mjpeg(frame)

            if paquete:
                yield paquete

    finally:
        print("[STREAM] Cerrando captura")
        cap.release()


@camaras_bp.route("/<camara_id>/stream-vivo")
def stream_vivo(camara_id):
    camara = obtener_camara_por_id(camara_id)

    if not camara:
        abort(404)

    fuente = camara.get("url_stream") or camara.get("url_deteccion")

    if not fuente:
        abort(404)

    return Response(
        generar_mjpeg(fuente),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )