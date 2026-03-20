import json
import os
from backend.database.conexion import obtener_conexion

def cargar_json():
    ruta = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "colonias_gdl.json"
    )

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_zonas():
    try:
        datos = cargar_json()

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # limpiar tabla
        cursor.execute("DELETE FROM zonas")

        for colonia in datos:
            nombre = colonia["nombre_colonia"]
            lat = colonia["centro"][1]
            lng = colonia["centro"][0]
            riesgo = colonia["riesgo"]

            query = """
            INSERT INTO zonas (nombre, riesgo, latitud, longitud)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(query, (nombre, riesgo, lat, lng))

        conexion.commit()

        print(f"{len(datos)} colonias cargadas correctamente")

    except Exception as e:
        print("Error al cargar zonas:", e)

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    cargar_zonas()