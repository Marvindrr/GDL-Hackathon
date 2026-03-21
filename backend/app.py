from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import json
import re
import math
from pathlib import Path

from data.validators import cargar_colonias_desde_json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATA_DIR = PROJECT_ROOT / "data"

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / "templates"),
    static_folder=str(FRONTEND_DIR / "static"),
)
app.config["SECRET_KEY"] = "mysecret"

socketio = SocketIO(app)

ARCHIVO_COLONIAS = "colonias_jalisco.json"


def ubicaciones_camaras():
    ruta = DATA_DIR / "ubicaciones_camaras.json"
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


puntos_zonas = cargar_colonias_desde_json(
    ARCHIVO_COLONIAS,
    municipio="Guadalajara"
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/camara")
def camara():
    return render_template("camara.html")


def clasificar_zonas(colonias):
    zonas_con_riesgo = []
    bajo = []
    moderado = []
    alto = []
    muy_alto = []

    for colonia in colonias:
        nombre = colonia["nombre_colonia"]
        lat = colonia["lat"]
        lng = colonia["lon"]
        riesgo = colonia["riesgo"]

        item = {
            "nombre": nombre,
            "lat": lat,
            "lng": lng,
            "riesgo": riesgo,
            "municipio": colonia.get("municipio"),
            "estado": colonia.get("estado"),
        }

        zonas_con_riesgo.append(item)

        if 0 <= riesgo <= 25:
            bajo.append(item)
        elif 26 <= riesgo <= 50:
            moderado.append(item)
        elif 51 <= riesgo <= 75:
            alto.append(item)
        elif 76 <= riesgo <= 100:
            muy_alto.append(item)

    return zonas_con_riesgo, bajo, moderado, alto, muy_alto


def calcular_distancia(coord1, coord2):
    R = 6371
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

    return R * c


@app.route("/mapa/<int:opcion>")
def mapa(opcion):
    zonas_con_riesgo, bajo, moderado, alto, muy_alto = clasificar_zonas(puntos_zonas)

    if opcion == 1:
        return render_template("mapa_gdl.html", lista=bajo)
    elif opcion == 2:
        return render_template("mapa_gdl.html", lista=moderado)
    elif opcion == 3:
        return render_template("mapa_gdl.html", lista=alto)
    elif opcion == 4:
        return render_template("mapa_gdl.html", lista=muy_alto)
    else:
        return render_template("mapa_gdl.html", lista=zonas_con_riesgo)


@app.route("/api/colonias", methods=["GET"])
def api_colonias():
    municipio = request.args.get("municipio")

    colonias = cargar_colonias_desde_json(
        ARCHIVO_COLONIAS,
        municipio=municipio
    )

    return jsonify(colonias)


@app.route("/api/ruta", methods=["POST"])
def api_ruta():
    data = request.get_json()

    origen = data.get("origen")
    destino = data.get("destino")
    municipio = data.get("municipio")
    tipo_ruta = data.get("tipo_ruta")

    return jsonify({
        "origen": origen,
        "destino": destino,
        "municipio": municipio,
        "tipo_ruta": tipo_ruta,
        "riesgo_total": "Medio",
        "distancia": "4.2 km",
        "tiempo": "11 min",
        "camaras_cercanas": 5,
        "colonias_criticas": ["Analco", "Oblatos"],
        "ruta": [
            [20.6767, -103.3475],
            [20.6730, -103.3400],
            [20.6680, -103.3350]
        ]
    })


@socketio.on("mostrar_zonas_riesgo")
def handle_mostrar_zonas_riesgo():
    zonas_con_riesgo, _, _, _, _ = clasificar_zonas(puntos_zonas)
    socketio.emit("zonas_riesgo", zonas_con_riesgo)


@socketio.on("search")
def handle_search(query):
    query = query.strip().lower()
    results = [
        colonia for colonia in puntos_zonas
        if query in colonia["nombre_colonia"].lower()
    ]
    socketio.emit("search_results", results)


@socketio.on("ruta_cambiada")
def handle_ruta_cambiada(data):
    calles = data.get("calles", [])

    calles_str = "Calles por las que pasa la ruta:\n"
    for calle in calles:
        calles_str += calle + "\n"

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
            print(f'Cámara con id {camara.get("id")} no tiene coordenadas válidas.')
            continue

    socketio.emit("camaras_cercanas", camaras_cercanas)


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)