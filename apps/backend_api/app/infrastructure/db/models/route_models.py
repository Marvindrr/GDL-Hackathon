from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class RutaCalculada(Base):
    __tablename__ = "rutas_calculadas"

    id_ruta: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_evento: Mapped[int | None] = mapped_column(ForeignKey("eventos_seguridad.id_evento"), nullable=True)
    id_track: Mapped[int | None] = mapped_column(ForeignKey("track_objetos.id_track"), nullable=True)
    id_punto_turistico: Mapped[int | None] = mapped_column(ForeignKey("puntos_turisticos.id_punto_turistico"), nullable=True)

    tipo_ruta: Mapped[str] = mapped_column(String(80), nullable=False)

    origen = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)
    destino = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    score_riesgo = mapped_column(Numeric(5, 2), nullable=True)
    score_confianza = mapped_column(Numeric(5, 2), nullable=True)
    distancia_m = mapped_column(Numeric(12, 2), nullable=True)
    duracion_estimada_seg = mapped_column(Numeric(12, 2), nullable=True)

    algoritmo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    parametros = mapped_column(JSONB, nullable=True)

    geom = mapped_column(Geometry("LINESTRING", srid=4326, spatial_index=False), nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    evento = relationship("EventoSeguridad", back_populates="rutas")
    track = relationship("TrackObjeto", back_populates="rutas")
    punto_turistico = relationship("PuntoTuristico", back_populates="rutas")
    segmentos = relationship("RutaSegmento", back_populates="ruta")
    puntos_control = relationship("RutaPuntoControl", back_populates="ruta")


class RutaSegmento(Base):
    __tablename__ = "rutas_segmentos"

    id_segmento: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_ruta: Mapped[int] = mapped_column(ForeignKey("rutas_calculadas.id_ruta"), nullable=False)
    id_edge: Mapped[int | None] = mapped_column(ForeignKey("calles_edges.id_edge"), nullable=True)

    orden: Mapped[int] = mapped_column(Integer, nullable=False)

    distancia_m = mapped_column(Numeric(12, 2), nullable=True)
    riesgo_segmento = mapped_column(Numeric(5, 2), nullable=True)
    costo_segmento = mapped_column(Numeric(12, 4), nullable=True)

    geom = mapped_column(Geometry("LINESTRING", srid=4326, spatial_index=False), nullable=True)

    ruta = relationship("RutaCalculada", back_populates="segmentos")


class RutaPuntoControl(Base):
    __tablename__ = "ruta_puntos_control"

    id_punto_control: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_ruta: Mapped[int] = mapped_column(ForeignKey("rutas_calculadas.id_ruta"), nullable=False)

    orden: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_punto: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    ruta = relationship("RutaCalculada", back_populates="puntos_control")