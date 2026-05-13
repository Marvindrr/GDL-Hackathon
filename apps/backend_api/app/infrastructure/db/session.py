import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://segury:segury123@localhost:5432/segurytech"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("SQLALCHEMY_ECHO", "0") == "1",
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Este código configura la conexión a la base de datos utilizando SQLAlchemy. 
#Define una función `get_db_session` que se puede usar como dependencia en 
#FastAPI para obtener una sesión de base de datos. La conexión se establece 
#utilizando una URL de base de datos que se puede configurar a través de variables de entorno.