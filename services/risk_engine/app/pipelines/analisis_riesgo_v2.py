import pandas as pd
import numpy as np
import folium
import webbrowser
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from sklearn.linear_model import LogisticRegression

# ==============================
# Coordenadas de GDL                 UAAAAAAAAA!!!!!!
# ==============================

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
    "La Penal": (20.6763, -103.3002)
}

# ==============================
# Datos de riesgo simulados
# ==============================

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
    "La Penal": 85
}

# DataFrame
data = pd.DataFrame(list(datos_riesgo.items()), columns=['Zona', 'Riesgo'])

X = data['Riesgo'].values.reshape(-1, 1).astype(np.float32)
y = (data['Riesgo'].values > 50).astype(int)

if len(np.unique(y)) < 2:
    raise ValueError("No hay suficientes clases.")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Red neuronal
modelo = Sequential()
modelo.add(Dense(10, input_dim=1, activation='relu'))
modelo.add(Dense(1))

modelo.compile(loss='mean_squared_error', optimizer='adam')

modelo.fit(X_train, y_train, epochs=50, verbose=0)

y_pred = modelo.predict(X_test)

if len(y_test) > 0:
    mse = mean_squared_error(y_test, y_pred)
    print(f'MSE: {mse:.2f}')

# Logistica de Regresion 
modelo_logistico = LogisticRegression()
modelo_logistico.fit(X_train, y_train)

probabilidades = modelo_logistico.predict_proba(X_test)[:, 1]

print("\nProbabilidad de riesgo:")
for zona, prob in zip(data['Zona'].iloc[X_test.flatten().argsort()], np.sort(probabilidades)):
    print(f'{zona}: {prob:.2f}')

# MAPA GDL
mapa = folium.Map(location=[20.6767, -103.3475], zoom_start=13)

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
    ).add_to(mapa)

# Guardar mapa
mapa.save('mapa_gdl.html')

webbrowser.open('mapa_gdl.html')