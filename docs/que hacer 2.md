GDL-Hackathon/
│
├─ apps/
│  ├─ backend_api/
│  │  ├─ Dockerfile              # Nuevo
│  │  ├─ requirements.txt        # Nuevo o separado del requirements global
│  │  └─ app/
│  │     ├─ main.py              # Modificar
│  │     └─ infrastructure/db/
│  │        └─ conexion.py       # Modificar
│  │
│  ├─ frontend_legacy/           # Se queda igual por ahora
│  │
│  └─ frontend_web/
│     ├─ Dockerfile              # Nuevo
│     ├─ package.json            # Revisar si existe; si no, crear
│     ├─ index.html              # Revisar si existe; si no, crear
│     ├─ vite.config.ts          # Revisar si existe; si no, crear
│     └─ src/
│
├─ data/
├─ infra/
│  └─ nginx/
│     └─ default.conf            # Más adelante
│
├─ services/
│  ├─ risk_engine/
│  ├─ vision_engine/
│  └─ camaras_ingestion_service/
│
├─ .env                          # Nuevo
├─ .env.example                  # Nuevo recomendado
├─ .dockerignore                 # Nuevo
├─ docker-compose.yml            # Nuevo
├─ .gitignore                    # Modificar
└─ requirements.txt              # Puedes dejarlo, pero mejor dividirlo

Día 1:
- Crear tablas base en PostGIS.
- Cargar colonias y cámaras desde JSON.
- Consultar zona por lat/lon.
- Consultar cámaras cercanas.

Día 2:
- Crear risk_score_service.
- Calcular riesgo por zona.
- Guardar riesgo_total.
- Exponer endpoint desde backend_api.

Día 3:
- Crear eventos_seguridad y detecciones_camara.
- Simular detección YOLO.
- Crear evento de robo/persona sospechosa.
- Calcular cámaras cercanas siguientes.

Día 4:
- Crear primera ruta probable de desplazamiento.
- No con IA todavía, sino con distancia + cámaras + zona.

Día 5:
- Crear ruta segura turista.
- Primero por zonas y puntos turísticos.
- Luego con calles reales.