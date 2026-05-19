from app.infrastructure.db.seeders.seed_fuentes import seed_fuentes
from app.infrastructure.db.seeders.seed_modelos_ia import seed_modelos_ia
from app.infrastructure.db.seeders.seed_municipios import seed_municipios
from app.infrastructure.db.seeders.seed_zonas_colonias_from_json import seed_zonas_colonias
from app.infrastructure.db.seeders.seed_zonas_turisticas_from_json import seed_zonas_turisticas
from app.infrastructure.db.seeders.seed_puntos_turisticos_from_json import seed_puntos_turisticos


def seed_all():
    print("Iniciando seeds...")

    seed_fuentes()
    seed_modelos_ia()
    seed_municipios()
    seed_zonas_colonias()
    seed_zonas_turisticas()
    seed_puntos_turisticos()

    print("Seeds completadas.")


if __name__ == "__main__":
    seed_all()