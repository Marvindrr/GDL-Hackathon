import cv2
import tkinter as tk
from tkinter import StringVar
from threading import Thread
import numpy as np
import time
from ultralytics import YOLO

# CARGAR MODELO YOLOv8
modelo = YOLO("yolov8n.pt")


class AplicacionDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Detección - Multi Cámara")

        # VARIABLES
        self.tipo_objeto = StringVar(value="auto")
        self.color_objeto = StringVar(value="")
        self.ejecutando = True
        self.detectando = True
        self.contador_frames = 0
        self.ultimo_frame = None

        # INTERFAZ
        self.cuadro_camara_1 = tk.Label(self.root)
        self.cuadro_camara_1.grid(row=0, column=0)

        self.cuadro_camara_2 = tk.Label(self.root)
        self.cuadro_camara_2.grid(row=0, column=1)

        tk.Label(self.root, text="Tipo de objeto").grid(row=1, column=0)

        tk.OptionMenu(
            self.root,
            self.tipo_objeto,
            "auto", "moto", "autobus", "persona"
        ).grid(row=1, column=1)

        tk.Label(self.root, text="Color").grid(row=2, column=0)

        tk.OptionMenu(
            self.root,
            self.color_objeto,
            "Rojo", "Naranja", "Amarillo", "Verde",
            "Azul", "Morado", "Negro", "Blanco", "Gris"
        ).grid(row=2, column=1)

        tk.Button(self.root, text="Actualizar", command=self.actualizar_busqueda).grid(row=3, column=0)
        tk.Button(self.root, text="Limpiar", command=self.limpiar_busqueda).grid(row=3, column=1)

        # VENTANA SECUNDARIA
        self.ventana_secundaria = tk.Toplevel(self.root)
        self.ventana_secundaria.title("Última detección")

        self.label_secundario = tk.Label(self.ventana_secundaria)
        self.label_secundario.pack()

        # HILOS DE CÁMARAS
        self.hilo1 = Thread(target=self.mostrar_camara, args=(0, self.cuadro_camara_1), daemon=True)
        self.hilo2 = Thread(target=self.mostrar_camara, args=(1, self.cuadro_camara_2), daemon=True)

        self.hilo1.start()
        self.hilo2.start()

    # CONTROL
    def actualizar_busqueda(self):
        self.detectando = True

    def limpiar_busqueda(self):
        self.tipo_objeto.set("")
        self.color_objeto.set("")
        self.detectando = False

    # FILTRO
    def filtrar_objetos(self, detecciones):
        filtrados = []

        tipo = self.tipo_objeto.get().lower()
        color = self.color_objeto.get().lower()

        mapeo = {
            "auto": ["car", "truck"],
            "moto": ["motorcycle"],
            "autobus": ["bus"],
            "persona": ["person"]
        }

        etiquetas = mapeo.get(tipo, [])

        for det in detecciones:
            if det["name"] in etiquetas:
                if not color or color == det["color"].lower():
                    filtrados.append(det)

        return filtrados

    # COLOR
    def obtener_color_objeto(self, frame, x1, y1, x2, y2):
        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:
            return "Desconocido"

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        tono = np.argmax(hist)

        if 0 <= tono <= 10 or 160 <= tono <= 180:
            return "Rojo"
        elif 11 <= tono <= 25:
            return "Naranja"
        elif 26 <= tono <= 34:
            return "Amarillo"
        elif 35 <= tono <= 85:
            return "Verde"
        elif 86 <= tono <= 125:
            return "Azul"
        elif 126 <= tono <= 159:
            return "Morado"
        else:
            brillo = np.mean(roi)
            if brillo < 60:
                return "Negro"
            elif brillo > 180:
                return "Blanco"
            else:
                return "Gris"

    # CÁMARA 
    def mostrar_camara(self, cam_id, cuadro):
        cap = cv2.VideoCapture(cam_id)

        if not cap.isOpened():
            print(f"Cámara {cam_id} no disponible")
            return

        while self.ejecutando:
            ret, frame = cap.read()
            if not ret:
                break

            frame_procesado = frame.copy()

            self.contador_frames += 1

            if self.detectando and self.tipo_objeto.get() and self.contador_frames % 3 == 0:

                resultados = modelo(frame_procesado, conf=0.5)

                detecciones = []

                for r in resultados:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        etiqueta = r.names[cls]

                        det = {
                            "xmin": x1,
                            "ymin": y1,
                            "xmax": x2,
                            "ymax": y2,
                            "confidence": conf,
                            "name": etiqueta
                        }

                        det["color"] = self.obtener_color_objeto(frame_procesado, x1, y1, x2, y2)
                        detecciones.append(det)

                filtradas = self.filtrar_objetos(detecciones)

                if filtradas:
                    self.ultimo_frame = frame_procesado.copy()

                for det in filtradas:
                    x1, y1, x2, y2 = det["xmin"], det["ymin"], det["xmax"], det["ymax"]

                    cv2.rectangle(frame_procesado, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    cv2.putText(
                        frame_procesado,
                        f"{det['name']} ({det['color']}) {det['confidence']:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

                    # ALERTA
                    if det["name"] == "person":
                        print(f"NIGGERRRRRR  {cam_id}")

                        cv2.imwrite(f"alerta_cam{cam_id}_{int(time.time())}.jpg", frame_procesado)

            # TEXTO CÁMARA
            cv2.putText(frame_procesado, f"Camara {cam_id}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # CONVERSIÓN CORRECTA
            img = cv2.resize(frame_procesado, (640, 480))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            photo = tk.PhotoImage(
                data=cv2.imencode(".png", img_rgb)[1].tobytes()
            )

            cuadro.configure(image=photo)
            cuadro.image = photo

            # ÚLTIMA DETECCIÓN
            if self.ultimo_frame is not None:
                ult = cv2.resize(self.ultimo_frame, (640, 480))
                ult_rgb = cv2.cvtColor(ult, cv2.COLOR_BGR2RGB)

                photo2 = tk.PhotoImage(
                    data=cv2.imencode(".png", ult_rgb)[1].tobytes()
                )

                self.label_secundario.configure(image=photo2)
                self.label_secundario.image = photo2

        cap.release()

    # DETENER
    def detener(self):
        self.ejecutando = False
        self.root.destroy()


# MAIN
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionDetector(root)
    root.protocol("WM_DELETE_WINDOW", app.detener)
    root.mainloop()