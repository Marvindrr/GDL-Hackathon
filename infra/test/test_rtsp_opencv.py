import cv2

RTSP_URL = "rtsp://192.168.100.241:5543/0cddfebc8d53c702ed000de3bffaba0b/live/channel1"

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("No se pudo abrir el stream RTSP")
    exit()

print("Stream abierto correctamente")

for i in range(10):
    ok, frame = cap.read()

    if not ok:
        print("No se pudo leer frame")
        break

    print(f"Frame {i + 1} recibido:", frame.shape)

cap.release()
print("Prueba terminada")