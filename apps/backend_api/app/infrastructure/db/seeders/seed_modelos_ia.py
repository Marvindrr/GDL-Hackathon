from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.ai_models import ModeloIA


MODELOS_IA_INICIALES = [
    {
        "nombre": "YOLO26_OBJECT_DETECTION",
        "version": "0.1.0",
        "tipo_modelo": "deteccion_objetos",
        "proveedor": "SeguryTech",
        "descripcion": "Modelo base para detectar personas, vehículos, motos y objetos relevantes.",
        "activo": True,
    },
    {
        "nombre": "YOLO26_MOVEMENT_DETECTION",
        "version": "0.1.0",
        "tipo_modelo": "deteccion_movimiento",
        "proveedor": "SeguryTech",
        "descripcion": "Modelo para detectar movimiento en zonas monitoreadas por cámaras.",
        "activo": True,
    },
    {
        "nombre": "YOLO26_AGGRESSIVE_MOVEMENT",
        "version": "0.1.0",
        "tipo_modelo": "comportamiento",
        "proveedor": "SeguryTech",
        "descripcion": "Modelo para detectar movimientos agresivos o comportamiento anómalo.",
        "activo": True,
    },
    {
        "nombre": "YOLO26_FIGHT_DETECTION",
        "version": "0.1.0",
        "tipo_modelo": "comportamiento",
        "proveedor": "SeguryTech",
        "descripcion": "Modelo para detectar posibles peleas entre personas.",
        "activo": True,
    },
    {
        "nombre": "YOLO26_POSSIBLE_ROBBERY",
        "version": "0.1.0",
        "tipo_modelo": "comportamiento",
        "proveedor": "SeguryTech",
        "descripcion": "Modelo para detectar señales visuales asociadas a un posible robo.",
        "activo": True,
    },
    {
        "nombre": "PERSON_TRACKING_V1",
        "version": "0.1.0",
        "tipo_modelo": "tracking",
        "proveedor": "SeguryTech",
        "descripcion": "Algoritmo para seguimiento de personas entre cámaras.",
        "activo": True,
    },
    {
        "nombre": "RISK_SCORE_HEURISTIC_V1",
        "version": "1.0.0",
        "tipo_modelo": "riesgo_heuristico",
        "proveedor": "SeguryTech",
        "descripcion": "Algoritmo inicial para calcular riesgo usando zona, reportes, hora, cámaras y comportamiento.",
        "activo": True,
    },
    {
        "nombre": "SAFE_ROUTE_HEURISTIC_V1",
        "version": "1.0.0",
        "tipo_modelo": "rutas",
        "proveedor": "SeguryTech",
        "descripcion": "Algoritmo inicial para rutas seguras turísticas.",
        "activo": True,
    },
    {
        "nombre": "SUSPECT_ROUTE_HEURISTIC_V1",
        "version": "1.0.0",
        "tipo_modelo": "rutas",
        "proveedor": "SeguryTech",
        "descripcion": "Algoritmo inicial para estimar ruta probable de desplazamiento.",
        "activo": True,
    },
]


def seed_modelos_ia():
    db = SessionLocal()

    try:
        for item in MODELOS_IA_INICIALES:
            existente = (
                db.query(ModeloIA)
                .filter(ModeloIA.nombre == item["nombre"])
                .first()
            )

            if existente:
                for key, value in item.items():
                    setattr(existente, key, value)
            else:
                db.add(ModeloIA(**item))

        db.commit()
        print("Seed modelos_ia completado.")
    except Exception as e:
        db.rollback()
        print(f"Error en seed_modelos_ia: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_modelos_ia()