import os
import time
import requests
from urllib.parse import quote
from requests import Session
from requests.exceptions import RequestException


class DenueClient:
    BASE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta"

    def __init__(self):
        self.token = os.getenv("DENUE_TOKEN")

        if not self.token:
            raise RuntimeError("Falta DENUE_TOKEN en variables de entorno.")

        self.session = Session()
        self.session.headers.update({
            "User-Agent": "SeguryTech-Hackathon/1.0",
            "Accept": "application/json,text/plain,*/*",
        })

    def buscar_area_act_estr(
        self,
        entidad: str,
        municipio: str,
        nombre: str,
        registro_inicial: int = 1,
        registro_final: int = 200,
        localidad: str = "0",
        ageb: str = "0",
        manzana: str = "0",
        sector: str = "0",
        subsector: str = "0",
        rama: str = "0",
        clase: str = "0",
        id_establecimiento: str = "0",
        estrato: str = "0",
        retries: int = 3,
        sleep_seconds: float = 2.0,
    ) -> list[dict]:

        nombre_encoded = quote(nombre)

        url = (
            f"{self.BASE_URL}/BuscarAreaActEstr/"
            f"{entidad}/{municipio}/{localidad}/{ageb}/{manzana}/"
            f"{sector}/{subsector}/{rama}/{clase}/{nombre_encoded}/"
            f"{registro_inicial}/{registro_final}/{id_establecimiento}/{estrato}/{self.token}"
        )

        last_error = None

        for intento in range(1, retries + 1):
            try:
                response = self.session.get(url, timeout=45)
                response.raise_for_status()

                data = response.json()

                if not isinstance(data, list):
                    return []

                return data

            except RequestException as e:
                last_error = e
                print(
                    f"    Intento {intento}/{retries} falló para '{nombre}' "
                    f"registros {registro_inicial}-{registro_final}: {e}"
                )

                if intento < retries:
                    time.sleep(sleep_seconds * intento)

            except ValueError as e:
                last_error = e
                print(
                    f"    Respuesta no JSON para '{nombre}' "
                    f"registros {registro_inicial}-{registro_final}: {e}"
                )

                if intento < retries:
                    time.sleep(sleep_seconds * intento)

        print(
            f"    No se pudo consultar DENUE para '{nombre}' "
            f"registros {registro_inicial}-{registro_final}. Se omite este bloque."
        )

        return []

    def buscar_todos_paginado(
        self,
        entidad: str,
        municipio: str,
        nombre: str,
        page_size: int = 100,
        max_pages: int = 20,
        sleep_seconds: float = 1.0,
    ) -> list[dict]:
        todos = []
        inicio = 1

        for page in range(max_pages):
            fin = inicio + page_size - 1

            batch = self.buscar_area_act_estr(
                entidad=entidad,
                municipio=municipio,
                nombre=nombre,
                registro_inicial=inicio,
                registro_final=fin,
            )

            if not batch:
                break

            todos.extend(batch)

            if len(batch) < page_size:
                break

            inicio = fin + 1
            time.sleep(sleep_seconds)

        return todos