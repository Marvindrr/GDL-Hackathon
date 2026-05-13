def calcular_riesgo_zona(
    riesgo_base: float,
    reportes_score: float = 0,
    luz_score: float = 50,
    hora_score: float = 0,
    reputacion_score: float = 50,
    cobertura_camaras_score: float = 50,
) -> float:
    riesgo = (
        riesgo_base * 0.45
        + reportes_score * 0.25
        + (100 - luz_score) * 0.10
        + hora_score * 0.10
        + (100 - reputacion_score) * 0.05
        + (100 - cobertura_camaras_score) * 0.05
    )

    return round(max(0, min(100, riesgo)), 2) 

# Esto lo que hace es calcular el riesgo de una zona basándose en varios factores, 
# como el riesgo base, los reportes de incidentes, la iluminación, la hora del día, 
# la reputación de la zona y la cobertura de cámaras. Cada factor tiene un peso 
# específico en el cálculo del riesgo total. El resultado se redondea a dos decimales 
# y se asegura de que esté entre 0 y 100.
