import pandas as pd
import numpy as np
import folium
import webbrowser
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from sklearn.linear_model import LogisticRegression

# Coordenadas de zonas representativas de Guadalajara y alrededores
puntos_zonas = {
    "Centro": (20.6767, -103.3467),
    "Providencia": (20.7000, -103.3735),
    "Zapopan Centro": (20.7236, -103.3850),
    "Tlaquepaque Centro": (20.6407, -103.2931),
    "Chapalita": (20.6620, -103.3925),
    "Tonalá Centro": (20.6248, -103.2341),
    "Colonia Americana": (20.6733, -103.3631),
    "Oblatos": (20.6920, -103.2980),
    "Analco": (20.6689, -103.3381),
    "Atlas": (20.6480, -103.3220),
    "Capilla de Jesus": (20.6820, -103.3580),
    "Del Fresno": (20.6580, -103.3620),
    "Del Sol": (20.6520, -103.3980),
    "El Sauz": (20.6220, -103.3920),
    "Huentitan el Bajo": (20.7320, -103.3250),
    "Independencia": (20.7080, -103.3350),
    "Jardines Alcalde": (20.7020, -103.3450),
    "Jardines de Guadalupe": (20.6750, -103.4050),
    "Jardines del Bosque": (20.6680, -103.3850),
    "Jardines de San Ignacio": (20.6620, -103.4020),
    "La Nogalera": (20.6280, -103.3450),
    "Lomas de Polanco": (20.6312, -103.3654),
    "Lomas del Valle": (20.6950, -103.4050),
    "Los Arcos": (20.6750, -103.3820),
    "Mezquitan Country": (20.6950, -103.3550),
    "Miravalle": (20.6120, -103.3450),
    "Moderna": (20.6650, -103.3580),
    "Monraz": (20.6820, -103.3950),
    "San Andres": (20.6650, -103.2920),
    "San Rafael": (20.6480, -103.3020),
    "Tetlan": (20.6620, -103.2780),
    "Zona Industrial": (20.6420, -103.3550),
}

# Índice de riesgo (0-100) por zona
datos_riesgo = {
    "Centro": 65,
    "Providencia": 35,
    "Zapopan Centro": 45,
    "Tlaquepaque Centro": 70,
    "Chapalita": 30,
    "Tonalá Centro": 60,
    "Colonia Americana": 55,
    "Oblatos": 75,
    "Analco": 62,
    "Atlas": 68,
    "Capilla de Jesus": 40,
    "Del Fresno": 58,
    "Del Sol": 28,
    "El Sauz": 72,
    "Huentitan el Bajo": 66,
    "Independencia": 64,
    "Jardines Alcalde": 42,
    "Jardines de Guadalupe": 25,
    "Jardines del Bosque": 27,
    "Jardines de San Ignacio": 22,
    "La Nogalera": 71,
    "Lomas de Polanco": 69,
    "Lomas del Valle": 20,
    "Los Arcos": 26,
    "Mezquitan Country": 33,
    "Miravalle": 73,
    "Moderna": 38,
    "Monraz": 24,
    "San Andres": 67,
    "San Rafael": 61,
    "Tetlan": 74,
    "Zona Industrial": 70,
}

# DataFrame de trabajo
data = pd.DataFrame(list(datos_riesgo.items()), columns=["Zona", "Riesgo"])

# Característica numérica y etiqueta binaria (alto riesgo > 50)
X = data["Riesgo"].values.reshape(-1, 1).astype(np.float32)
y = (data["Riesgo"].values > 50).astype(int)

# Verificar que haya al menos una muestra por clase
if len(np.unique(y)) < 2:
    raise ValueError("Se requieren ejemplos de ambas clases (alto y bajo riesgo).")

# Split entrenamiento/prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modelo de red neuronal para aproximar riesgo continuo
modelo = Sequential()
modelo.add(Dense(10, input_dim=1, activation="relu"))
modelo.add(Dense(1))
modelo.compile(loss="mean_squared_error", optimizer="adam")

modelo.fit(X_train, y_train, epochs=100, verbose=0)
y_pred = modelo.predict(X_test, verbose=0)

if len(y_test) > 0:
    mse = mean_squared_error(y_test, y_pred)
    print(f"Error cuadrático medio NN: {mse:.2f}")

# --- Regresión logística para clasificación alto/bajo ---
X_train_log, X_test_log, y_train_log, y_test_log = train_test_split(X, y, test_size=0.2, random_state=42)

modelo_logistico = LogisticRegression()
modelo_logistico.fit(X_train_log, y_train_log)

probabilidades = modelo_logistico.predict_proba(X_test_log)[:, 1]
for zona, prob in zip(data["Zona"].values[X_test_log.flatten().argsort()], np.sort(probabilidades)):
    print(f"Zona: {zona}, Probabilidad de riesgo alto: {prob:.2f}")

# --- Mapa Folium ---
mapa = folium.Map(location=[20.6736, -103.3440], zoom_start=12)

for zona, coords in puntos_zonas.items():
    riesgo = datos_riesgo.get(zona, "Riesgo no encontrado")
    if riesgo >= 60:
        color = "red"
    elif 40 <= riesgo < 60:
        color = "orange"
    else:
        color = "green"

    folium.Marker(
        location=coords,
        popup=f"{zona} - Riesgo: {riesgo}",
        icon=folium.Icon(color=color),
    ).add_to(mapa)

mapa.save("mapa_guadalajara.html")
webbrowser.open("mapa_guadalajara.html")
