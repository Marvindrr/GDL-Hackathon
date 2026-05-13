from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class Camara(Base):
    __tablename__ = "camaras"

    id_camara: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    id_municipio: Mapped[int | None] = mapped_column(ForeignKey("municipios.id_municipio"), nullable=True)
    id_zona: Mapped[int | None] = mapped_column(ForeignKey("zonas.id_zona"), nullable=True)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo_externo: Mapped[str | None] = mapped_column(String(100), nullable=True)

    tipo: Mapped[str] = mapped_column(String(50), nullable=False, default="fija")
    fuente: Mapped[str] = mapped_column(String(80), nullable=False, default="simulada")

    lat = mapped_column(Numeric(10, 7), nullable=False)
    lon = mapped_column(Numeric(10, 7), nullable=False)
    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)

    direccion_texto: Mapped[str | None] = mapped_column(Text, nullable=True)
    activa = mapped_column(Boolean, default=True, nullable=False)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    municipio = relationship("Municipio", back_populates="camaras")
    zona = relationship("Zona", back_populates="camaras")
    streams = relationship("CamaraStream", back_populates="camara")
    estados = relationship("CamaraEstado", back_populates="camara")
    coberturas = relationship("CamaraCobertura", back_populates="camara")
    detecciones = relationship("DeteccionCamara", back_populates="camara")
    observaciones = relationship("TrackObservacion", back_populates="camara")


class CamaraStream(Base):
    __tablename__ = "camara_streams"

    id_stream: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_camara: Mapped[int] = mapped_column(ForeignKey("camaras.id_camara"), nullable=False)

    url_stream: Mapped[str] = mapped_column(Text, nullable=False)
    protocolo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    usuario: Mapped[str | None] = mapped_column(String(120), nullable=True)
    password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

    activo = mapped_column(Boolean, default=True, nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    camara = relationship("Camara", back_populates="streams")


class CamaraEstado(Base):
    __tablename__ = "camara_estados"

    id_estado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_camara: Mapped[int] = mapped_column(ForeignKey("camaras.id_camara"), nullable=False)

    estado: Mapped[str] = mapped_column(String(50), nullable=False)
    fps_actual = mapped_column(Numeric(8, 2), nullable=True)
    latencia_ms = mapped_column(Numeric(10, 2), nullable=True)
    mensaje_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    fecha_estado = mapped_column(DateTime, server_default=func.now(), nullable=False)

    camara = relationship("Camara", back_populates="estados")


class CamaraCobertura(Base):
    __tablename__ = "camara_cobertura"

    id_cobertura: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_camara: Mapped[int] = mapped_column(ForeignKey("camaras.id_camara"), nullable=False)

    angulo = mapped_column(Numeric(8, 2), nullable=True)
    distancia_m = mapped_column(Numeric(10, 2), nullable=True)
    geom = mapped_column(Geometry("POLYGON", srid=4326, spatial_index=False), nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    camara = relationship("Camara", back_populates="coberturas")