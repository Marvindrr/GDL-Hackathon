import cv2
import tkinter as tk
from tkinter import StringVar
from threading import Thread
import numpy as np
from ultralytics import YOLO

# ==============================
# CARGAR MODELO YOLO
# ==============================
# Se carga el modelo pequeño para mejor rendimiento en tiempo real
modelo = YOLO("yolov5s.pt")


class AplicacionDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Detección de Objetos")

        # ==============================
        # VARIABLES DE CONTROL
        # ==============================
        self.tipo_objeto = StringVar(value="auto")
        self.color_objeto = StringVar(value="")
        self.ejecutando = True
        self.detectando = True
        self.contador_frames = 0
        self.ultimo_frame = None

        # ==============================
        # INTERFAZ PRINCIPAL
        # ==============================
        self.cuadro_camara = tk.Label(self.root)
        self.cuadro_camara.grid(row=0, column=0, columnspan=3)

        tk.Label(self.root, text="Tipo de objeto:").grid(row=1, column=0)
        self.tipo_objeto_menu = tk.OptionMenu(
            self.root,
            self.tipo_objeto,
            "auto",
            "moto",
            "autobus",
            "persona"
        )
        self.tipo_objeto_menu.grid(row=1, column=1)

        tk.Label(self.root, text="Color:").grid(row=2, column=0)
        self.color_objeto_menu = tk.OptionMenu(
            self.root,
            self.color_objeto,
            "Rojo",
            "Naranja",
            "Amarillo",
            "Verde",
            "Azul",
            "Morado",
            "Negro",
            "Blanco",
            "Gris"
        )
        self.color_objeto_menu.grid(row=2, column=1)

        tk.Button(self.root, text="Actualizar búsqueda",
                  command=self.actualizar_busqueda).grid(row=3, column=2)

        tk.Button(self.root, text="Limpiar búsqueda",
                  command=self.limpiar_busqueda).grid(row=3, column=1)

        # ==============================
        # VENTANA SECUNDARIA
        # ==============================
        self.ventana_secundaria = tk.Toplevel(self.root)
        self.ventana_secundaria.title("Último Frame con Detección")
        self.label_secundario = tk.Label(self.ventana_secundaria)
        self.label_secundario.grid(row=0, column=0)

        # ==============================
        # INICIAR HILO DE CÁMARA
        # ==============================
        self.hilo_camara = Thread(target=self.mostrar_camara, daemon=True)
        self.hilo_camara.start()

    # ==============================
    # CONTROL DE BÚSQUEDA
    # ==============================
    def actualizar_busqueda(self):
        self.detectando = True

    def limpiar_busqueda(self):
        self.tipo_objeto.set("")
        self.color_objeto.set("")
        self.detectando = False

    # ==============================
    # FILTRAR OBJETOS
    # ==============================
    def filtrar_objetos(self, detecciones):
        filtrados = []
        tipo_buscar = self.tipo_objeto.get().lower()
        color_buscar = self.color_objeto.get().lower()

        mapeo_tipo = {
            "auto": ["car", "truck"],
            "moto": ["motorcycle"],
            "autobus": ["bus"],
            "persona": ["person"],
        }

        etiquetas_validas = mapeo_tipo.get(tipo_buscar, [])

        for det in detecciones:
            if det["name"] in etiquetas_validas:
                if color_buscar in det["color"].lower():
                    filtrados.append(det)

        return filtrados

    # ==============================
    # DETECTAR COLOR DOMINANTE
    # ==============================
    def obtener_color_objeto(self, frame, x1, y1, x2, y2):
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return "Desconocido"

        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
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

    # ==============================
    # FUNCIÓN PRINCIPAL DE CÁMARA
    # ==============================
    def mostrar_camara(self):
        cap = cv2.VideoCapture(0)

        while self.ejecutando:
            ret, frame = cap.read()
            if not ret:
                break

            self.contador_frames += 1

            # Detectar cada 3 frames (optimización)
            if self.detectando and self.tipo_objeto.get() and self.contador_frames % 3 == 0:

                resultados = modelo(frame)
                resultado = resultados[0]

                detecciones = []

                # Extraer detecciones del nuevo formato YOLO
                for box in resultado.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    clase_id = int(box.cls[0])
                    etiqueta = resultado.names[clase_id]

                    detecciones.append({
                        "xmin": int(x1),
                        "ymin": int(y1),
                        "xmax": int(x2),
                        "ymax": int(y2),
                        "confidence": conf,
                        "name": etiqueta
                    })

                # Analizar color
                for det in detecciones:
                    det["color"] = self.obtener_color_objeto(
                        frame,
                        det["xmin"],
                        det["ymin"],
                        det["xmax"],
                        det["ymax"]
                    )

                detecciones_filtradas = self.filtrar_objetos(detecciones)

                if detecciones_filtradas:
                    self.ultimo_frame = frame.copy()

                # Dibujar detecciones
                for det in detecciones_filtradas:
                    x1, y1, x2, y2 = det["xmin"], det["ymin"], det["xmax"], det["ymax"]
                    etiqueta = det["name"]
                    color = det["color"]
                    conf = det["confidence"]

                    cv2.rectangle(frame, (x1, y1), (x2, y2),
                                  (0, 255, 0), 2)

                    cv2.putText(
                        frame,
                        f"{etiqueta} ({color}) {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

            # ==============================
            # MOSTRAR FRAME EN TKINTER
            # ==============================
            img = cv2.resize(frame, (640, 480))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            self.photo = tk.PhotoImage(
                data=cv2.imencode(".png", img_rgb)[1].tobytes()
            )

            self.cuadro_camara.configure(image=self.photo)
            self.cuadro_camara.image = self.photo

            # Mostrar último frame detectado
            if self.ultimo_frame is not None:
                ultimo = cv2.resize(self.ultimo_frame, (640, 480))
                ultimo_rgb = cv2.cvtColor(ultimo, cv2.COLOR_BGR2RGB)

                self.photo_ultimo = tk.PhotoImage(
                    data=cv2.imencode(".png", ultimo_rgb)[1].tobytes()
                )

                self.label_secundario.configure(image=self.photo_ultimo)
                self.label_secundario.image = self.photo_ultimo

        cap.release()

    # ==============================
    # DETENER APLICACIÓN
    # ==============================
    def detener(self):
        self.ejecutando = False
        self.root.destroy()


# ==============================
# EJECUCIÓN PRINCIPAL
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionDetector(root)
    root.protocol("WM_DELETE_WINDOW", app.detener)
    root.mainloop()
