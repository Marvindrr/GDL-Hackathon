import ast
import math
import unicodedata
from difflib import get_close_matches
from pathlib import Path


def get_project_root():
    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "apps").exists() and (parent / "data").exists():
            return parent

    raise RuntimeError("No se encontró la raíz del proyecto.")


def get_mapa_service_path():
    root = get_project_root()

    return (
        root
        / "apps"
        / "backend_api"
        / "app"
        / "application"
        / "services"
        / "mapa_service.py"
    )


def leer_diccionario_desde_mapa_service(nombre_variable):
    path = get_mapa_service_path()

    if not path.exists():
        raise FileNotFoundError(f"No existe mapa_service.py en: {path}")

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == nombre_variable:
                    return ast.literal_eval(node.value)

    return {}


def normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(char for char in texto if unicodedata.category(char) != "Mn")


def crear_id(texto):
    return normalizar_texto(texto).replace(" ", "_")


def obtener_nivel_riesgo(riesgo):
    if riesgo >= 60:
        return "alto"

    if riesgo >= 40:
        return "medio"

    return "bajo"


def obtener_color_riesgo(riesgo):
    nivel = obtener_nivel_riesgo(riesgo)

    if nivel == "alto":
        return "red"

    if nivel == "medio":
        return "orange"

    return "green"


def obtener_radio_riesgo(riesgo):
    nivel = obtener_nivel_riesgo(riesgo)

    if nivel == "alto":
        return 450

    if nivel == "medio":
        return 350

    return 250


def obtener_datos_mapa():
    puntos_zonas = leer_diccionario_desde_mapa_service("puntos_zonas")
    datos_riesgo = leer_diccionario_desde_mapa_service("datos_riesgo")
    puntos_escape = leer_diccionario_desde_mapa_service("puntos_escape")

    return puntos_zonas, datos_riesgo, puntos_escape


def listar_zonas():
    puntos_zonas, datos_riesgo, _ = obtener_datos_mapa()

    zonas = []

    for nombre, coords in puntos_zonas.items():
        latitud, longitud = coords
        riesgo = int(datos_riesgo.get(nombre, 0))

        zonas.append({
            "id": crear_id(nombre),
            "nombre": nombre,
            "latitud": float(latitud),
            "longitud": float(longitud),
            "riesgo": riesgo,
            "nivel_riesgo": obtener_nivel_riesgo(riesgo),
            "color": obtener_color_riesgo(riesgo),
            "radio": obtener_radio_riesgo(riesgo),
        })

    return zonas


def listar_puntos_escape():
    _, _, puntos_escape = obtener_datos_mapa()

    puntos = []

    for nombre, coords in puntos_escape.items():
        latitud, longitud = coords

        puntos.append({
            "id": crear_id(nombre),
            "nombre": nombre,
            "latitud": float(latitud),
            "longitud": float(longitud),
        })

    return puntos


def buscar_zona(nombre):
    if not nombre:
        return None

    zonas = listar_zonas()
    query = normalizar_texto(nombre)

    for zona in zonas:
        if normalizar_texto(zona["nombre"]) == query:
            return zona

    for zona in zonas:
        if query in normalizar_texto(zona["nombre"]):
            return zona

    nombres = [zona["nombre"] for zona in zonas]

    coincidencias = get_close_matches(
        nombre,
        nombres,
        n=1,
        cutoff=0.45
    )

    if not coincidencias:
        return None

    nombre_encontrado = coincidencias[0]

    for zona in zonas:
        if zona["nombre"] == nombre_encontrado:
            return zona

    return None


def distancia_haversine(lat1, lon1, lat2, lon2):
    radio_tierra_km = 6371

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra_km * c


def obtener_escape_mas_cercano(latitud, longitud):
    puntos_escape = listar_puntos_escape()

    mejor = None
    mejor_distancia = float("inf")

    for punto in puntos_escape:
        distancia = distancia_haversine(
            latitud,
            longitud,
            punto["latitud"],
            punto["longitud"],
        )

        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor = {
                "id": punto["id"],
                "nombre": punto["nombre"],
                "latitud": punto["latitud"],
                "longitud": punto["longitud"],
                "distancia_km": round(distancia, 2),
            }

    return mejor


def calcular_ruta_escape(origen):
    latitud = float(origen.get("latitud") or origen.get("lat"))
    longitud = float(origen.get("longitud") or origen.get("lng"))

    escape = obtener_escape_mas_cercano(latitud, longitud)

    if not escape:
        return None

    return {
        "destino": escape,
        "ruta": [
            [latitud, longitud],
            [escape["latitud"], escape["longitud"]],
        ],
    }