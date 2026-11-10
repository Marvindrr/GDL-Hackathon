
import os

# Configura FFmpeg antes de importar OpenCV para priorizar RTSP sobre TCP.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp"
    "|stimeout;10000000"
    "|max_delay;500000"
)

import cv2
import json
import time
import math
import tempfile

from pathlib import Path
from threading import Lock

from flask import (
    Blueprint,
    jsonify,
    send_file,
    Response,
    abort,
    request
)


# ============================================================
# BLUEPRINT Y CONFIGURACIÓN GENERAL
# ============================================================

camaras_bp = Blueprint(
    "camaras",
    __name__,
    url_prefix="/api/camaras"
)


# ============================================================
# CONFIGURACIÓN DEL MODELO YOLO
# ============================================================

# Instancia compartida del modelo para evitar cargarlo por cada frame.
_modelo_yolo = None

# Indica si ya se intentó cargar el modelo.
_modelo_yolo_intentado = False

# Evita que dos streams ejecuten inferencia simultáneamente.
_modelo_yolo_lock = Lock()


# ============================================================
# CONFIGURACIÓN DE FILTROS DE DETECCIÓN
# ============================================================

FILTROS_DETECCION_DEFAULT = {
    "activo": False,
    "tipo_ropa": "cualquiera",
    "color_ropa": "cualquiera",
    "confianza_color_minima": 0.08
}

TIPOS_ROPA_VALIDOS = {
    "cualquiera",
    "superior",
    "inferior"
}

COLORES_ROPA_VALIDOS = {
    "cualquiera",
    "rojo",
    "naranja",
    "amarillo",
    "verde",
    "azul",
    "morado",
    "rosa",
    "negro",
    "blanco",
    "gris"
}


# ============================================================
# UTILIDADES GENERALES
# ============================================================

def get_project_root():
    """
    Obtiene la raíz del proyecto.

    Primero utiliza PROJECT_ROOT si está configurada.
    Si no, busca las carpetas principales desde este archivo.
    """

    configured_root = os.getenv("PROJECT_ROOT")

    if configured_root:
        root = Path(configured_root).expanduser().resolve()

        if (root / "apps").is_dir() and (root / "data").is_dir():
            return root

    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "apps").is_dir() and (parent / "data").is_dir():
            return parent

    raise RuntimeError("No se encontró la raíz del proyecto.")


def cargar_json(path):
    """
    Lee un archivo JSON.

    Devuelve None cuando el archivo todavía no existe.
    """

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalizar_fuente_video(fuente):
    """
    Convierte fuentes numéricas como '0' o '1' en enteros
    para permitir el acceso a cámaras conectadas localmente.
    """

    if isinstance(fuente, int):
        return fuente

    if isinstance(fuente, str) and fuente.isdigit():
        return int(fuente)

    return fuente


# ============================================================
# CARGA ÚNICA DEL MODELO YOLO
# ============================================================

def obtener_modelo_yolo():
    """
    Carga YOLO una sola vez y comparte la instancia entre streams.

    El modelo se encuentra en:
    data/modelos/yolo26n.pt

    Si no se puede cargar, devuelve None para que el video
    pueda continuar sin recuadros de detección.
    """

    global _modelo_yolo
    global _modelo_yolo_intentado

    with _modelo_yolo_lock:

        # Evita volver a cargar el modelo en cada solicitud.
        if _modelo_yolo_intentado:
            return _modelo_yolo

        _modelo_yolo_intentado = True

        try:
            # Construye la ruta del modelo dentro del proyecto.
            ruta_modelo = (
                get_project_root()
                / "data"
                / "modelos"
                / "yolo26n.pt"
            )

            if not ruta_modelo.is_file():
                print(
                    f"[YOLO] No se encontró el modelo: {ruta_modelo}"
                )
                return None

            # Importación diferida para no impedir que Flask arranque
            # si la dependencia de Ultralytics no está disponible.
            from ultralytics import YOLO

            print(f"[YOLO] Cargando modelo: {ruta_modelo}")

            _modelo_yolo = YOLO(str(ruta_modelo))

            print("[YOLO] Modelo cargado correctamente.")

            return _modelo_yolo

        except Exception as error:
            print(f"[YOLO] Error cargando el modelo: {error}")

            _modelo_yolo = None
            return None


