from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class ModeloIA(Base):
    __tablename__ = "modelos_ia"

    id_modelo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tipo_modelo: Mapped[str] = mapped_column(String(80), nullable=False)
    proveedor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    activo = mapped_column(Boolean, default=True, nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    ejecuciones = relationship("EjecucionModelo", back_populates="modelo")
    detecciones = relationship("DeteccionCamara", back_populates="modelo")
    comportamientos = relationship("ComportamientoDetectado", back_populates="modelo")


class EjecucionModelo(Base):
    __tablename__ = "ejecuciones_modelo"

    id_ejecucion: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_modelo: Mapped[int] = mapped_column(ForeignKey("modelos_ia.id_modelo"), nullable=False)

    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="finalizado")
    fecha_inicio = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_fin = mapped_column(DateTime, nullable=True)

    parametros = mapped_column(JSONB, nullable=True)
    metricas = mapped_column(JSONB, nullable=True)

    modelo = relationship("ModeloIA", back_populates="ejecuciones")


class DeteccionCamara(Base):
    __tablename__ = "detecciones_camara"

    id_deteccion: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_camara: Mapped[int] = mapped_column(ForeignKey("camaras.id_camara"), nullable=False)
    id_modelo: Mapped[int | None] = mapped_column(ForeignKey("modelos_ia.id_modelo"), nullable=True)
    id_evento: Mapped[int | None] = mapped_column(ForeignKey("eventos_seguridad.id_evento"), nullable=True)

    clase_detectada: Mapped[str] = mapped_column(String(80), nullable=False)
    confianza = mapped_column(Numeric(6, 4), nullable=True)
    tracking_id_externo: Mapped[str | None] = mapped_column(String(120), nullable=True)

    bbox = mapped_column(JSONB, nullable=True)
    keypoints = mapped_column(JSONB, nullable=True)
    extra_metadata = mapped_column("metadata", JSONB, nullable=True)

    fecha_deteccion = mapped_column(DateTime, server_default=func.now(), nullable=False)

    lat = mapped_column(Numeric(10, 7), nullable=True)
    lon = mapped_column(Numeric(10, 7), nullable=True)
    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    camara = relationship("Camara", back_populates="detecciones")
    modelo = relationship("ModeloIA", back_populates="detecciones")
    evento = relationship("EventoSeguridad", back_populates="detecciones")
    evento_links = relationship("EventoDeteccion", back_populates="deteccion")
    evidencias = relationship("EvidenciaMedia", back_populates="deteccion")
    comportamientos = relationship("ComportamientoDetectado", back_populates="deteccion")
    observaciones = relationship("TrackObservacion", back_populates="deteccion")


class TrackObjeto(Base):
    __tablename__ = "track_objetos"

    id_track: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    tracking_id: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    tipo_objeto: Mapped[str] = mapped_column(String(80), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="activo")

    confianza_global = mapped_column(Numeric(6, 4), nullable=True)

    fecha_inicio = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_fin = mapped_column(DateTime, nullable=True)

    ultima_ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    observaciones = relationship("TrackObservacion", back_populates="track")
    eventos = relationship("EventoSeguridad", back_populates="track")
    rutas = relationship("RutaCalculada", back_populates="track")


class TrackObservacion(Base):
    __tablename__ = "track_observaciones"

    id_observacion: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_track: Mapped[int] = mapped_column(ForeignKey("track_objetos.id_track"), nullable=False)
    id_deteccion: Mapped[int | None] = mapped_column(ForeignKey("detecciones_camara.id_deteccion"), nullable=True)
    id_camara: Mapped[int | None] = mapped_column(ForeignKey("camaras.id_camara"), nullable=True)

    fecha_observacion = mapped_column(DateTime, server_default=func.now(), nullable=False)

    lat = mapped_column(Numeric(10, 7), nullable=True)
    lon = mapped_column(Numeric(10, 7), nullable=True)
    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    velocidad_estimada_m_s = mapped_column(Numeric(10, 4), nullable=True)
    direccion_grados = mapped_column(Numeric(8, 2), nullable=True)

    extra_metadata = mapped_column("metadata", JSONB, nullable=True)

    track = relationship("TrackObjeto", back_populates="observaciones")
    deteccion = relationship("DeteccionCamara", back_populates="observaciones")
    camara = relationship("Camara", back_populates="observaciones")


class ComportamientoDetectado(Base):
    __tablename__ = "comportamientos_detectados"

    id_comportamiento: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_deteccion: Mapped[int] = mapped_column(ForeignKey("detecciones_camara.id_deteccion"), nullable=False)
    id_modelo: Mapped[int | None] = mapped_column(ForeignKey("modelos_ia.id_modelo"), nullable=True)

    tipo_comportamiento: Mapped[str] = mapped_column(String(100), nullable=False)
    confianza = mapped_column(Numeric(6, 4), nullable=True)
    severidad = mapped_column(Numeric(5, 2), nullable=True)

    extra_metadata = mapped_column("metadata", JSONB, nullable=True)
    fecha_deteccion = mapped_column(DateTime, server_default=func.now(), nullable=False)

    deteccion = relationship("DeteccionCamara", back_populates="comportamientos")
    modelo = relationship("ModeloIA", back_populates="comportamientos")