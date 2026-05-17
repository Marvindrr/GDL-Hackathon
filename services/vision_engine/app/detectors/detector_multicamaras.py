import os
import cv2
import json
import time
import numpy as np
from pathlib import Path
from threading import Thread, Lock

from ultralytics import YOLO


os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

ROOT_DIR = Path(__file__).resolve().parents[4]

CAMARAS_PATH = ROOT_DIR / "data" / "camaras" / "camaras.json"
EVENTOS_PATH = ROOT_DIR / "data" / "camaras" / "eventos_actuales.json"
FRAMES_DIR = ROOT_DIR / "data" / "camaras" / "frames"

FRAMES_DIR.mkdir(parents=True, exist_ok=True)

MODELO_YOLO = "yolo11s.pt"
modelo = YOLO(MODELO_YOLO)

lock_eventos = Lock()
eventos_actuales = {}

CLASES_INTERES_DEFAULT = {
    "person",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "bicycle",
}


COLORES_HSV = {
    "rojo": [
        ((0, 70, 50), (10, 255, 255)),
        ((170, 70, 50), (180, 255, 255)),
    ],
    "naranja": [
        ((11, 80, 80), (24, 255, 255)),
    ],
    "amarillo": [
        ((25, 70, 80), (35, 255, 255)),
    ],
    "verde": [
        ((36, 60, 50), (85, 255, 255)),
    ],
    "azul": [
        ((86, 60, 50), (130, 255, 255)),
    ],
    "morado": [
        ((131, 50, 50), (160, 255, 255)),
    ],
    "rosa": [
        ((145, 40, 80), (169, 255, 255)),
    ],
}


