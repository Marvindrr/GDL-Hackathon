import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Xoceandav12",
    "database": "zona_de_riesgo"
}

def obtener_conexion():
    return mysql.connector.connect(**db_config)