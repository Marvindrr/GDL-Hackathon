import pandas as pd
import numpy as np
import folium
import webbrowser
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from sklearn.linear_model import LogisticRegression

# Zonas representativas de Guadalajara y alrededores (lat, lon)
puntos_zonas = {
    "Centro": (20.6767, -103.3476),
    "Providencia": (20.7000, -103.3735),
    "Zapopan Centro": (20.7236, -103.3850),
    "Tlaquepaque Centro": (20.6407, -103.2931),
    "Chapalita": (20.6620, -103.3925),
    "Tonalá Centro": (20.6248, -103.2341),
    "Colonia Americana": (20.6733, -103.3631),
    "Oblatos": (20.6905, -103.2975),
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
}

# Puntos de escape / refugios sugeridos
puntos_escape = {
    "Unidad Deportiva Ávila Camacho": (20.7046, -103.3657),
    "Parque Alcalde": (20.6908, -103.3565),
    "Parque Revolución": (20.6775, -103.3471),
    "Parque Solidaridad": (20.6565, -103.2637),
    "Auditorio Benito Juárez": (20.7247, -103.3878),
}

# --- Preparación de datos ---
data = pd.DataFrame(list(datos_riesgo.items()), columns=["Zona", "Riesgo"])
X = data["Riesgo"].values.reshape(-1, 1).astype(np.float32)
y = (data["Riesgo"].values > 50).astype(int)  # 1 = alto riesgo

if len(np.unique(y)) < 2:
    raise ValueError("Se requieren ejemplos de ambas clases (alto y bajo riesgo).")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Modelo NN para aproximar riesgo ---
modelo = Sequential()
modelo.add(Dense(10, input_dim=1, activation="relu"))
modelo.add(Dense(1))
modelo.compile(loss="mean_squared_error", optimizer="adam")
modelo.fit(X_train, y_train, epochs=100, verbose=0)
y_pred = modelo.predict(X_test, verbose=0)
if len(y_test) > 0:
    mse = mean_squared_error(y_test, y_pred)
    print(f"Error cuadrático medio NN: {mse:.2f}")

# --- Regresión logística para probabilidad de riesgo alto ---
modelo_logistico = LogisticRegression()
modelo_logistico.fit(X_train, y_train)
probabilidades = modelo_logistico.predict_proba(X)[:, 1]
data["ProbRiesgoAlto"] = probabilidades

# --- Utilidades de geodistancia ---
def distancia_haversine(lat1, lon1, lat2, lon2):
    """Devuelve distancia aproximada en km."""
    R = 6371
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlambda / 2) ** 2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def escape_mas_cercano(coord):
    lat, lon = coord
    mejor = None
    mejor_dist = 1e9
    for nombre, (elat, elon) in puntos_escape.items():
        d = distancia_haversine(lat, lon, elat, elon)
        if d < mejor_dist:
            mejor_dist = d
            mejor = (nombre, (elat, elon), d)
    return mejor

# --- Mapa Folium ---
mapa = folium.Map(location=[20.6736, -103.3440], zoom_start=12)

# Marcadores de zonas con círculos para delimitar área y color por riesgo
for zona, coords in puntos_zonas.items():
    riesgo = datos_riesgo.get(zona, "Riesgo no encontrado")
    prob = float(data.loc[data["Zona"] == zona, "ProbRiesgoAlto"].values[0])

    if riesgo >= 60:
        color = "red"
        radius = 450
    elif 40 <= riesgo < 60:
        color = "orange"
        radius = 350
    else:
        color = "green"
        radius = 250

    folium.Circle(
        location=coords,
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.2,
        popup=f"{zona} - Riesgo: {riesgo} (Prob. alto: {prob:.2f})",
    ).add_to(mapa)

    # Ruta de escape recomendada solo si alto riesgo
    if riesgo >= 60:
        nombre_esc, coords_esc, dist_km = escape_mas_cercano(coords)
        folium.PolyLine(
            [coords, coords_esc],
            color="blue",
            weight=3,
            tooltip=f"Ruta de escape a {nombre_esc} (~{dist_km:.1f} km)",
        ).add_to(mapa)

# Marcadores de puntos de escape
for nombre, coords in puntos_escape.items():
    folium.Marker(
        location=coords,
        popup=f"{nombre} (escape)",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(mapa)

mapa.save("mapa_guadalajara.html")
webbrowser.open("mapa_guadalajara.html")
