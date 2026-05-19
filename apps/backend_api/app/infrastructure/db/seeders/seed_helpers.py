import json
import os
from pathlib import Path
from typing import Any

from geoalchemy2 import WKTElement

from app.infrastructure.db.models.geo_models import Municipio


def get_project_root() -> Path:
    """
    Dentro de Docker normalmente usaremos /workspace.
    Localmente intenta encontrar la raíz del proyecto.
    """
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root)

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "apps").exists() and (parent / "data").exists():
            return parent

    return Path.cwd()


def load_json_from_candidates(candidates: list[Path]) -> list[dict[str, Any]]:
    for path in candidates:
        if path.exists():
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)

    paths_text = "\n".join(str(p) for p in candidates)
    raise FileNotFoundError(f"No se encontró el JSON en estas rutas:\n{paths_text}")


def point_wkt(lon: float, lat: float):
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def multipolygon_wkt_from_latlon(points: list[list[float]]):
    """
    El JSON viene como [lat, lon].
    PostGIS/WKT necesita lon lat.
    """
    if not points or len(points) < 3:
        return None

    coords = [(float(lon), float(lat)) for lat, lon in points]

    if coords[0] != coords[-1]:
        coords.append(coords[0])

    ring = ", ".join(f"{lon} {lat}" for lon, lat in coords)

    return WKTElement(f"MULTIPOLYGON((({ring})))", srid=4326)


def get_or_create_municipio(db, nombre: str, estado: str = "Jalisco") -> Municipio:
    municipio = (
        db.query(Municipio)
        .filter(Municipio.nombre == nombre)
        .first()
    )

    if municipio:
        return municipio

    municipio = Municipio(
        nombre=nombre,
        estado=estado,
    )

    db.add(municipio)
    db.flush()

    return municipio