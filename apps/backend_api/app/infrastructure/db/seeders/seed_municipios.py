from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import Municipio


MUNICIPIOS_INICIALES = [
    "Guadalajara",
    "Zapopan",
    "San Pedro Tlaquepaque",
    "Tonalá",
    "Tlajomulco de Zúñiga",
    "El Salto",
    "Acatlán de Juárez",
    "Tequila",
]


def seed_municipios():
    db = SessionLocal()

    try:
        for nombre in MUNICIPIOS_INICIALES:
            existente = (
                db.query(Municipio)
                .filter(Municipio.nombre == nombre)
                .first()
            )

            if not existente:
                db.add(Municipio(nombre=nombre, estado="Jalisco"))

        db.commit()
        print("Seed municipios completado.")
    except Exception as e:
        db.rollback()
        print(f"Error en seed_municipios: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_municipios()