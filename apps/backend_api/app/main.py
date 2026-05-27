import os
from pathlib import Path
import json
import re
import math
from app.api.routes.rutas_ia_routes import rutas_ia_bp
from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from app.modules.gdl_turismo.backend.gdl_routes import gdl_turismo_bp
from app.api.routes.detecciones_routes import detecciones_bp

BASE_DIR = Path(os.getenv("PROJECT_ROOT", "/workspace"))
FRONTEND_DIR = Path(os.getenv("FRONTEND_LEGACY_DIR", "/workspace/apps/frontend_legacy"))
DATA_DIR = Path(os.getenv("DATA_DIR", "/workspace/data"))

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static"),
)
app.config["SECRET_KEY"] = "mysecret"
app.register_blueprint(gdl_turismo_bp)
app.register_blueprint(rutas_ia_bp)
app.register_blueprint(detecciones_bp)
socketio = SocketIO(app)

@app.route("/gdl_static/data/<path:filename>")
def gdl_static_data(filename):
    data_dir = FRONTEND_DIR / "static" / "modules" / "gdl_turismo" / "data"
    return send_from_directory(data_dir, filename)

@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "Backend API is running"
    }


def cargar_puntos_zonas():
    ruta = DATA_DIR / "geo" / "colonias_gdl.json"
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def ubicaciones_camaras():
    ruta = DATA_DIR / "geo" / "ubicaciones_camaras.json"
    if not ruta.exists():
        print(f"No se encontro el archivo de camaras: {ruta}")
        return []

    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def clasificar_por_riesgo(colonias):
    bajo, moderado, alto, muy_alto = [], [], [], []
    for colonia in colonias:
        nombre = colonia["nombre_colonia"]
        lat = colonia["centro"][1]
        lng = colonia["centro"][0]
        riesgo = colonia["riesgo"]

        item = {"nombre": nombre, "lat": lat, "lng": lng, "riesgo": riesgo}

        if 0 <= riesgo <= 25:
            bajo.append(item)
        elif 26 <= riesgo <= 50:
            moderado.append(item)
        elif 51 <= riesgo <= 75:
            alto.append(item)
        elif 76 <= riesgo <= 100:
            muy_alto.append(item)
    return bajo, moderado, alto, muy_alto


puntos_zonas = cargar_puntos_zonas()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/camara")
def camara():
    return render_template("camara.html")


@socketio.on("mostrar_zonas_riesgo")
def handle_mostrar_zonas_riesgo():
    zonas_con_riesgo = [
        {
            "nombre": c["nombre_colonia"],
            "lat": c["centro"][1],
            "lng": c["centro"][0],
            "riesgo": c["riesgo"],
        }
        for c in puntos_zonas
    ]
    socketio.emit("zonas_riesgo", zonas_con_riesgo)


def calcular_distancia(coord1, coord2):
    r = 6371
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return r * c


@app.route("/mapa/<int:opcion>")
def mapa(opcion):
    zonas_con_riesgo = [
        {
            "nombre": c["nombre_colonia"],
            "lat": c["centro"][1],
            "lng": c["centro"][0],
            "riesgo": c["riesgo"],
        }
        for c in puntos_zonas
    ]

    bajo, moderado, alto, muy_alto = clasificar_por_riesgo(puntos_zonas)

    if opcion == 1:
        return render_template("mapa.html", lista=bajo)
    elif opcion == 2:
        return render_template("mapa.html", lista=moderado)
    elif opcion == 3:
        return render_template("mapa.html", lista=alto)
    elif opcion == 4:
        return render_template("mapa.html", lista=muy_alto)
    else:
        return render_template("mapa.html", lista=zonas_con_riesgo)


@socketio.on("search")
def handle_search(query):
    results = [
        colonia
        for colonia in puntos_zonas
        if query.lower() in colonia["nombre_colonia"].lower()
    ]
    socketio.emit("search_results", results)


@socketio.on("ruta_cambiada")
def handle_ruta_cambiada(data):
    distancia = data.get("distancia")
    duracion = data.get("duracion")
    waypoints = data.get("waypoints")
    calles = data.get("calles") or []

    calles_str = "Calles por las que pasa la ruta:\n"
    for calle in calles:
        calles_str += calle + "\n"

    print(distancia, duracion, waypoints)
    print(calles_str)


def separate_by_street(text):
    lines = text.strip().split("\n")
    streets = []

    for line in lines:
        match = re.search(r"\b(C|A)\w+.*", line)
        if match:
            streets.append(match.group(0))

    return streets


@socketio.on("waypoint_dragged")
def handle_waypoint_dragged(data):
    waypoints = data["waypoints"]
    print("Puntos de control actualizados:", waypoints)


@app.route("/estadisticas/<int:opcion>")
def estadisticas(opcion):
    # Aquí todavía te faltan estos imports/funciones reales:
    # from apps.backend_api.app.infrastructure.db.conexion import obtener_conexion
    # from ... import graficar_datos
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, riesgo FROM zonas order by riesgo desc;")
        bd = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f"Error al consultar BD: {e}")
        bd = []

    nombres1 = [c[0] for c in bd]
    riesgos1 = [c[1] for c in bd]
    combinados = list(zip(nombres1, riesgos1))
    img1 = graficar_datos(opcion)

    return render_template("estadisticas.html", img=img1, combinados=combinados)


@socketio.on("enviar_coordenadas")
def handle_coordinates(data):
    lat = data["lat"]
    lon = data["lng"]
    radio = 1

    camaras = ubicaciones_camaras()
    camaras_cercanas = []

    for camara in camaras:
        try:
            camara_coord = (camara["lat"], camara["lon"])
            distancia = calcular_distancia((lat, lon), camara_coord)

            if distancia <= radio:
                camaras_cercanas.append(camara)
        except KeyError:
            print(f"Cámara con id {camara.get('id')} no tiene coordenadas válidas.")
            continue

    socketio.emit("camaras_cercanas", camaras_cercanas)


if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        allow_unsafe_werkzeug=True
    )
