import json
from pathlib import Path
from backend.database.conexion import obtener_conexion


def cargar_json(nombre_archivo="colonias_jalisco.json"):
    ruta = Path(__file__).resolve().parent.parent / "data" / nombre_archivo

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_zonas(nombre_archivo="colonias_jalisco.json"):
    conexion = None
    cursor = None

    try:
        datos = cargar_json(nombre_archivo)

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM zonas")

        query = """
        INSERT INTO zonas (
            id,
            estado,
            municipio,
            nombre,
            riesgo,
            latitud,
            longitud
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for colonia in datos:
            cursor.execute(
                query,
                (
                    int(colonia["id"]),
                    colonia["estado"],
                    colonia["municipio"],
                    colonia["nombre_colonia"],
                    float(colonia["riesgo"]),
                    float(colonia["lat"]),
                    float(colonia["lon"]),
                ),
            )

        conexion.commit()
        print(f"{len(datos)} colonias cargadas correctamente")

    except Exception as e:
        print("Error al cargar zonas:", e)

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


if __name__ == "__main__":
    cargar_zonas()