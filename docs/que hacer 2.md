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