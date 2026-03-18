import mysql.connector
import json
import os

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",      #----------------- Si su BD tiene contraseña ponla ahí mismo ------------------#
    "database": "zona_de_riesgo"
}

def obtener_conexion():
    return mysql.connector.connect(**db_config)

def cargar_json():

    ruta = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "colonias_gdl.json"
    )

    with open(ruta,"r",encoding="utf-8") as f:
        return json.load(f)

def cargar_zonas():

    datos = cargar_json()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM zonas")

    for colonia in datos:

        nombre = colonia["nombre_colonia"]
        lat = colonia["centro"][1]
        lng = colonia["centro"][0]
        riesgo = colonia["riesgo"]

        query = """
        INSERT INTO zonas(nombre,riesgo,latitud,longitud)
        VALUES(%s,%s,%s,%s)
        """

        cursor.execute(query,(nombre,riesgo,lat,lng))

    conexion.commit()

    cursor.close()
    conexion.close()

    print("Colonias cargadas correctamente")

if __name__ == "__main__":              #---------------------
    cargar_zonas()                      # BANDIA BANDIA BANDIA
                                        #---------------------