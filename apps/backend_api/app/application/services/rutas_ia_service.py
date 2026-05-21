from dataclasses import dataclass

from sqlalchemy import func

from app.infrastructure.db.models.geo_models import Zona
from app.infrastructure.db.models.security_point_models import PuntoSeguridad
from app.infrastructure.db.models.route_models import RutaCalculada, RutaPuntoControl
from app.application.services.route_geo_utils import (
    distance_point_to_route_m,
    haversine_m,
    linestring_wkt,
    midpoint,
    offset_point_m,
    point_to_geojson_feature,
    point_wkt,
    route_distance_m,
    route_to_geojson_feature,
)


@dataclass
class ZonaRiesgo:
    id_zona: int
    nombre: str
    tipo: str
    riesgo: float
    lat: float
    lon: float


@dataclass
class PuntoSeguro:
    id_punto_seguridad: int
    nombre: str
    marca: str
    tipo_punto: str
    peso_seguridad: float
    nivel_confianza: float
    validado_c5: bool
    lat: float
    lon: float


class RutasIAService:
    ALGORITMO_RUTA_SEGURA = "SAFE_ROUTE_HEURISTIC_V1"
    ALGORITMO_RUTA_PROBABLE = "SUSPECT_ROUTE_HEURISTIC_V1"

    RADIO_ZONA_RIESGO_M = 700
    RADIO_PUNTO_SEGURO_M = 180
    BONO_MAX_PUNTOS_SEGUROS = 22

    def __init__(self, db):
        self.db = db

    def obtener_zonas_con_centro(self) -> list[ZonaRiesgo]:
        rows = (
            self.db.query(
                Zona.id_zona,
                Zona.nombre,
                Zona.tipo,
                Zona.riesgo_base,
                func.ST_Y(Zona.centro).label("lat"),
                func.ST_X(Zona.centro).label("lon"),
            )
            .filter(Zona.centro.isnot(None))
            .all()
        )

        zonas = []

        for row in rows:
            zonas.append(
                ZonaRiesgo(
                    id_zona=row.id_zona,
                    nombre=row.nombre,
                    tipo=row.tipo,
                    riesgo=float(row.riesgo_base or 0),
                    lat=float(row.lat),
                    lon=float(row.lon),
                )
            )

        return zonas

    def obtener_puntos_seguridad_activos(self) -> list[PuntoSeguro]:
        rows = (
            self.db.query(
                PuntoSeguridad.id_punto_seguridad,
                PuntoSeguridad.nombre,
                PuntoSeguridad.marca,
                PuntoSeguridad.tipo_punto,
                PuntoSeguridad.peso_seguridad,
                PuntoSeguridad.nivel_confianza,
                PuntoSeguridad.validado_c5,
                func.ST_Y(PuntoSeguridad.ubicacion).label("lat"),
                func.ST_X(PuntoSeguridad.ubicacion).label("lon"),
            )
            .filter(PuntoSeguridad.activo.is_(True))
            .all()
        )

        puntos = []

        for row in rows:
            puntos.append(
                PuntoSeguro(
                    id_punto_seguridad=row.id_punto_seguridad,
                    nombre=row.nombre,
                    marca=row.marca or "",
                    tipo_punto=row.tipo_punto,
                    peso_seguridad=float(row.peso_seguridad or 0),
                    nivel_confianza=float(row.nivel_confianza or 50),
                    validado_c5=bool(row.validado_c5),
                    lat=float(row.lat),
                    lon=float(row.lon),
                )
            )

        return puntos

    def calcular_riesgo_zonas(
        self,
        route_points: list[dict],
        zonas: list[ZonaRiesgo],
        radio_influencia_m: float = RADIO_ZONA_RIESGO_M,
    ) -> dict:
        zonas_influyentes = []
        suma_pesos = 0.0
        suma_riesgo = 0.0
        max_riesgo = 0.0

        for zona in zonas:
            punto_zona = {
                "lat": zona.lat,
                "lon": zona.lon,
            }

            distancia = distance_point_to_route_m(punto_zona, route_points)

            if distancia <= radio_influencia_m:
                peso = max(0.05, 1 - (distancia / radio_influencia_m))
                riesgo_ponderado = zona.riesgo * peso

                suma_pesos += peso
                suma_riesgo += riesgo_ponderado
                max_riesgo = max(max_riesgo, zona.riesgo)

                zonas_influyentes.append(
                    {
                        "id_zona": zona.id_zona,
                        "nombre": zona.nombre,
                        "tipo": zona.tipo,
                        "riesgo": zona.riesgo,
                        "distancia_m": round(distancia, 2),
                        "peso": round(peso, 4),
                    }
                )

        if suma_pesos == 0:
            riesgo_promedio = 30.0
        else:
            riesgo_promedio = suma_riesgo / suma_pesos

        riesgo_total = (riesgo_promedio * 0.75) + (max_riesgo * 0.25)

        zonas_influyentes.sort(key=lambda z: z["riesgo"], reverse=True)

        return {
            "riesgo_zonas": round(max(0, min(100, riesgo_total)), 2),
            "riesgo_promedio": round(riesgo_promedio, 2),
            "max_riesgo": round(max_riesgo, 2),
            "zonas_influyentes": zonas_influyentes[:8],
        }

    def calcular_bono_puntos_seguridad(
        self,
        route_points: list[dict],
        puntos_seguridad: list[PuntoSeguro],
        radio_influencia_m: float = RADIO_PUNTO_SEGURO_M,
    ) -> dict:
        puntos_cercanos = []

        for punto in puntos_seguridad:
            punto_dict = {
                "lat": punto.lat,
                "lon": punto.lon,
            }

            distancia = distance_point_to_route_m(punto_dict, route_points)

            if distancia <= radio_influencia_m:
                factor_cercania = 1 - (distancia / radio_influencia_m)
                factor_confianza = max(0.3, punto.nivel_confianza / 100)

                bono = punto.peso_seguridad * factor_cercania * factor_confianza

                if punto.validado_c5:
                    bono *= 1.25

                puntos_cercanos.append(
                    {
                        "id_punto_seguridad": punto.id_punto_seguridad,
                        "nombre": punto.nombre,
                        "marca": punto.marca,
                        "tipo_punto": punto.tipo_punto,
                        "distancia_m": round(distancia, 2),
                        "peso_seguridad": punto.peso_seguridad,
                        "nivel_confianza": punto.nivel_confianza,
                        "validado_c5": punto.validado_c5,
                        "bono": round(bono, 2),
                    }
                )

        puntos_cercanos.sort(key=lambda p: p["bono"], reverse=True)

        # Solo los 5 puntos más relevantes deben impactar el score.
        # Esto evita que una ruta larga se vuelva "súper segura"
        # solo porque cruza muchos OXXO/Farmacias.
        puntos_para_bono = puntos_cercanos[:5]

        bono_total = sum(p["bono"] for p in puntos_para_bono)
        bono_limitado = min(self.BONO_MAX_PUNTOS_SEGUROS, bono_total)

        return {
            "bono_puntos_seguridad": round(bono_limitado, 2),
            "bono_puntos_seguridad_sin_limite": round(bono_total, 2),
            "puntos_seguridad_cercanos": puntos_cercanos[:10],
        }

    def evaluar_ruta(
        self,
        route_points: list[dict],
        zonas: list[ZonaRiesgo],
        puntos_seguridad: list[PuntoSeguro],
        distancia_directa_m: float,
    ) -> dict:
        distancia = route_distance_m(route_points)

        riesgo = self.calcular_riesgo_zonas(route_points, zonas)
        seguridad = self.calcular_bono_puntos_seguridad(route_points, puntos_seguridad)

        riesgo_ajustado = riesgo["riesgo_zonas"] - seguridad["bono_puntos_seguridad"]
        riesgo_ajustado = max(0, min(100, riesgo_ajustado))

        penalizacion_distancia = 0.0

        if distancia_directa_m > 0:
            exceso_distancia = max(0, (distancia / distancia_directa_m) - 1)
            penalizacion_distancia = exceso_distancia * 25

        score_final = riesgo_ajustado + penalizacion_distancia

        return {
            "distancia_m": round(distancia, 2),
            "riesgo_zonas": riesgo["riesgo_zonas"],
            "bono_puntos_seguridad": seguridad["bono_puntos_seguridad"],
            "riesgo_ajustado": round(riesgo_ajustado, 2),
            "penalizacion_distancia": round(penalizacion_distancia, 2),
            "score_final": round(score_final, 2),
            "zonas_influyentes": riesgo["zonas_influyentes"],
            "puntos_seguridad_cercanos": seguridad["puntos_seguridad_cercanos"],
        }

    def generar_candidatas_ruta_segura(
        self,
        origen: dict,
        destino: dict,
        zonas: list[ZonaRiesgo],
        puntos_seguridad: list[PuntoSeguro],
    ) -> list[dict]:
        candidatas = []

        candidatas.append({
            "nombre": "ruta_directa",
            "tipo": "directa",
            "points": [origen, destino],
        })

        mid = midpoint(origen, destino)

        offsets = [
            ("desvio_norte_500m", 500, 0),
            ("desvio_sur_500m", -500, 0),
            ("desvio_este_500m", 0, 500),
            ("desvio_oeste_500m", 0, -500),
            ("desvio_noreste_700m", 500, 500),
            ("desvio_noroeste_700m", 500, -500),
            ("desvio_sureste_700m", -500, 500),
            ("desvio_suroeste_700m", -500, -500),
        ]

        for nombre, north_m, east_m in offsets:
            waypoint = offset_point_m(mid["lat"], mid["lon"], north_m=north_m, east_m=east_m)
            candidatas.append({
                "nombre": nombre,
                "tipo": "desvio_geografico",
                "points": [origen, waypoint, destino],
            })

        # Candidatas que pasan por zonas de menor riesgo
        zonas_seguras_cercanas = []

        for zona in zonas:
            if zona.riesgo <= 40:
                distancia_mid = haversine_m(mid["lat"], mid["lon"], zona.lat, zona.lon)

                if distancia_mid <= 2500:
                    zonas_seguras_cercanas.append((distancia_mid, zona))

        zonas_seguras_cercanas.sort(key=lambda item: item[0])

        for _, zona in zonas_seguras_cercanas[:5]:
            waypoint = {
                "lat": zona.lat,
                "lon": zona.lon,
            }

            candidatas.append({
                "nombre": f"desvio_zona_segura_{zona.id_zona}",
                "tipo": "desvio_por_zona_segura",
                "points": [origen, waypoint, destino],
                "zona_apoyo": {
                    "id_zona": zona.id_zona,
                    "nombre": zona.nombre,
                    "riesgo": zona.riesgo,
                },
            })

        # Candidatas que pasan cerca de puntos seguros reales
        puntos_candidatos = []

        ruta_directa = [origen, destino]

        for punto in puntos_seguridad:
            punto_dict = {
                "lat": punto.lat,
                "lon": punto.lon,
            }

            distancia_a_ruta = distance_point_to_route_m(punto_dict, ruta_directa)
            distancia_mid = haversine_m(mid["lat"], mid["lon"], punto.lat, punto.lon)

            if distancia_a_ruta <= 900 or distancia_mid <= 1800:
                prioridad = distancia_a_ruta - (punto.peso_seguridad * 12)
                puntos_candidatos.append((prioridad, punto))

        puntos_candidatos.sort(key=lambda item: item[0])

        for _, punto in puntos_candidatos[:8]:
            waypoint = {
                "lat": punto.lat,
                "lon": punto.lon,
            }

            candidatas.append({
                "nombre": f"desvio_punto_seguro_{punto.id_punto_seguridad}",
                "tipo": "desvio_por_punto_seguro",
                "points": [origen, waypoint, destino],
                "punto_seguridad_apoyo": {
                    "id_punto_seguridad": punto.id_punto_seguridad,
                    "nombre": punto.nombre,
                    "marca": punto.marca,
                    "tipo_punto": punto.tipo_punto,
                    "peso_seguridad": punto.peso_seguridad,
                },
            })

        return candidatas

    def calcular_ruta_segura_turista(
        self,
        origen: dict,
        destino: dict,
        guardar: bool = True,
    ) -> dict:
        zonas = self.obtener_zonas_con_centro()
        puntos_seguridad = self.obtener_puntos_seguridad_activos()

        candidatas = self.generar_candidatas_ruta_segura(
            origen=origen,
            destino=destino,
            zonas=zonas,
            puntos_seguridad=puntos_seguridad,
        )

        distancia_directa = route_distance_m([origen, destino])

        evaluadas = []

        for candidata in candidatas:
            evaluacion = self.evaluar_ruta(
                route_points=candidata["points"],
                zonas=zonas,
                puntos_seguridad=puntos_seguridad,
                distancia_directa_m=distancia_directa,
            )

            evaluadas.append({
                **candidata,
                **evaluacion,
            })

        evaluadas.sort(key=lambda item: item["score_final"])

        mejor = evaluadas[0]
        explicacion = self.generar_explicacion_ruta(mejor)

        id_ruta = None

        if guardar:
            id_ruta = self.guardar_ruta_calculada(
                tipo_ruta="ruta_segura_turista",
                origen=origen,
                destino=destino,
                points=mejor["points"],
                score_riesgo=mejor["riesgo_ajustado"],
                distancia_m=mejor["distancia_m"],
                algoritmo=self.ALGORITMO_RUTA_SEGURA,
                parametros={
                    "ruta_elegida": mejor["nombre"],
                    "tipo": mejor["tipo"],
                    "riesgo_zonas": mejor["riesgo_zonas"],
                    "bono_puntos_seguridad": mejor["bono_puntos_seguridad"],
                    "riesgo_ajustado": mejor["riesgo_ajustado"],
                    "score_final": mejor["score_final"],
                    "explicacion": explicacion,
                    "zonas_influyentes": mejor["zonas_influyentes"],
                    "puntos_seguridad_cercanos": mejor["puntos_seguridad_cercanos"],
                },
            )

        geojson = {
            "type": "FeatureCollection",
            "features": [
                route_to_geojson_feature(
                    mejor["points"],
                    {
                        "id_ruta": id_ruta,
                        "tipo_ruta": "ruta_segura_turista",
                        "ruta_elegida": mejor["nombre"],
                        "score_final": mejor["score_final"],
                        "riesgo_zonas": mejor["riesgo_zonas"],
                        "bono_puntos_seguridad": mejor["bono_puntos_seguridad"],
                        "riesgo_ajustado": mejor["riesgo_ajustado"],
                        "distancia_m": mejor["distancia_m"],
                    },
                ),
                point_to_geojson_feature(origen, {"tipo": "origen"}),
                point_to_geojson_feature(destino, {"tipo": "destino"}),
            ],
        }

        return {
            "id_ruta": id_ruta,
            "tipo_ruta": "ruta_segura_turista",
            "algoritmo": self.ALGORITMO_RUTA_SEGURA,
            "ruta_elegida": mejor["nombre"],
            "score_final": mejor["score_final"],
            "riesgo_zonas": mejor["riesgo_zonas"],
            "bono_puntos_seguridad": mejor["bono_puntos_seguridad"],
            "riesgo_ajustado": mejor["riesgo_ajustado"],
            "distancia_m": mejor["distancia_m"],
            "duracion_estimada_min": round(mejor["distancia_m"] / 80, 1),
            "explicacion": explicacion,
            "zonas_influyentes": mejor["zonas_influyentes"],
            "puntos_seguridad_cercanos": mejor["puntos_seguridad_cercanos"],
            "candidatas": [
                {
                    "nombre": item["nombre"],
                    "tipo": item["tipo"],
                    "distancia_m": item["distancia_m"],
                    "riesgo_zonas": item["riesgo_zonas"],
                    "bono_puntos_seguridad": item["bono_puntos_seguridad"],
                    "riesgo_ajustado": item["riesgo_ajustado"],
                    "score_final": item["score_final"],
                }
                for item in evaluadas[:10]
            ],
            "geojson": geojson,
        }

    def generar_explicacion_ruta(self, ruta: dict) -> list[str]:
        explicacion = []

        explicacion.append("Se eligió la ruta con mejor balance entre riesgo, distancia y cercanía a puntos seguros.")
        explicacion.append(f"Riesgo de zonas estimado: {ruta['riesgo_zonas']}/100.")
        explicacion.append(f"Bono por puntos seguros cercanos: -{ruta['bono_puntos_seguridad']} puntos.")
        explicacion.append(f"Riesgo ajustado final: {ruta['riesgo_ajustado']}/100.")
        explicacion.append(f"Distancia aproximada: {ruta['distancia_m']} metros.")

        puntos = ruta.get("puntos_seguridad_cercanos") or []

        if puntos:
            principal = puntos[0]
            explicacion.append(
                f"La ruta pasa cerca de {principal['nombre']} ({principal['marca']}), "
                f"a {principal['distancia_m']} metros."
            )
        else:
            explicacion.append("No se detectaron puntos seguros cercanos a la ruta elegida.")

        zonas = ruta.get("zonas_influyentes") or []

        if zonas:
            zona_mayor = zonas[0]
            explicacion.append(
                f"La zona de mayor influencia fue {zona_mayor['nombre']} con riesgo {zona_mayor['riesgo']}."
            )

        if ruta["tipo"] == "desvio_por_punto_seguro":
            punto_apoyo = ruta.get("punto_seguridad_apoyo")
            if punto_apoyo:
                explicacion.append(
                    f"La ruta fue desviada para acercarse a un punto seguro: {punto_apoyo['nombre']}."
                )

        if ruta["tipo"] == "desvio_por_zona_segura":
            zona_apoyo = ruta.get("zona_apoyo")
            if zona_apoyo:
                explicacion.append(
                    f"La ruta se apoyó en una zona de menor riesgo: {zona_apoyo['nombre']}."
                )

        return explicacion

    def guardar_ruta_calculada(
        self,
        tipo_ruta: str,
        origen: dict,
        destino: dict | None,
        points: list[dict],
        score_riesgo: float,
        distancia_m: float,
        algoritmo: str,
        parametros: dict,
    ) -> int:
        ruta = RutaCalculada(
            tipo_ruta=tipo_ruta,
            origen=point_wkt(origen["lon"], origen["lat"]),
            destino=point_wkt(destino["lon"], destino["lat"]) if destino else None,
            score_riesgo=score_riesgo,
            score_confianza=75,
            distancia_m=distancia_m,
            duracion_estimada_seg=distancia_m / 1.3,
            algoritmo=algoritmo,
            parametros=parametros,
            geom=linestring_wkt(points),
        )

        self.db.add(ruta)
        self.db.flush()

        for index, point in enumerate(points):
            self.db.add(
                RutaPuntoControl(
                    id_ruta=ruta.id_ruta,
                    orden=index + 1,
                    tipo_punto="origen" if index == 0 else "destino" if index == len(points) - 1 else "waypoint",
                    descripcion=f"Punto {index + 1} de la ruta calculada.",
                    ubicacion=point_wkt(point["lon"], point["lat"]),
                )
            )

        self.db.commit()

        return ruta.id_ruta

    def calcular_rutas_probables_desplazamiento(
        self,
        origen: dict,
        radio_m: int = 500,
        guardar: bool = True,
    ) -> dict:
        zonas = self.obtener_zonas_con_centro()

        direcciones = [
            ("norte", radio_m, 0),
            ("sur", -radio_m, 0),
            ("este", 0, radio_m),
            ("oeste", 0, -radio_m),
            ("noreste", radio_m, radio_m),
            ("noroeste", radio_m, -radio_m),
            ("sureste", -radio_m, radio_m),
            ("suroeste", -radio_m, -radio_m),
        ]

        candidatas = []

        for nombre, north_m, east_m in direcciones:
            destino = offset_point_m(origen["lat"], origen["lon"], north_m=north_m, east_m=east_m)
            points = [origen, destino]
            distancia = route_distance_m(points)

            riesgo = self.calcular_riesgo_zonas(points, zonas)

            # En esta v1, menor riesgo = ruta de seguimiento más segura para operador/turista.
            # Después para sospechoso podemos cambiarlo a baja cobertura de cámaras / baja seguridad.
            probabilidad_operativa = max(5, 100 - riesgo["riesgo_zonas"])

            candidatas.append({
                "direccion": nombre,
                "points": points,
                "destino_estimado": destino,
                "distancia_m": round(distancia, 2),
                "riesgo_zonas": riesgo["riesgo_zonas"],
                "probabilidad_operativa": round(probabilidad_operativa, 2),
                "zonas_influyentes": riesgo["zonas_influyentes"],
            })

        candidatas.sort(key=lambda item: item["probabilidad_operativa"], reverse=True)

        mejor = candidatas[0]

        id_ruta = None

        if guardar:
            id_ruta = self.guardar_ruta_calculada(
                tipo_ruta="ruta_probable_desplazamiento",
                origen=origen,
                destino=mejor["destino_estimado"],
                points=mejor["points"],
                score_riesgo=mejor["riesgo_zonas"],
                distancia_m=mejor["distancia_m"],
                algoritmo=self.ALGORITMO_RUTA_PROBABLE,
                parametros={
                    "direccion_probable": mejor["direccion"],
                    "probabilidad_operativa": mejor["probabilidad_operativa"],
                    "radio_m": radio_m,
                    "candidatas": [
                        {
                            "direccion": c["direccion"],
                            "probabilidad_operativa": c["probabilidad_operativa"],
                            "riesgo_zonas": c["riesgo_zonas"],
                        }
                        for c in candidatas
                    ],
                },
            )

        geojson = {
            "type": "FeatureCollection",
            "features": [
                route_to_geojson_feature(
                    mejor["points"],
                    {
                        "id_ruta": id_ruta,
                        "tipo_ruta": "ruta_probable_desplazamiento",
                        "direccion": mejor["direccion"],
                        "probabilidad_operativa": mejor["probabilidad_operativa"],
                        "riesgo_zonas": mejor["riesgo_zonas"],
                    },
                ),
                point_to_geojson_feature(origen, {"tipo": "deteccion_origen"}),
            ],
        }

        return {
            "id_ruta": id_ruta,
            "tipo_ruta": "ruta_probable_desplazamiento",
            "algoritmo": self.ALGORITMO_RUTA_PROBABLE,
            "direccion_probable": mejor["direccion"],
            "probabilidad_operativa": mejor["probabilidad_operativa"],
            "riesgo_zonas": mejor["riesgo_zonas"],
            "distancia_m": mejor["distancia_m"],
            "candidatas": [
                {
                    "direccion": item["direccion"],
                    "probabilidad_operativa": item["probabilidad_operativa"],
                    "riesgo_zonas": item["riesgo_zonas"],
                    "distancia_m": item["distancia_m"],
                    "destino_estimado": item["destino_estimado"],
                }
                for item in candidatas
            ],
            "geojson": geojson,
        }