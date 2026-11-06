from app.services.risk_score_service import calcular_riesgo_zona


def ejecutar_analisis():
    """
    Pipeline temporal:
    1. Lee zonas desde la base de datos.
    2. Calcula riesgo con fórmula heurística.
    3. Guarda riesgo_total.
    """
    pass