def cargar_camaras():
    if not CAMARAS_PATH.exists():
        raise FileNotFoundError(f"No existe el archivo de cámaras: {CAMARAS_PATH}")

    with open(CAMARAS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def guardar_eventos():
    with lock_eventos:
        with open(EVENTOS_PATH, "w", encoding="utf-8") as file:
            json.dump(eventos_actuales, file, ensure_ascii=False, indent=4)


def obtener_ids_clases(clases, detectar_ropa=True):
    clases_set = set(clases or CLASES_INTERES_DEFAULT)

    # Para analizar ropa/color, siempre necesitamos detectar personas.
    if detectar_ropa:
        clases_set.add("person")

    return [
        class_id
        for class_id, nombre in modelo.names.items()
        if nombre in clases_set
    ]


def normalizar_fuente_video(fuente):
    if isinstance(fuente, int):
        return fuente

    if isinstance(fuente, str) and fuente.isdigit():
        return int(fuente)

    return fuente


def abrir_stream(fuente):
    fuente = normalizar_fuente_video(fuente)

    if isinstance(fuente, int):
        cap = cv2.VideoCapture(fuente, cv2.CAP_MSMF)

        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(fuente, cv2.CAP_DSHOW)

        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(fuente, cv2.CAP_ANY)

    else:
        cap = cv2.VideoCapture(fuente, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(fuente, cv2.CAP_ANY)

    if cap.isOpened():
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    return cap


def recortar_seguro(frame, x1, y1, x2, y2):
    alto, ancho = frame.shape[:2]

    x1 = max(0, min(x1, ancho - 1))
    x2 = max(0, min(x2, ancho - 1))
    y1 = max(0, min(y1, alto - 1))
    y2 = max(0, min(y2, alto - 1))

    if x2 <= x1 or y2 <= y1:
        return None

    return frame[y1:y2, x1:x2]


def clasificar_color_basico(roi):
    if roi is None or roi.size == 0:
        return {
            "color": "indefinido",
            "confianza_color": 0.0
        }

    roi = cv2.resize(roi, (80, 80))
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv)

    total_pixeles = hsv.shape[0] * hsv.shape[1]

    # Primero detectamos blanco, negro y gris.
    mascara_negro = v < 50
    mascara_blanco = (s < 35) & (v > 190)
    mascara_gris = (s < 35) & (v >= 50) & (v <= 190)

    conteos_basicos = {
        "negro": int(np.count_nonzero(mascara_negro)),
        "blanco": int(np.count_nonzero(mascara_blanco)),
        "gris": int(np.count_nonzero(mascara_gris)),
    }

    mejor_color = "indefinido"
    mejor_conteo = 0

    for color, conteo in conteos_basicos.items():
        if conteo > mejor_conteo:
            mejor_color = color
            mejor_conteo = conteo

    # Ahora colores cromáticos.
    for color, rangos in COLORES_HSV.items():
        mascara_total = np.zeros(hsv.shape[:2], dtype=np.uint8)

        for lower, upper in rangos:
            lower_np = np.array(lower, dtype=np.uint8)
            upper_np = np.array(upper, dtype=np.uint8)

            mascara = cv2.inRange(hsv, lower_np, upper_np)
            mascara_total = cv2.bitwise_or(mascara_total, mascara)

        conteo = int(np.count_nonzero(mascara_total))

        if conteo > mejor_conteo:
            mejor_color = color
            mejor_conteo = conteo

    confianza = round(mejor_conteo / total_pixeles, 3)

    if confianza < 0.08:
        mejor_color = "indefinido"

    return {
        "color": mejor_color,
        "confianza_color": confianza
    }


def analizar_ropa_persona(frame, x1, y1, x2, y2):
    """
    Estima color de ropa superior e inferior usando la caja de la persona.
    No es segmentación real de ropa, es aproximación por regiones del cuerpo.
    """

    ancho_persona = x2 - x1
    alto_persona = y2 - y1

    if ancho_persona <= 0 or alto_persona <= 0:
        return None

    # Evitamos cabeza y pies. Tomamos torso y piernas aproximadas.
    y_superior_1 = int(y1 + alto_persona * 0.22)
    y_superior_2 = int(y1 + alto_persona * 0.55)

    y_inferior_1 = int(y1 + alto_persona * 0.55)
    y_inferior_2 = int(y1 + alto_persona * 0.90)

    margen_x = int(ancho_persona * 0.12)

    xs1 = x1 + margen_x
    xs2 = x2 - margen_x

    roi_superior = recortar_seguro(frame, xs1, y_superior_1, xs2, y_superior_2)
    roi_inferior = recortar_seguro(frame, xs1, y_inferior_1, xs2, y_inferior_2)

    color_superior = clasificar_color_basico(roi_superior)
    color_inferior = clasificar_color_basico(roi_inferior)

    return {
        "superior": {
            "tipo": "ropa_superior",
            "color": color_superior["color"],
            "confianza_color": color_superior["confianza_color"]
        },
        "inferior": {
            "tipo": "ropa_inferior",
            "color": color_inferior["color"],
            "confianza_color": color_inferior["confianza_color"]
        }
    }


def dibujar_detecciones(frame, detecciones_box):
    for item in detecciones_box:
        x1, y1, x2, y2 = item["box"]
        clase = item["clase"]
        confianza = item["confianza"]
        ropa = item.get("ropa")

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        texto = f"{clase} {confianza:.2f}"

        if ropa:
            color_sup = ropa["superior"]["color"]
            color_inf = ropa["inferior"]["color"]
            texto = f"{texto} | sup:{color_sup} inf:{color_inf}"

        cv2.putText(
            frame,
            texto,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    return frame


def detectar_en_camara(camara):
    camara_id = camara["id"]
    nombre = camara.get("nombre", camara_id)
    fuente_deteccion = camara["url_deteccion"]

    detectar_ropa = camara.get("detectar_ropa", True)
    detectar_color_ropa = camara.get("detectar_color_ropa", True)

    clases = camara.get("clases", list(CLASES_INTERES_DEFAULT))
    classes_ids = obtener_ids_clases(clases, detectar_ropa=detectar_ropa)

    print(f"[{camara_id}] Iniciando detección: {nombre}")
    print(f"[{camara_id}] Fuente detección: {fuente_deteccion}")

    cap = abrir_stream(fuente_deteccion)

    if cap is None or not cap.isOpened():
        print(f"[{camara_id}] No se pudo abrir la fuente: {fuente_deteccion}")
        return

    ultimo_evento = 0
    cooldown_evento = camara.get("cooldown_evento", 10)

    ultimo_analisis = 0
    intervalo_inferencia = camara.get("intervalo_inferencia", 0.7)

    while True:
        ret, frame = cap.read()

        if not ret or frame is None:
            print(f"[{camara_id}] Sin señal. Reintentando...")
            cap.release()
            time.sleep(2)
            cap = abrir_stream(fuente_deteccion)
            continue

        ahora = time.time()

        if ahora - ultimo_analisis < intervalo_inferencia:
            continue

        ultimo_analisis = ahora

        frame_small = cv2.resize(frame, (640, 360))

        resultados = modelo.predict(
            source=frame_small,
            conf=camara.get("confianza_minima", 0.35),
            imgsz=640,
            verbose=False,
            classes=classes_ids
        )

        detecciones = []
        detecciones_box = []

        if resultados and resultados[0].boxes is not None:
            for box in resultados[0].boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                nombre_clase = modelo.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                ropa = None

                if (
                    detectar_ropa
                    and detectar_color_ropa
                    and nombre_clase == "person"
                ):
                    ropa = analizar_ropa_persona(frame_small, x1, y1, x2, y2)

                deteccion = {
                    "clase": nombre_clase,
                    "confianza": round(conf, 3)
                }

                if ropa:
                    deteccion["ropa"] = ropa

                detecciones.append(deteccion)

                detecciones_box.append({
                    "clase": nombre_clase,
                    "confianza": conf,
                    "box": [x1, y1, x2, y2],
                    "ropa": ropa
                })

        if detecciones and ahora - ultimo_evento >= cooldown_evento:
            ultimo_evento = ahora

            frame_detectado = dibujar_detecciones(
                frame_small.copy(),
                detecciones_box
            )

            frame_path = FRAMES_DIR / f"{camara_id}.jpg"
            cv2.imwrite(str(frame_path), frame_detectado)

            evento = {
                "camara_id": camara_id,
                "nombre": nombre,
                "zona": camara.get("zona"),
                "timestamp": ahora,
                "detecciones": detecciones,
                "frame_url": f"/api/camaras/{camara_id}/ultimo-frame",
                "stream_url": f"/api/camaras/{camara_id}/stream-vivo",
                "latitud": camara.get("latitud"),
                "longitud": camara.get("longitud")
            }

            print(f"[{camara_id}] Evento generado:")
            print(json.dumps(evento, ensure_ascii=False, indent=4))

            with lock_eventos:
                eventos_actuales[camara_id] = evento

            guardar_eventos()

            print(f"[{camara_id}] Evento detectado:", detecciones)


def main():
    camaras = cargar_camaras()

    if not camaras:
        print("No hay cámaras configuradas en data/camaras/camaras.json")
        return

    for camara in camaras:
        if not camara.get("activa", True):
            continue

        hilo = Thread(
            target=detectar_en_camara,
            args=(camara,),
            daemon=True
        )
        hilo.start()

    print("Detector multicámaras iniciado.")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()