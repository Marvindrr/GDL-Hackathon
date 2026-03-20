import pandas as pd
import numpy as np
import folium
import webbrowser
from folium.plugins import MarkerCluster
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from sklearn.linear_model import LogisticRegression
from backend.database.conexion import obtener_conexion 

# ZONAS DE GUADALAJARA
puntos_zonas = {
    "Centro Guadalajara": (20.6767, -103.3475),
    "Americana": (20.6736, -103.3684),
    "Providencia": (20.6994, -103.3750),
    "Chapalita": (20.6589, -103.3956),
    "Oblatos": (20.6999, -103.2960),
    "Santa Tere": (20.6802, -103.3602),
    "Analco": (20.6670, -103.3406),
    "Polanco": (20.6520, -103.3143),
    "Miravalle": (20.6238, -103.3572),
    "La Penal": (20.6763, -103.3002),
    "Mezquitán": (20.6995, -103.3477),
    "Monraz": (20.7015, -103.3927),
    "Jardines del Bosque": (20.6557, -103.3844)
}

# PUNTOS DE SALIDA      (Salida a garden???)
puntos_esc = {
    "Plaza del Sol": (20.6505, -103.3913),
    "La Gran Plaza": (20.6730, -103.3950),
    "Parque Metropolitano": (20.6784, -103.4400),
    "Centro Médico": (20.6745, -103.3440)
}

# RIESGO
datos_riesgo = {
    "Centro Guadalajara": 75,
    "Americana": 45,
    "Providencia": 30,
    "Chapalita": 25,
    "Oblatos": 65,
    "Santa Tere": 55,
    "Analco": 70,
    "Polanco": 60,
    "Miravalle": 80,
    "La Penal": 85,
    "Mezquitán": 50,
    "Monraz": 20,
    "Jardines del Bosque": 35
}

# DATASET
data = pd.DataFrame(list(datos_riesgo.items()), columns=['Zona', 'Riesgo'])

X = data['Riesgo'].values.reshape(-1, 1)
y = np.random.rand(len(X)) * 100

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# RED NEURONAL
modelo = Sequential()
modelo.add(Dense(10, input_dim=1, activation='relu'))
modelo.add(Dense(1))

modelo.compile(loss='mean_squared_error', optimizer='adam')
modelo.fit(X_train, y_train, epochs=50, verbose=0)

y_pred = modelo.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
print(f'MSE: {mse:.2f}')

# LOGISTICA DE REGRESION

X_logistic = data['Riesgo'].values.reshape(-1, 1)
y_logistic = (data['Riesgo'].values > 50).astype(int)

modelo_logistico = LogisticRegression()
modelo_logistico.fit(X_logistic, y_logistic)

# MAPA GDL
mapa = folium.Map(location=[20.6767, -103.3475], zoom_start=13)

cluster = MarkerCluster().add_to(mapa)

for zona, coords in puntos_zonas.items():

    riesgo = datos_riesgo[zona]

    if riesgo >= 70:
        color = 'red'
    elif 40 <= riesgo < 70:
        color = 'orange'
    else:
        color = 'green'

    folium.Marker(
        location=coords,
        popup=f'{zona} - Riesgo: {riesgo}',
        icon=folium.Icon(color=color)
    ).add_to(cluster)

# PUNTOS DE SALIDA (AZUL)
for nombre, coords in puntos_esc.items():
    folium.Marker(
        location=coords,
        popup=f'Salida: {nombre}',
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(mapa)

# GUARDAR MAPA
nombre_archivo = 'mapa_gdl.html'
mapa.save(nombre_archivo)

webbrowser.open(nombre_archivo)