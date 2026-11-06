# services/risk_engine/app/services/risk_probability_service.py

import numpy as np
from sklearn.linear_model import LogisticRegression


def entrenar_modelo_riesgo(datos_riesgo: dict[str, int]):
    """
    Entrena un modelo simple para calcular probabilidad de riesgo alto.
    """
    zonas = list(datos_riesgo.keys())
    valores_riesgo = np.array(list(datos_riesgo.values()), dtype=np.float32)

    x = valores_riesgo.reshape(-1, 1)
    y = (valores_riesgo > 50).astype(int)

    if len(np.unique(y)) < 2:
        raise ValueError("Se requieren ejemplos de riesgo alto y bajo para entrenar el modelo.")

    modelo = LogisticRegression()
    modelo.fit(x, y)

    probabilidades = modelo.predict_proba(x)[:, 1]

    return {
        zona: round(float(prob), 4)
        for zona, prob in zip(zonas, probabilidades)
    }