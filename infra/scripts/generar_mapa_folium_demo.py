# infra/scripts/generar_mapa_folium_demo.py

import webbrowser

import folium

from apps.backend_api.app.data.mapa_demo_data import PUNTOS_ZONAS, DATOS_RIESGO, PUNTOS_ESCAPE
from apps.backend_api.app.services.mapa_service import obtener_color_y_radio_por_riesgo
from apps.backend_api.app.services.route_geo_utils import obtener_punto_escape_mas_cercano


def generar_mapa():
    mapa = folium.Map(location=[20.6736, -103.3440], zoom_start=12)

    for zona, coordenadas in PUNTOS_ZONAS.items():
        riesgo = DATOS_RIESGO.get(zona, 0)
        estilo = obtener_color_y_radio_por_riesgo(riesgo)

        folium.Circle(
            location=coordenadas,
            radius=estilo["radio"],
            color=estilo["color"],
            fill=True,
            fill_opacity=0.2,
            popup=f"{zona} - Riesgo: {riesgo}",
        ).add_to(mapa)

        if riesgo >= 60:
            escape = obtener_punto_escape_mas_cercano(
                coordenadas_origen=coordenadas,
                puntos_escape=PUNTOS_ESCAPE,
            )

            folium.PolyLine(
                [coordenadas, escape["coordenadas"]],
                color="blue",
                weight=3,
                tooltip=f"Ruta de escape a {escape['nombre']} (~{escape['distancia_km']} km)",
            ).add_to(mapa)

    for nombre, coordenadas in PUNTOS_ESCAPE.items():
        folium.Marker(
            location=coordenadas,
            popup=f"{nombre} (escape)",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(mapa)

    salida = "mapa_guadalajara.html"
    mapa.save(salida)
    webbrowser.open(salida)


if __name__ == "__main__":
    generar_mapa()