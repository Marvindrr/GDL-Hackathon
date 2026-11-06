import cv2
import time

RTSP_URL = "rtsp://192.168.100.241:5543/0cddfebc8d53c702ed000de3bffaba0b/live/channel1"

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("No se pudo abrir el stream")
    exit()

start = time.time()
frames = 0

while time.time() - start < 10:
    ok, frame = cap.read()

    if not ok:
        print("Frame perdido")
        continue

    frames += 1

cap.release()

elapsed = time.time() - start
print(f"Frames leídos: {frames}")
print(f"FPS aproximado: {frames / elapsed:.2f}")