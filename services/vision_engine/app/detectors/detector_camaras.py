import os
import cv2
import time
import tkinter as tk
from tkinter import StringVar, ttk, messagebox
from threading import Thread, Lock

import numpy as np
from PIL import Image, ImageTk
from ultralytics import YOLO


# Importante: esto se usa cuando OpenCV abre streams mediante FFmpeg.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"


# - yolo11n.pt = más rápido, menos pesado
# - yolo11s.pt = buen balance
# - yolo11m.pt = más preciso, más pesado
MODELO_YOLO_DEFAULT = "yolo11s.pt"


class AplicacionDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Cámaras con YOLO11")

        self.ejecutando = True
        self.frame_mostrado = None
        self.estado_texto = "Inicializando..."
        self.lock_frame = Lock()

        # Modelo YOLO
        self.modelo_nombre_var = StringVar(value=MODELO_YOLO_DEFAULT)
        self.modelo = YOLO(MODELO_YOLO_DEFAULT)

        # Fuente de video
        self.tipo_fuente_var = StringVar(value="Local")
        self.indice_camara_var = tk.IntVar(value=0)
        self.url_camara_var = StringVar(value="")
        self.fuente_actual = None
        self.reconectar_solicitado = False

        # Filtro
        self.filtro_objeto = StringVar(value="Todos")

        self.clases_interes = {
            "person",
            "car",
            "motorcycle",
            "bus",
            "truck",
            "bicycle",
        }

        self.nombre_a_id = self.obtener_nombre_a_id()

        self.crear_interfaz()

        self.hilo_camara = Thread(target=self.capturar_y_detectar, daemon=True)
        self.hilo_camara.start()

        self.actualizar_ui()

    def obtener_nombre_a_id(self):
        return {
            nombre: class_id
            for class_id, nombre in self.modelo.names.items()
            if nombre in self.clases_interes
        }

    def crear_interfaz(self):
        frame_superior = tk.Frame(self.root)
        frame_superior.pack(pady=10)

        # Modelo
        tk.Label(frame_superior, text="Modelo YOLO:").pack(side="left", padx=5)

        self.combo_modelo = ttk.Combobox(
            frame_superior,
            textvariable=self.modelo_nombre_var,
            state="readonly",
            values=[
                "yolo11n.pt",
                "yolo11s.pt",
                "yolo11m.pt",
                "yolo11l.pt",
                "yolo11x.pt",
                #"yolo26n.pt",
            ],
            width=14
        )
        self.combo_modelo.pack(side="left", padx=5)

        self.btn_cargar_modelo = tk.Button(
            frame_superior,
            text="Cargar modelo",
            command=self.cargar_modelo
        )
        self.btn_cargar_modelo.pack(side="left", padx=5)

        # Filtro
        tk.Label(frame_superior, text="Buscar objeto:").pack(side="left", padx=5)

        self.combo_filtro = ttk.Combobox(
            frame_superior,
            textvariable=self.filtro_objeto,
            state="readonly",
            values=[
                "everyone",
                "person",
                "car",
                "motorcycle",
                "bus",
                "truck",
                "bicycle",
            ],
            width=15
        )
        self.combo_filtro.pack(side="left", padx=5)

        # Fuente
        frame_fuente = tk.Frame(self.root)
        frame_fuente.pack(pady=6)

        tk.Label(frame_fuente, text="Tipo de fuente:").pack(side="left", padx=5)

        self.combo_tipo_fuente = ttk.Combobox(
            frame_fuente,
            textvariable=self.tipo_fuente_var,
            state="readonly",
            values=["Local", "RTSP"],
            width=10
        )
        self.combo_tipo_fuente.pack(side="left", padx=5)
        self.combo_tipo_fuente.bind("<<ComboboxSelected>>", lambda event: self.cambiar_camara())

        tk.Label(frame_fuente, text="Cámara local #:").pack(side="left", padx=5)

        self.spin_camara = tk.Spinbox(
            frame_fuente,
            from_=0,
            to=10,
            width=4,
            textvariable=self.indice_camara_var,
            command=self.cambiar_camara
        )
        self.spin_camara.pack(side="left", padx=5)

        tk.Label(frame_fuente, text="URL RTSP:").pack(side="left", padx=5)

        self.entry_url_camara = tk.Entry(
            frame_fuente,
            textvariable=self.url_camara_var,
            width=60
        )
        self.entry_url_camara.pack(side="left", padx=5)

        self.btn_reconectar = tk.Button(
            frame_fuente,
            text="Conectar / Reconectar",
            command=self.cambiar_camara
        )
        self.btn_reconectar.pack(side="left", padx=5)

        # Estado
        self.label_estado = tk.Label(self.root, text="Inicializando...")
        self.label_estado.pack(pady=4)

        # Cámara
        self.cuadro_camara = tk.Label(self.root)
        self.cuadro_camara.pack()

    def cargar_modelo(self):
        nuevo_modelo = self.modelo_nombre_var.get().strip()

        if not nuevo_modelo:
            messagebox.showwarning("Modelo vacío", "Selecciona un modelo YOLO.")
            return

        try:
            self.actualizar_estado(f"Cargando modelo {nuevo_modelo}...")

            self.modelo = YOLO(nuevo_modelo)
            self.nombre_a_id = self.obtener_nombre_a_id()

            self.actualizar_estado(f"Modelo cargado: {nuevo_modelo}")

        except Exception as error:
            self.actualizar_estado("Error cargando modelo")
            messagebox.showerror(
                "Error cargando modelo",
                f"No se pudo cargar el modelo:\n{error}"
            )

    def actualizar_estado(self, texto):
        with self.lock_frame:
            self.estado_texto = texto

    def obtener_classes_filtradas(self):
        filtro = self.filtro_objeto.get()

        if filtro == "Todos":
            return list(self.nombre_a_id.values())

        if filtro in self.nombre_a_id:
            return [self.nombre_a_id[filtro]]

        return list(self.nombre_a_id.values())

    def obtener_fuente_camara(self):
        tipo = self.tipo_fuente_var.get()

        if tipo == "RTSP":
            url = self.url_camara_var.get().strip()

            if not url:
                return None

            return url

        return int(self.indice_camara_var.get())

    def abrir_captura(self, fuente):
        if fuente is None:
            return None

        cap = None

        # Cámara local
        if isinstance(fuente, int):
            cap = cv2.VideoCapture(fuente, cv2.CAP_DSHOW)

            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(fuente, cv2.CAP_ANY)

        # Cámara IP: RTSP/HTTP 
        else:
            cap = cv2.VideoCapture(fuente, cv2.CAP_FFMPEG)

            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(fuente, cv2.CAP_ANY)

        if cap is not None and cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        return cap

    def cambiar_camara(self):
        self.reconectar_solicitado = True
        self.actualizar_estado("Reconectando fuente de video...")

    def detectar_y_dibujar(self, frame):
        classes_filtradas = self.obtener_classes_filtradas()

        resultados = self.modelo.predict(
            source=frame,
            conf=0.20,
            imgsz=640,
            verbose=False,
            classes=classes_filtradas
        )

        total_detectados = 0

        if resultados:
            resultado = resultados[0]

            if resultado.boxes is not None:
                for box in resultado.boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                    nombre = self.modelo.names[cls_id]

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"{nombre} {conf:.2f}",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

                    total_detectados += 1

        filtro_txt = self.filtro_objeto.get()
        modelo_txt = self.modelo_nombre_var.get()

        estado = f"Modelo: {modelo_txt} | Filtro: {filtro_txt} | Detectados: {total_detectados}"
        self.actualizar_estado(estado)

        cv2.putText(
            frame,
            f"Filtro: {filtro_txt} | Detectados: {total_detectados}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        return frame

    def guardar_ultimo_frame(self, frame):
        cv2.imwrite("ultimo_frame.jpg", frame)

    def crear_frame_mensaje(self, texto):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        cv2.putText(
            frame,
            texto,
            (25, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        return frame

    def capturar_y_detectar(self):
        self.fuente_actual = self.obtener_fuente_camara()
        cap = self.abrir_captura(self.fuente_actual)

        if cap is None or not cap.isOpened():
            print(f"No se pudo abrir la fuente: {self.fuente_actual}")
            with self.lock_frame:
                self.frame_mostrado = self.crear_frame_mensaje(
                    "Fuente de video no disponible"
                )
            self.actualizar_estado("Fuente de video no disponible")

        ultimo_guardado = 0

        while self.ejecutando:
            nueva_fuente = self.obtener_fuente_camara()

            if self.reconectar_solicitado or nueva_fuente != self.fuente_actual:
                self.reconectar_solicitado = False
                self.fuente_actual = nueva_fuente

                if cap is not None:
                    cap.release()

                cap = self.abrir_captura(self.fuente_actual)

                if cap is None or not cap.isOpened():
                    with self.lock_frame:
                        self.frame_mostrado = self.crear_frame_mensaje(
                            "Fuente de video no disponible"
                        )

                    self.actualizar_estado("Fuente de video no disponible")
                    time.sleep(1)
                    continue

                self.actualizar_estado(f"Fuente conectada: {self.fuente_actual}")

            if cap is None or not cap.isOpened():
                time.sleep(0.5)
                continue

            ret, frame = cap.read()

            if not ret:
                with self.lock_frame:
                    self.frame_mostrado = self.crear_frame_mensaje(
                        "Sin señal de cámara"
                    )

                self.actualizar_estado("Sin señal de cámara")
                time.sleep(0.2)
                continue

            frame_detectado = self.detectar_y_dibujar(frame.copy())

            if time.time() - ultimo_guardado >= 2:
                self.guardar_ultimo_frame(frame_detectado)
                ultimo_guardado = time.time()

            with self.lock_frame:
                self.frame_mostrado = frame_detectado

        if cap is not None:
            cap.release()

    def actualizar_ui(self):
        with self.lock_frame:
            frame = self.frame_mostrado
            estado = self.estado_texto

        self.label_estado.config(text=estado)

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