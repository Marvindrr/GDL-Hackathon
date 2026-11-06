import os
import time
import requests
import cv2


API_URL = os.getenv(
    "DETECTION_API_URL",
    "http://localhost:5000/api/detecciones/persona",
)

CAMERA_CODE = os.getenv("CAMERA_CODE", "WEBCAM_LAPTOP_LAB")
TRACKING_ID = os.getenv("TRACKING_ID", "demo_person_001")

CAMERA_LAT = float(os.getenv("CAMERA_LAT", "20.677055"))
CAMERA_LON = float(os.getenv("CAMERA_LON", "-103.347063"))

WEBCAM_INDEX = int(os.getenv("WEBCAM_INDEX", "0"))


def dominant_color_name(frame, bbox):
    x = max(0, bbox["x"])
    y = max(0, bbox["y"])
    w = max(1, bbox["width"])
    h = max(1, bbox["height"])

    crop = frame[y:y + h, x:x + w]

    if crop.size == 0:
        return "desconocido"

    b, g, r, _ = cv2.mean(crop)

    if r > 160 and g > 160 and b > 160:
        return "blanco"

    if r < 70 and g < 70 and b < 70:
        return "negro"

    if abs(r - g) < 25 and abs(g - b) < 25:
        return "gris"

    if r > g and r > b:
        if g > 120:
            return "amarillo"
        return "rojo"

    if g > r and g > b:
        return "verde"

    if b > r and b > g:
        return "azul"

    return "desconocido"


def send_detection(frame, bbox):
    color = dominant_color_name(frame, bbox)

    payload = {
        "codigo_camara": CAMERA_CODE,
        "clase_detectada": "person",
        "confianza": 0.80,
        "color_dominante": color,
        "bbox": bbox,
        "lat": CAMERA_LAT,
        "lon": CAMERA_LON,
        "tracking_id": TRACKING_ID,
        "source": "webcam_laptop_manual",
        "calcular_ruta": True,
        "radio_m": 500,
    }

    response = requests.post(API_URL, json=payload, timeout=20)

    print("Status:", response.status_code)

    try:
        print(response.json())
    except Exception:
        print(response.text)


def main():
    print("Iniciando webcam laptop...")
    print(f"API: {API_URL}")
    print(f"Cámara lógica: {CAMERA_CODE}")
    print(f"Ubicación simulada: {CAMERA_LAT}, {CAMERA_LON}")

    cap = cv2.VideoCapture(WEBCAM_INDEX, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("No se pudo abrir la cámara de la laptop.")
        print("Prueba cambiando WEBCAM_INDEX=1 o WEBCAM_INDEX=2.")
        return

    last_send = 0

    while True:
        ok, frame = cap.read()

        if not ok:
            print("No se pudo leer frame.")
            break

        height, width = frame.shape[:2]

        bbox_w = int(width * 0.28)
        bbox_h = int(height * 0.55)
        bbox_x = int((width - bbox_w) / 2)
        bbox_y = int((height - bbox_h) / 2)

        bbox = {
            "x": bbox_x,
            "y": bbox_y,
            "width": bbox_w,
            "height": bbox_h,
        }

        cv2.rectangle(
            frame,
            (bbox_x, bbox_y),
            (bbox_x + bbox_w, bbox_y + bbox_h),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            "Presiona D para enviar deteccion | Q para salir",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Webcam Laptop - Demo Deteccion", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == ord("d"):
            now = time.time()

            if now - last_send > 1.5:
                print("Enviando detección...")
                send_detection(frame, bbox)
                last_send = now
            else:
                print("Espera un momento antes de enviar otra detección.")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()