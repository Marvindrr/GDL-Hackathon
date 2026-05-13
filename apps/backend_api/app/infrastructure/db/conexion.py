import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "segurytech"),
        user=os.getenv("POSTGRES_USER", "segury"),
        password=os.getenv("POSTGRES_PASSWORD", "segury123"),
        cursor_factory=RealDictCursor,
    )