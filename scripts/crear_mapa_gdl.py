from pathlib import Path
import osmnx as ox


OUTPUT_PATH = Path("/workspace/data/geo/map.graphml")

# Centro aproximado de Guadalajara.
CENTRO_GDL = (20.6767, -103.3467)

# 30 km cubren Guadalajara, Zapopan, Tlaquepaque, Tonalá y alrededores.
DISTANCIA_M = 30000

print("Descargando red vial de Guadalajara desde OpenStreetMap...")
print(f"Centro: {CENTRO_GDL}")
print(f"Radio: {DISTANCIA_M} m")

# Para sospechoso a pie conviene 'walk', porque incluye más pasos peatonales.
# Si después quieremos rutas vehiculares de patrullas, creamos otro grafo con network_type='drive'.
G = ox.graph_from_point(
    CENTRO_GDL,
    dist=DISTANCIA_M,
    network_type="walk",
    simplify=True,
    retain_all=False,
    truncate_by_edge=True,
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

print("Guardando mapa vial en:", OUTPUT_PATH)
ox.save_graphml(G, OUTPUT_PATH)

nodes = list(G.nodes(data=True))
xs = [float(data["x"]) for _, data in nodes]
ys = [float(data["y"]) for _, data in nodes]

print("Mapa creado correctamente.")
print("Nodos:", len(G.nodes))
print("Edges:", len(G.edges))
print("Lat min/max:", min(ys), max(ys))
print("Lon min/max:", min(xs), max(xs))