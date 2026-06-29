from pathlib import Path
import os
from math import asin, cos, radians, sin, sqrt

import networkx as nx
import osmnx as ox


class RoadRoutingService:
    """
    Calcula rutas sobre red vial real usando OpenStreetMap local.

    Usa primero:
    /workspace/data/geo/map.graphml

    Si no existe, construye el GraphML desde:
    /workspace/data/geo/map.osm
    """

    MAX_DISTANCIA_NODO_M = 1200

    def __init__(self):
        project_root = Path(os.getenv("PROJECT_ROOT", "/workspace"))

        self.geo_dir = project_root / "data" / "geo"
        self.graphml_path = self.geo_dir / "map.graphml"
        self.osm_path = self.geo_dir / "map.osm"

        self.graph = self._load_graph()

    def _load_graph(self):
        if self.graphml_path.exists() and self.graphml_path.stat().st_size > 0:
            return ox.load_graphml(self.graphml_path)

        if self.osm_path.exists() and self.osm_path.stat().st_size > 0:
            graph = ox.graph_from_xml(
                self.osm_path,
                simplify=True,
                retain_all=False,
            )

            self.graphml_path.parent.mkdir(parents=True, exist_ok=True)
            ox.save_graphml(graph, self.graphml_path)

            return graph

        raise RuntimeError(
            f"No se encontró mapa vial válido. "
            f"Se esperaba {self.graphml_path} o {self.osm_path}"
        )

    def calcular_ruta_vial(self, origen: dict, destino: dict) -> dict:
        try:
            nodo_origen = self._nearest_node(origen)
            nodo_destino = self._nearest_node(destino)

            ruta_nodos = nx.shortest_path(
                self.graph,
                nodo_origen,
                nodo_destino,
                weight="length",
            )

            coordenadas = self._extraer_coordenadas_ruta(ruta_nodos)
            distancia_m = self._calcular_distancia_ruta(ruta_nodos)

            if len(coordenadas) < 2:
                raise RuntimeError("La ruta vial calculada no tiene suficientes puntos.")

            return {
                "modo_ruteo": "red_vial_osm",
                "coordenadas": coordenadas,
                "distancia_m": round(distancia_m, 2),
                "nodos": len(ruta_nodos),
                "error": None,
            }

        except Exception as error:
            distancia_directa = self._haversine_m(
                origen["lat"],
                origen["lon"],
                destino["lat"],
                destino["lon"],
            )

            return {
                "modo_ruteo": "linea_directa_fallback",
                "coordenadas": [
                    {"lat": float(origen["lat"]), "lon": float(origen["lon"])},
                    {"lat": float(destino["lat"]), "lon": float(destino["lon"])},
                ],
                "distancia_m": round(distancia_directa, 2),
                "nodos": 2,
                "error": str(error),
            }

    def _nearest_node(self, punto: dict):
        nodo = ox.distance.nearest_nodes(
            self.graph,
            X=float(punto["lon"]),
            Y=float(punto["lat"]),
        )

        data = self.graph.nodes[nodo]

        distancia_m = self._haversine_m(
            float(punto["lat"]),
            float(punto["lon"]),
            float(data["y"]),
            float(data["x"]),
        )

        if distancia_m > self.MAX_DISTANCIA_NODO_M:
            raise RuntimeError(
                f"El punto {punto} está a {round(distancia_m, 2)} m "
                f"del nodo vial más cercano. Puede estar fuera del mapa."
            )

        return nodo

    def _extraer_coordenadas_ruta(self, ruta_nodos: list) -> list[dict]:
        coordenadas = []

        for nodo_a, nodo_b in zip(ruta_nodos[:-1], ruta_nodos[1:]):
            edge_data = self.graph.get_edge_data(nodo_a, nodo_b)

            if not edge_data:
                continue

            mejor_edge = min(
                edge_data.values(),
                key=lambda edge: float(edge.get("length", 0)),
            )

            geometry = mejor_edge.get("geometry")

            if geometry is not None:
                for lon, lat in geometry.coords:
                    punto = {
                        "lat": float(lat),
                        "lon": float(lon),
                    }

                    if not coordenadas or coordenadas[-1] != punto:
                        coordenadas.append(punto)
            else:
                data_a = self.graph.nodes[nodo_a]
                data_b = self.graph.nodes[nodo_b]

                puntos = [
                    {"lat": float(data_a["y"]), "lon": float(data_a["x"])},
                    {"lat": float(data_b["y"]), "lon": float(data_b["x"])},
                ]

                for punto in puntos:
                    if not coordenadas or coordenadas[-1] != punto:
                        coordenadas.append(punto)

        return coordenadas

    def _calcular_distancia_ruta(self, ruta_nodos: list) -> float:
        distancia = 0.0

        for nodo_a, nodo_b in zip(ruta_nodos[:-1], ruta_nodos[1:]):
            edge_data = self.graph.get_edge_data(nodo_a, nodo_b)

            if not edge_data:
                continue

            mejor_edge = min(
                edge_data.values(),
                key=lambda edge: float(edge.get("length", 0)),
            )

            distancia += float(mejor_edge.get("length", 0))

        return distancia

    @staticmethod
    def _haversine_m(lat1, lon1, lat2, lon2):
        radio_tierra_m = 6371000

        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        return radio_tierra_m * c