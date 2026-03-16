import mysql.connector
import json


# Configuración de la conexión a la base de datos
db_config = {
    'host': 'localhost',  # Cambiado a 'localhost' ya que es tu usuario
    'user': 'root',       # Cambiado a 'root' ya que es tu usuario
    'password': '',  # Manteniendo tu contraseña
    'database': 'zona_de_riesgo'  # Cambia esto por tu nombre de base de datos
}

# Crear la conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(**db_config)
def cargar_puntos_zonas():
    with open(r'C:\Users\hiram\OneDrive\Desktop\SeguryTechs\colonias_modificado.json', 'r') as archivo:
        return json.load(archivo)

# Carga de los puntos de zonas
puntos_zonas = cargar_puntos_zonas()



def cargar_zonas_a_db():
    """Carga las zonas de riesgo en la base de datos."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    


    # Limpiar la tabla antes de insertar datos
    cursor.execute("DELETE FROM zonas")
    for colonia in puntos_zonas:
       
        nombre = colonia['nombre_colonia']
        lat = colonia['centro'][1]  # Latitud
        lng = colonia['centro'][0]  # Longitud
        riesgo = colonia['riesgo']# Asignar riesgo, 0 si no está en datos_riesgo
        query = "INSERT INTO zonas (nombre, riesgo, latitud, longitud) VALUES ( %s, %s, %s,%s)"
        print(query)
        cursor.execute(query, (nombre, riesgo,lat , lng))

    conexion.commit()
    cursor.close()
    conexion.close()
obtener_conexion()
cargar_zonas_a_db()