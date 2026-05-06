# RutaSegura GDL

Aplicacion web para visualizar zonas de riesgo en Guadalajara y calcular una ruta demo entre colonias o puntos turisticos.

## Flujo principal

El proyecto que funciona actualmente esta conectado asi:

1. `apps/backend_api/app/main.py` levanta Flask, sirve la pagina principal y expone los endpoints `/api/colonias` y `/api/ruta`.
2. `apps/frontend_web/templates/index.html` carga la interfaz, `static/css/styles.css` y `static/js/main.js`.
3. `apps/frontend_web/static/js/main.js` pinta el mapa con Leaflet/Turf, consulta `/api/colonias`, carga los JSON turisticos estaticos y pide el calculo de ruta a `/api/ruta`.
4. `apps/backend_api/app/applications/services/colonias_loader.py` lee `data/geo/colonias_jalisco.json`.
5. `apps/backend_api/app/applications/services/mapa_gdl.py` calcula distancia, tiempo estimado, riesgo y colonias criticas cercanas.

## Datos usados por la pantalla

- `data/geo/colonias_jalisco.json`
- `apps/frontend_web/static/data/puntos_turisticos_ruta.json`
- `apps/frontend_web/static/data/zonas_turisticas_normalizadas.json`

## Archivos no conectados al flujo actual

Estos archivos pueden servir como insumos futuros, pero la app principal no los usa hoy:

- `data/geo/COLONIAS.geojson`
- `data/geo/map.osm`
- `data/geo/ubicaciones.json`
- `examples/*`
- `docs/*`
- `services/*`
- `infra/scripts/cargar_zonas_bd.py`

## Ejecutar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m apps.backend_api.app.main
```

Despues abre `http://127.0.0.1:5000/`.
