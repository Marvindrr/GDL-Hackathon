from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class EventoSeguridad(Base):
    __tablename__ = "eventos_seguridad"

    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    id_zona: Mapped[int | None] = mapped_column(ForeignKey("zonas.id_zona"), nullable=True)
    id_track: Mapped[int | None] = mapped_column(ForeignKey("track_objetos.id_track"), nullable=True)

    tipo_evento: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="activo")
    severidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    lat = mapped_column(Numeric(10, 7), nullable=True)
    lon = mapped_column(Numeric(10, 7), nullable=True)
    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    fecha_inicio = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_fin = mapped_column(DateTime, nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    zona = relationship("Zona", back_populates="eventos")
    track = relationship("TrackObjeto", back_populates="eventos")
    detecciones = relationship("DeteccionCamara", back_populates="evento")
    deteccion_links = relationship("EventoDeteccion", back_populates="evento")
    evidencias = relationship("EvidenciaMedia", back_populates="evento")
    alertas = relationship("AlertaSeguridad", back_populates="evento")
    rutas = relationship("RutaCalculada", back_populates="evento")


class EventoDeteccion(Base):
    __tablename__ = "evento_detecciones"

    id_evento_deteccion: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_evento: Mapped[int] = mapped_column(ForeignKey("eventos_seguridad.id_evento"), nullable=False)
    id_deteccion: Mapped[int] = mapped_column(ForeignKey("detecciones_camara.id_deteccion"), nullable=False)

    relacion: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    evento = relationship("EventoSeguridad", back_populates="deteccion_links")
    deteccion = relationship("DeteccionCamara", back_populates="evento_links")


class EvidenciaMedia(Base):
    __tablename__ = "evidencias_media"

    id_evidencia: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_evento: Mapped[int | None] = mapped_column(ForeignKey("eventos_seguridad.id_evento"), nullable=True)
    id_deteccion: Mapped[int | None] = mapped_column(ForeignKey("detecciones_camara.id_deteccion"), nullable=True)

    tipo_media: Mapped[str] = mapped_column(String(50), nullable=False)
    path_archivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    url_archivo: Mapped[str | None] = mapped_column(Text, nullable=True)

    fecha_captura = mapped_column(DateTime, nullable=True)
    extra_metadata = mapped_column("metadata", JSONB, nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    evento = relationship("EventoSeguridad", back_populates="evidencias")
    deteccion = relationship("DeteccionCamara", back_populates="evidencias")


class AlertaSeguridad(Base):
    __tablename__ = "alertas_seguridad"

    id_alerta: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_evento: Mapped[int] = mapped_column(ForeignKey("eventos_seguridad.id_evento"), nullable=False)

    tipo_alerta: Mapped[str] = mapped_column(String(80), nullable=False)
    prioridad: Mapped[str] = mapped_column(String(50), nullable=False, default="media")
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="pendiente")
    mensaje: Mapped[str | None] = mapped_column(Text, nullable=True)

    fecha_alerta = mapped_column(DateTime, server_default=func.now(), nullable=False)
    fecha_atencion = mapped_column(DateTime, nullable=True)

    evento = relationship("EventoSeguridad", back_populates="alertas")