# ============================================================
# CONFIGURACIÓN DE INFERENCIA POR CÁMARA
# ============================================================

def obtener_configuracion_inferencia(camara):
    """
    Recupera las clases, la confianza y el intervalo
    configurados para una cámara.
    """

    # Recupera las clases permitidas en camaras.json.
    clases_configuradas = camara.get("clases", [])

    if isinstance(clases_configuradas, (list, tuple, set)):
        clases_permitidas = {
            str(clase).strip().lower()
            for clase in clases_configuradas
            if str(clase).strip()
        }
    else:
        clases_permitidas = set()

    # Recupera y valida la confianza mínima.
    try:
        confianza = float(camara.get("confianza_minima", 0.35))

        if not math.isfinite(confianza):
            confianza = 0.35

    except (TypeError, ValueError):
        confianza = 0.35

    confianza = max(0.0, min(confianza, 1.0))

    # Recupera y valida el intervalo entre inferencias.
    try:
        intervalo = float(camara.get("intervalo_inferencia", 0.7))

        if not math.isfinite(intervalo) or intervalo <= 0:
            intervalo = 0.7

    except (TypeError, ValueError):
        intervalo = 0.7

    # Evita intervalos excesivamente pequeños.
    intervalo = max(0.1, intervalo)

    return clases_permitidas, confianza, intervalo


# ============================================================
# INFERENCIA YOLO
# ============================================================

def ejecutar_inferencia(frame, clases_permitidas, confianza):
    """
    Ejecuta YOLO sobre un frame y devuelve las detecciones
    que coinciden con las clases configuradas.

    Cada detección contiene:
    - nombre de clase
    - confianza
    - coordenadas de la caja delimitadora
    """

    modelo = obtener_modelo_yolo()

    if modelo is None:
        return []

    detecciones = []

    try:
        # Protege el modelo compartido ante múltiples conexiones.
        with _modelo_yolo_lock:
            resultados = modelo.predict(
                source=frame,
                conf=confianza,
                imgsz=640,
                verbose=False
            )

        if not resultados:
            return []

        resultado = resultados[0]

        if resultado.boxes is None:
            return []

        # Recorre las cajas detectadas por YOLO.
        for caja in resultado.boxes:

            clase_id = int(caja.cls[0].item())

            # Obtiene el nombre de la clase detectada.
            if isinstance(resultado.names, dict):
                nombre_clase = resultado.names.get(
                    clase_id,
                    str(clase_id)
                )
            else:
                nombre_clase = resultado.names[clase_id]

            nombre_clase = str(nombre_clase).lower()

            # Aplica el filtro de clases de camaras.json.
            # Si la lista está vacía, no restringe las clases.
            if (
                clases_permitidas
                and nombre_clase not in clases_permitidas
            ):
                continue

            # Recupera confianza y coordenadas de la detección.
            confianza_deteccion = float(caja.conf[0].item())

            x1, y1, x2, y2 = caja.xyxy[0].tolist()

            detecciones.append({
                "clase": nombre_clase,
                "confianza": confianza_deteccion,
                "caja": [
                    float(x1),
                    float(y1),
                    float(x2),
                    float(y2)
                ]
            })

        return detecciones

    except Exception as error:
        # Un error de inferencia no debe interrumpir el stream.
        print(f"[YOLO] Error durante la inferencia: {error}")

        return []


# ============================================================
# DIBUJADO DE DETECCIONES
# ============================================================

