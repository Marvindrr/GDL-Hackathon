from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class FuenteDatos(Base):
    __tablename__ = "fuentes_datos"

    id_fuente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    tipo: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    activa = mapped_column(Boolean, default=True, nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    reportes = relationship("ReporteSeguridad", back_populates="fuente")
    factores_riesgo = relationship("FactorRiesgoZona", back_populates="fuente")


class ReporteSeguridad(Base):
    __tablename__ = "reportes_seguridad"

    id_reporte: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    id_zona: Mapped[int | None] = mapped_column(ForeignKey("zonas.id_zona"), nullable=True)
    id_fuente: Mapped[int | None] = mapped_column(ForeignKey("fuentes_datos.id_fuente"), nullable=True)

    tipo_reporte: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    severidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    lat = mapped_column(Numeric(10, 7), nullable=True)
    lon = mapped_column(Numeric(10, 7), nullable=True)
    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    validado = mapped_column(Boolean, default=False, nullable=False)

    fecha_reporte = mapped_column(DateTime, server_default=func.now(), nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    zona = relationship("Zona", back_populates="reportes")
    fuente = relationship("FuenteDatos", back_populates="reportes")