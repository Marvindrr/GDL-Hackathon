import os

from app.infrastructure.db.seeders.seed_fuentes import seed_fuentes
from app.infrastructure.db.seeders.seed_modelos_ia import seed_modelos_ia
from app.infrastructure.db.seeders.seed_municipios import seed_municipios
from app.infrastructure.db.seeders.seed_zonas_colonias_from_json import seed_zonas_colonias
from app.infrastructure.db.seeders.seed_zonas_turisticas_from_json import seed_zonas_turisticas
from app.infrastructure.db.seeders.seed_puntos_turisticos_from_json import seed_puntos_turisticos
from app.infrastructure.db.seeders.seed_puntos_seguridad_manual import seed_puntos_seguridad_manual
from app.infrastructure.db.seeders.seed_puntos_seguridad_denue import seed_puntos_seguridad_denue


def seed_all():
    print("Iniciando seeds...")

    seed_fuentes()
    seed_modelos_ia()
    seed_municipios()
    seed_zonas_colonias()
    seed_zonas_turisticas()
    seed_puntos_turisticos()
    seed_puntos_seguridad_manual()

    if os.getenv("RUN_DENUE_SEED", "0") == "1":
        seed_puntos_seguridad_denue()
    else:
        print("Seed DENUE omitido. Para correrlo usa RUN_DENUE_SEED=1.")

    print("Seeds completadas.")


if __name__ == "__main__":
    seed_all()