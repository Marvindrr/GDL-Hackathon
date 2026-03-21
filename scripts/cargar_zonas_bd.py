import json
from pathlib import Path
from backend.database.conexion import obtener_conexion

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def cargar_json(nombre_archivo="colonias_jalisco.json"):
    ruta = DATA_DIR / nombre_archivo
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def normalizar_colonia(colonia):
    nombre = colonia.get("nombre_colonia")
    riesgo = colonia.get("riesgo")

    if "lat" in colonia and "lon" in colonia:
        lat = colonia["lat"]
        lng = colonia["lon"]
    elif "centro" in colonia and isinstance(colonia["centro"], list) and len(colonia["centro"]) == 2:
        lng = colonia["centro"][0]
        lat = colonia["centro"][1]
    else:
        return None

    return {
        "nombre": nombre,
        "riesgo": riesgo,
        "lat": lat,
        "lng": lng,
    }


def cargar_zonas(nombre_archivo="colonias_jalisco.json"):
    conexion = None
    cursor = None

    try:
        datos = cargar_json(nombre_archivo)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM zonas")

        query = """
        INSERT INTO zonas (nombre, riesgo, latitud, longitud)
        VALUES (%s, %s, %s, %s)
        """

        insertados = 0

        for colonia in datos:
            item = normalizar_colonia(colonia)
            if not item:
                continue

            cursor.execute(
                query,
                (
                    item["nombre"],
                    float(item["riesgo"]),
                    float(item["lat"]),
                    float(item["lng"]),
                ),
            )
            insertados += 1

        conexion.commit()
        print(f"{insertados} colonias cargadas correctamente")

    except Exception as e:
        print("Error al cargar zonas:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


if __name__ == "__main__":
    cargar_zonas()