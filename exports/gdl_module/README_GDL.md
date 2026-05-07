# Modulo Mapa GDL

Este paquete esta pensado para copiarse dentro de otro proyecto Flask sin mezclar nombres con el resto del codigo.

## 1. Copiar carpeta

Copia la carpeta completa:

```text
gdl_module/
```

al proyecto de tu amigo, de preferencia en la raiz del repo.

## 2. Registrar el mapa en Flask

En el archivo donde tu amigo crea su `app = Flask(__name__)`, agrega:

```python
from gdl_module import gdl_bp

app.register_blueprint(gdl_bp)
```

Con eso se crean estas rutas:

```text
/gdl
/api/gdl/colonias
/api/gdl/ruta
/gdl_static/...
```

## 3. Abrirlo desde un boton

En cualquier template HTML del otro proyecto:

```html
<a class="btn" href="{{ url_for('gdl.gdl_mapa') }}">Abrir mapa GDL</a>
```

Si no quieren usar `url_for`, tambien funciona:

```html
<a class="btn" href="/gdl">Abrir mapa GDL</a>
```

## 4. Dependencias

El backend solo necesita Flask:

```bash
pip install -r gdl_module/gdl_requirements.txt
```

La pagina carga Leaflet, Turf y Font Awesome por CDN.

## 5. Archivos incluidos

- `backend/gdl_routes.py`: Blueprint de Flask y endpoints.
- `backend/gdl_colonias_loader.py`: carga colonias desde JSON.
- `backend/gdl_mapa_service.py`: calcula ruta, distancia, tiempo, riesgo y colonias criticas.
- `templates/gdl_mapa.html`: pagina del mapa.
- `static/css/gdl_styles.css`: estilos del mapa.
- `static/js/gdl_main.js`: logica del mapa.
- `static/data/gdl_puntos_turisticos_ruta.json`: puntos turisticos.
- `static/data/gdl_zonas_turisticas_normalizadas.json`: zonas turisticas.
- `data/gdl_colonias_jalisco.json`: colonias y riesgos.

## 6. Prueba rapida

Despues de registrar el blueprint:

```bash
flask --app app run
```

Abre:

```text
http://127.0.0.1:5000/gdl
```
