from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import json
import re
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

socketio = SocketIO(app)


def cargar_puntos_zonas():
    with open(r"data\colonias_gdl.json", "r") as archivo:
        return json.load(archivo)

def ubicaciones_camaras():
    with open(r"data\ubicaciones_camaras.json", "r") as archivo:
        return json.load(archivo)

def clasificar_por_riesgo(colonias):
    """Divide colonias según rango de riesgo."""
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camara')
def camara():
    return render_template('camara.html')

@socketio.on('mostrar_zonas_riesgo')
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

    socketio.emit('zonas_riesgo', zonas_con_riesgo)

def calcular_distancia(coord1, coord2):
    R = 6371 
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    return R * c  
    
@app.route('/mapa/<int:opcion>')
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
        return render_template('mapa.html', lista=bajo)
    elif opcion == 2:
        return render_template('mapa.html', lista=moderado)
    elif opcion == 3:
        return render_template('mapa.html', lista=alto)
    elif opcion == 4:
        return render_template('mapa.html', lista=muy_alto)
    else:
        return render_template('mapa.html', lista=zonas_con_riesgo)
        

@socketio.on('search')
def handle_search(query):
    results = [colonia for colonia in puntos_zonas if query.lower() in colonia['nombre_colonia'].lower()]
    socketio.emit('search_results', results)

@socketio.on('ruta_cambiada')
def handle_ruta_cambiada(data):
    distancia = data.get('distancia')
    duracion = data.get('duracion')
    waypoints = data.get('waypoints')
    calles = data.get('calles') 


    calles_str = "Calles por las que pasa la ruta:\n"


    for calle in calles:
        calles_str += calle + '\n'  

def separate_by_street(text):
    lines = text.strip().split('\n') 
    streets = []
    
    for line in lines:
        match = re.search(r'\b(C|A)\w+.*', line)
        if match:
            street = match.group(0)  
            streets.append(street)
    
    return streets
    
@socketio.on('waypoint_dragged')
def handle_waypoint_dragged(data):
    waypoints = data['waypoints']
    print("Puntos de control actualizados:", waypoints)

@app.route('/estadisticas/<int:opcion>')
def estadisticas(opcion):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, riesgo FROM zonas order by riesgo desc;")
        BD = cursor.fetchall()
        cursor.close()
        conexion.close()
    except Exception as e:
        print(f"Error al consultar BD: {e}")
        BD = []

    nombres1 = [c[0] for c in BD]
    riesgos1 = [c[1] for c in BD]
    combinados = list(zip(nombres1, riesgos1))
    img1=graficar_datos(opcion)
        
        
    return render_template('estadisticas.html',img=img1,combinados=combinados)


@socketio.on('enviar_coordenadas')
def handle_coordinates(data):
    lat = data['lat']
    lon = data['lng']
    radio = 1  

    camaras = ubicaciones_camaras()

    camaras_cercanas = []
    for camara in camaras:
        try:
            camara_coord = (camara['lat'], camara['lon'])
            distancia = calcular_distancia((lat, lon), camara_coord)

            if distancia <= radio:
                camaras_cercanas.append(camara)
        except KeyError:
            print(f"Cámara con id {camara.get('id')} no tiene coordenadas válidas.")
            continue


    socketio.emit('camaras_cercanas', camaras_cercanas)



if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
