from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class PuntoSeguridad(Base):
    __tablename__ = "puntos_seguridad"

    id_punto_seguridad: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    id_fuente: Mapped[int | None] = mapped_column(
        ForeignKey("fuentes_datos.id_fuente"),
        nullable=True,
    )

    id_municipio: Mapped[int | None] = mapped_column(
        ForeignKey("municipios.id_municipio"),
        nullable=True,
    )

    id_zona: Mapped[int | None] = mapped_column(
        ForeignKey("zonas.id_zona"),
        nullable=True,
    )

    id_externo: Mapped[str | None] = mapped_column(String(120), nullable=True)

    nombre: Mapped[str] = mapped_column(String(220), nullable=False)
    marca: Mapped[str | None] = mapped_column(String(120), nullable=True)

    tipo_punto: Mapped[str] = mapped_column(String(80), nullable=False)

    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    colonia: Mapped[str | None] = mapped_column(String(180), nullable=True)
    codigo_postal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sitio_web: Mapped[str | None] = mapped_column(Text, nullable=True)

    horario: Mapped[str | None] = mapped_column(Text, nullable=True)
    es_24h = mapped_column(Boolean, default=False, nullable=False)

    lat = mapped_column(Numeric(10, 7), nullable=False)
    lon = mapped_column(Numeric(10, 7), nullable=False)

    ubicacion = mapped_column(
        Geometry("POINT", srid=4326, spatial_index=False),
        nullable=False,
    )

    validado_c5 = mapped_column(Boolean, default=False, nullable=False)
    activo = mapped_column(Boolean, default=True, nullable=False)

    nivel_confianza = mapped_column(Numeric(5, 2), default=60, nullable=False)
    peso_seguridad = mapped_column(Numeric(5, 2), default=10, nullable=False)

    extra_metadata = mapped_column("metadata", JSONB, nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "id_fuente",
            "id_externo",
            name="uq_puntos_seguridad_fuente_externo",
        ),
    )