def dibujar_detecciones(frame, detecciones):
    """
    Dibuja las cajas delimitadoras y etiquetas sobre el frame.

    Muestra el nombre de la clase y su confianza porcentual.
    """

    alto, ancho = frame.shape[:2]

    for deteccion in detecciones:

        x1, y1, x2, y2 = deteccion["caja"]

        # Limita las coordenadas al tamaño real del frame.
        x1 = max(0, min(int(x1), ancho - 1))
        y1 = max(0, min(int(y1), alto - 1))
        x2 = max(0, min(int(x2), ancho - 1))
        y2 = max(0, min(int(y2), alto - 1))

        if x2 <= x1 or y2 <= y1:
            continue

        nombre = deteccion["clase"]
        confianza = deteccion["confianza"]

        etiqueta = f"{nombre} {confianza:.0%}"

        # Dibuja el rectángulo alrededor del objeto.
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        # Calcula el espacio necesario para la etiqueta.
        (ancho_texto, alto_texto), linea_base = cv2.getTextSize(
            etiqueta,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            2
        )

        # Coloca la etiqueta arriba de la caja si hay espacio.
        texto_y = y1 - alto_texto - linea_base - 6

        if texto_y < 0:
            texto_y = min(y1 + alto_texto + linea_base + 6, alto - 1)

        fondo_y1 = max(0, texto_y - alto_texto - 5)
        fondo_y2 = min(alto - 1, texto_y + linea_base)

        fondo_x2 = min(ancho - 1, x1 + ancho_texto + 8)

        # Dibuja un fondo para que la etiqueta sea legible.
        cv2.rectangle(
            frame,
            (x1, fondo_y1),
            (fondo_x2, fondo_y2),
            (0, 255, 0),
            -1
        )

        # Escribe la clase y el porcentaje de confianza.
        cv2.putText(
            frame,
            etiqueta,
            (x1 + 4, texto_y - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 0),
            2,
            cv2.LINE_AA
        )

    return frame


# ============================================================
# GESTIÓN DE CÁMARAS
# ============================================================

def cargar_camaras():
    """
    Recupera la configuración de las cámaras desde el JSON.
    """

    root = get_project_root()
    path = root / "data" / "camaras" / "camaras.json"

    return cargar_json(path) or []


def obtener_camara_por_id(camara_id):
    """
    Busca una cámara por su identificador.
    """

    camaras = cargar_camaras()

    for camara in camaras:
        if camara.get("id") == camara_id:
            return camara

    return None


# ============================================================
# GESTIÓN DE FILTROS DE DETECCIÓN
# ============================================================

def obtener_ruta_filtros_deteccion():
    """
    Obtiene la ubicación del archivo de filtros globales.
    """

    root = get_project_root()

    return (
        root
        / "data"
        / "camaras"
        / "filtros_deteccion.json"
    )


def validar_filtros_deteccion(datos):
    """
    Valida los campos y valores recibidos desde el frontend.
    """

    if not isinstance(datos, dict):
        raise ValueError("Se esperaba un objeto JSON.")

    campos_requeridos = {
        "activo",
        "tipo_ropa",
        "color_ropa",
        "confianza_color_minima"
    }

    faltantes = campos_requeridos - datos.keys()

    if faltantes:
        raise ValueError(
            f"Faltan campos obligatorios: {', '.join(sorted(faltantes))}"
        )

    if not isinstance(datos["activo"], bool):
        raise ValueError("'activo' debe ser booleano.")

    tipo_ropa = datos["tipo_ropa"]

    if (
        not isinstance(tipo_ropa, str)
        or tipo_ropa not in TIPOS_ROPA_VALIDOS
    ):
        raise ValueError("El tipo de ropa seleccionado no es válido.")

    color_ropa = datos["color_ropa"]

    if (
        not isinstance(color_ropa, str)
        or color_ropa not in COLORES_ROPA_VALIDOS
    ):
        raise ValueError("El color seleccionado no es válido.")

    confianza = datos["confianza_color_minima"]

    if isinstance(confianza, bool) or not isinstance(confianza, (int, float)):
        raise ValueError("La confianza mínima debe ser numérica.")

    confianza = float(confianza)

    if not math.isfinite(confianza) or not 0 <= confianza <= 1:
        raise ValueError("La confianza debe estar entre 0 y 1.")

    return {
        "activo": datos["activo"],
        "tipo_ropa": tipo_ropa,
        "color_ropa": color_ropa,
        "confianza_color_minima": confianza
    }


