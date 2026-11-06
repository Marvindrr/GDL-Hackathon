from pathlib import Path

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import Zona
from app.infrastructure.db.seeders.seed_helpers import (
    get_project_root,
    get_or_create_municipio,
    load_json_from_candidates,
    point_wkt,
    multipolygon_wkt_from_latlon,
)


def seed_zonas_turisticas():
    db = SessionLocal()
    root = get_project_root()

    frontend_legacy_dir = Path(
        str(root / "apps" / "frontend_legacy")
    )

    json_data = load_json_from_candidates([
        frontend_legacy_dir / "static" / "modules" / "gdl_turismo" / "data" / "gdl_zonas_turisticas_normalizadas.json",
        Path("/workspace/apps/frontend_legacy/static/modules/gdl_turismo/data/gdl_zonas_turisticas_normalizadas.json"),
    ])

    insertadas = 0
    actualizadas = 0

    try:
        for item in json_data:
            municipio_nombre = item.get("municipio")
            nombre_zona = item.get("nombre_zona")
            estado = item.get("estado", "Jalisco")
            tipo = item.get("tipo", "zona_turistica")
            riesgo = item.get("riesgo", 0)
            centro = item.get("centro") or {}
            poligono = item.get("poligono") or []

            lat = centro.get("lat")
            lon = centro.get("lon")

            if not municipio_nombre or not nombre_zona or lat is None or lon is None:
                continue

            municipio = get_or_create_municipio(db, municipio_nombre, estado)

            existente = (
                db.query(Zona)
                .filter(
                    Zona.id_municipio == municipio.id_municipio,
                    Zona.nombre == nombre_zona,
                    Zona.tipo == tipo,
                )
                .first()
            )

            geom = multipolygon_wkt_from_latlon(poligono)

            if existente:
                existente.riesgo_base = riesgo
                existente.reputacion_base = 50
                existente.nivel_luz_base = None
                existente.centro = point_wkt(lon, lat)
                existente.geom = geom
                actualizadas += 1
            else:
                db.add(Zona(
                    id_municipio=municipio.id_municipio,
                    nombre=nombre_zona,
                    tipo=tipo,
                    riesgo_base=riesgo,
                    reputacion_base=50,
                    nivel_luz_base=None,
                    centro=point_wkt(lon, lat),
                    geom=geom,
                ))
                insertadas += 1

        db.commit()
        print(f"Seed zonas turísticas completado. Insertadas: {insertadas}, actualizadas: {actualizadas}")
    except Exception as e:
        db.rollback()
        print(f"Error en seed_zonas_turisticas: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_zonas_turisticas()