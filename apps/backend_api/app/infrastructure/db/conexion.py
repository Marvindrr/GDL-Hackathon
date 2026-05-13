from app.infrastructure.db.session import SessionLocal


def obtener_conexion():
    """
    Compatibilidad temporal con código viejo.
    Lo ideal es migrar poco a poco a repositories usando SQLAlchemy.
    """
    return SessionLocal()