def guardar_filtros_deteccion(path, filtros):
    """
    Guarda los filtros mediante un archivo temporal.

    El reemplazo atómico evita dejar un JSON incompleto
    si el proceso se interrumpe durante la escritura.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    ruta_temporal = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix="filtros_deteccion_",
            suffix=".tmp",
            delete=False
        ) as archivo:

            ruta_temporal = Path(archivo.name)

            json.dump(
                filtros,
                archivo,
                ensure_ascii=False,
                indent=2
            )

            archivo.write("\n")

        os.replace(ruta_temporal, path)

    finally:
        if ruta_temporal and ruta_temporal.exists():
            try:
                ruta_temporal.unlink()
            except OSError:
                pass


# ============================================================
# ENDPOINTS DE CÁMARAS
# ============================================================

@camaras_bp.route("")
def listar_camaras():
    """
    Devuelve las cámaras disponibles sin exponer sus URL privadas.
    """

    camaras = cargar_camaras()

    camaras_publicas = []

    for camara in camaras:
        camaras_publicas.append({
            "id": camara.get("id"),
            "nombre": camara.get("nombre", camara.get("id")),
            "activa": camara.get("activa", True),
            "zona": camara.get("zona"),
            "latitud": camara.get("latitud"),
            "longitud": camara.get("longitud")
        })

    return jsonify(camaras_publicas)


@camaras_bp.route("/eventos")
def obtener_eventos():
    """
    Recupera los eventos de cámaras de los últimos 60 segundos.
    """

    root = get_project_root()

    path = (
        root
        / "data"
        / "camaras"
        / "eventos_actuales.json"
    )

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


# ============================================================
# ENDPOINTS DE FILTROS DE DETECCIÓN
# ============================================================

@camaras_bp.route("/filtros-deteccion", methods=["GET"])
def obtener_filtros_deteccion():
    """
    Recupera los filtros globales de detección.
    """

    path = obtener_ruta_filtros_deteccion()

    if not path.exists():
        return jsonify(FILTROS_DETECCION_DEFAULT.copy())

    try:
        filtros = cargar_json(path)
        filtros = validar_filtros_deteccion(filtros)

        return jsonify(filtros)

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"[CAMARAS] Error leyendo filtros: {error}")

        return jsonify({
            "error": "No se pudieron cargar los filtros."
        }), 500


@camaras_bp.route("/filtros-deteccion", methods=["POST"])
def actualizar_filtros_deteccion():
    """
    Recibe los filtros del frontend, los valida y los guarda.
    """

    datos = request.get_json(silent=True)

    try:
        filtros = validar_filtros_deteccion(datos)

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    path = obtener_ruta_filtros_deteccion()

    try:
        guardar_filtros_deteccion(path, filtros)

    except OSError as error:
        print(f"[CAMARAS] Error guardando filtros: {error}")

        return jsonify({
            "error": "No se pudieron guardar los filtros."
        }), 500

    return jsonify({
        "mensaje": "Filtros actualizados correctamente.",
        "filtros": filtros
    }), 200


# ============================================================
# ENDPOINT DE ÚLTIMO FRAME
# ============================================================

@camaras_bp.route("/<camara_id>/ultimo-frame")
def obtener_ultimo_frame(camara_id):
    """
    Devuelve la última imagen almacenada de una cámara.
    """

    root = get_project_root()

    path = (
        root
        / "data"
        / "camaras"
        / "frames"
        / f"{camara_id}.jpg"
    )

    if not path.exists():
        abort(404)

    return send_file(path, mimetype="image/jpeg")


# ============================================================
# CONEXIÓN A FUENTES DE VIDEO
# ============================================================

def abrir_stream(fuente):
    """
    Abre una cámara local o una fuente de video RTSP/HTTP.
    """

    fuente = normalizar_fuente_video(fuente)

    print(f"[STREAM] Fuente normalizada: {fuente}")

    if isinstance(fuente, int):
        backends = [
            cv2.CAP_DSHOW,
            cv2.CAP_MSMF,
            cv2.CAP_ANY
        ]
    else:
        backends = [
            cv2.CAP_FFMPEG,
            cv2.CAP_ANY
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

            print(
                f"[STREAM] Fuente abierta con backend: {backend}"
            )

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 450)

            return cap

        if cap is not None:
            cap.release()

    print(f"[STREAM] No se pudo abrir la fuente: {fuente}")

    return None


# ============================================================
# GENERACIÓN DE FRAMES Y MJPEG
# ============================================================

def crear_frame_error(texto):
    """
    Genera una imagen informativa cuando no hay señal de video.
    """

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
    """
    Codifica un frame como JPEG y construye el paquete MJPEG.
    """

    ok, buffer = cv2.imencode(".jpg", frame)

    if not ok:
        return None

    frame_bytes = buffer.tobytes()

    return (
        b"--frame\r\n"
        b"Content-Type: image/jpeg\r\n\r\n"
        + frame_bytes
        + b"\r\n"
    )


def generar_mjpeg(fuente, camara):
    """
    Transmite video MJPEG con detecciones YOLO superpuestas.

    La inferencia se ejecuta únicamente cuando transcurre
    el intervalo configurado para la cámara.

    Entre inferencias se reutilizan las últimas detecciones
    para evitar ejecutar el modelo en cada frame.
    """

    print(f"[STREAM] Intentando abrir fuente: {fuente}")

    cap = abrir_stream(fuente)

    # Si falla la conexión, mantiene el endpoint disponible
    # mostrando una imagen informativa.
    if cap is None or not cap.isOpened():

        print(f"[STREAM] No se pudo abrir la fuente: {fuente}")

        if cap is not None:
            cap.release()

        frame_error = crear_frame_error(
            "No se pudo abrir la camara"
        )

        while True:
            paquete = frame_a_mjpeg(frame_error)

            if paquete:
                yield paquete

            time.sleep(1)

    print("[STREAM] Fuente abierta correctamente.")

    # Recupera la configuración de inferencia de esta cámara.
    clases_permitidas, confianza, intervalo = (
        obtener_configuracion_inferencia(camara)
    )

    print(
        f"[YOLO] Clases: {sorted(clases_permitidas) if clases_permitidas else 'Todas'}"
    )
    print(f"[YOLO] Confianza mínima: {confianza}")
    print(f"[YOLO] Intervalo de inferencia: {intervalo}s")

    # Estado local de inferencia para esta conexión de video.
    ultima_inferencia = 0.0
    detecciones_actuales = []

    try:
        while True:

            # Obtiene un frame nuevo desde la cámara.
            ret, frame = cap.read()

            if not ret or frame is None:

                print("[STREAM] No se pudo leer frame.")

                frame_error = crear_frame_error(
                    "Sin senal de camara"
                )

                paquete = frame_a_mjpeg(frame_error)

                if paquete:
                    yield paquete

                time.sleep(0.2)
                continue

            # Normaliza la resolución antes de inferir.
            frame = cv2.resize(frame, (800, 450))

            ahora = time.monotonic()

            # Ejecuta YOLO solamente cuando corresponde.
            if ahora - ultima_inferencia >= intervalo:

                ultima_inferencia = ahora

                detecciones_actuales = ejecutar_inferencia(
                    frame,
                    clases_permitidas,
                    confianza
                )

                if detecciones_actuales:
                    print(
                        f"[YOLO] Detecciones: "
                        f"{len(detecciones_actuales)}"
                    )

            # Dibuja las últimas detecciones sobre el frame actual.
            frame = dibujar_detecciones(
                frame,
                detecciones_actuales
            )

            # Codifica y transmite el frame.
            paquete = frame_a_mjpeg(frame)

            if paquete:
                yield paquete

    finally:
        # Libera la conexión al cerrar el stream.
        print("[STREAM] Cerrando captura.")

        cap.release()


# ============================================================
# ENDPOINT DE STREAM EN VIVO
# ============================================================

@camaras_bp.route("/<camara_id>/stream-vivo")
def stream_vivo(camara_id):
    """
    Transmite el video en vivo de una cámara mediante MJPEG
    e incorpora las detecciones YOLO.
    """

    camara = obtener_camara_por_id(camara_id)

    if not camara:
        abort(404)

    # Prioriza la fuente de stream y utiliza detección como alternativa.
    fuente = (
        camara.get("url_stream")
        or camara.get("url_deteccion")
    )

    if not fuente:
        abort(404)

    return Response(
        generar_mjpeg(fuente, camara),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
