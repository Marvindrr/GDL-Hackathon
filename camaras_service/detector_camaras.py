import cv2
import tkinter as tk
from tkinter import StringVar, ttk
from threading import Thread, Lock
import time
from ultralytics import YOLO
from PIL import Image, ImageTk

modelo = YOLO("yolov8s.pt")


class AplicacionDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector Cámara Externa")

        self.ejecutando = True
        self.frame_mostrado = None
        self.lock_frame = Lock()

        # Cambia este índice si tu cámara externa no es la 1
        self.indice_camara = 0

        # filtro
        self.filtro_objeto = StringVar(value="Todos")

        self.clases_interes = {
            "person",
            "car",
            "motorcycle",
            "bus",
            "truck",
            "bicycle",
        }

        self.nombre_a_id = {
            nombre: class_id
            for class_id, nombre in modelo.names.items()
            if nombre in self.clases_interes
        }

        # UI filtro
        frame_filtros = tk.Frame(root)
        frame_filtros.pack(pady=10)

        tk.Label(frame_filtros, text="Buscar objeto:").pack(side="left", padx=5)

        self.combo_filtro = ttk.Combobox(
            frame_filtros,
            textvariable=self.filtro_objeto,
            state="readonly",
            values=["Todos", "person", "car", "motorcycle", "bus", "truck", "bicycle"],
            width=15
        )
        self.combo_filtro.pack(side="left", padx=5)

        self.cuadro_camara = tk.Label(root)
        self.cuadro_camara.pack()

        self.hilo_camara = Thread(target=self.capturar_y_detectar, daemon=True)
        self.hilo_camara.start()

        self.actualizar_ui()

    def obtener_classes_filtradas(self):
        filtro = self.filtro_objeto.get()

        if filtro == "Todos":
            return list(self.nombre_a_id.values())

        if filtro in self.nombre_a_id:
            return [self.nombre_a_id[filtro]]

        return list(self.nombre_a_id.values())

    def detectar_y_dibujar(self, frame):
        classes_filtradas = self.obtener_classes_filtradas()

        resultados = modelo.predict(
            source=frame,
            conf=0.40,
            imgsz=640,
            verbose=False,
            classes=classes_filtradas
        )

        if not resultados:
            return frame

        resultado = resultados[0]

        if resultado.boxes is None:
            return frame

        for box in resultado.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            nombre = modelo.names[cls_id]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{nombre} {conf:.2f}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        return frame

    def guardar_ultimo_frame(self, frame):
        cv2.imwrite("ultimo_frame.jpg", frame)

    def capturar_y_detectar(self):
        cap = cv2.VideoCapture(self.indice_camara, cv2.CAP_DSHOW)

        if not cap.isOpened():
            print(f"No se pudo abrir la cámara externa en índice {self.indice_camara}")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        ultimo_guardado = 0

        while self.ejecutando:
            ret, frame = cap.read()

            if not ret:
                continue

            frame_detectado = self.detectar_y_dibujar(frame.copy())

            if time.time() - ultimo_guardado >= 2:
                self.guardar_ultimo_frame(frame_detectado)
                ultimo_guardado = time.time()

            with self.lock_frame:
                self.frame_mostrado = frame_detectado

        cap.release()

    def actualizar_ui(self):
        with self.lock_frame:
            frame = self.frame_mostrado

        if frame is not None:
            img = cv2.resize(frame, (800, 600))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(img))

            self.cuadro_camara.configure(image=img)
            self.cuadro_camara.image = img

        self.root.after(30, self.actualizar_ui)

    def detener(self):
        self.ejecutando = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionDetector(root)
    root.protocol("WM_DELETE_WINDOW", app.detener)
    root.mainloop()