from sqlalchemy import (BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.infrastructure.db.base import Base


class Municipio(Base):
    __tablename__ = "municipios"

    id_municipio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str] = mapped_column(String(120), nullable=False, default="Jalisco")
    geom: Mapped[object] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    zonas = relationship("Zona", back_populates="municipio")
    camaras = relationship("Camara", back_populates="municipio")
    puntos_turisticos = relationship("PuntoTuristico", back_populates="municipio")


class Zona(Base):
    __tablename__ = "zonas"

    id_zona: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_municipio: Mapped[int | None] = mapped_column(ForeignKey("municipios.id_municipio"), nullable=True)

    nombre: Mapped[str] = mapped_column(String(180), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, default="colonia")

    riesgo_base = mapped_column(Numeric(5, 2), nullable=False, default=0)
    reputacion_base = mapped_column(Numeric(5, 2), nullable=False, default=50)
    nivel_luz_base = mapped_column(Numeric(5, 2), nullable=True)

    geom = mapped_column(Geometry("MULTIPOLYGON", srid=4326, spatial_index=False), nullable=True)
    centro = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=True)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    municipio = relationship("Municipio", back_populates="zonas")
    camaras = relationship("Camara", back_populates="zona")
    reportes = relationship("ReporteSeguridad", back_populates="zona")
    eventos = relationship("EventoSeguridad", back_populates="zona")
    factores_riesgo = relationship("FactorRiesgoZona", back_populates="zona")
    historial_riesgo = relationship("HistorialRiesgoZona", back_populates="zona")


class PuntoTuristico(Base):
    __tablename__ = "puntos_turisticos"

    id_punto_turistico: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_municipio: Mapped[int | None] = mapped_column(ForeignKey("municipios.id_municipio"), nullable=True)

    nombre: Mapped[str] = mapped_column(String(180), nullable=False)
    categoria: Mapped[str | None] = mapped_column(String(80), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    lat = mapped_column(Numeric(10, 7), nullable=False)
    lon = mapped_column(Numeric(10, 7), nullable=False)
    ubicacion = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)

    activo = mapped_column(Boolean, default=True, nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    municipio = relationship("Municipio", back_populates="puntos_turisticos")
    rutas = relationship("RutaCalculada", back_populates="punto_turistico")


class CalleNode(Base):
    __tablename__ = "calles_nodes"

    id_node: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)


class CalleEdge(Base):
    __tablename__ = "calles_edges"

    id_edge: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    source: Mapped[int | None] = mapped_column(ForeignKey("calles_nodes.id_node"), nullable=True)
    target: Mapped[int | None] = mapped_column(ForeignKey("calles_nodes.id_node"), nullable=True)
    id_zona: Mapped[int | None] = mapped_column(ForeignKey("zonas.id_zona"), nullable=True)

    nombre: Mapped[str | None] = mapped_column(String(180), nullable=True)
    tipo_via: Mapped[str | None] = mapped_column(String(80), nullable=True)

    distancia_m = mapped_column(Numeric(12, 2), nullable=True)
    velocidad_estimada_kmh = mapped_column(Numeric(8, 2), nullable=False, default=30)
    riesgo_base = mapped_column(Numeric(5, 2), nullable=False, default=0)
    costo_base = mapped_column(Numeric(12, 4), nullable=False, default=1)

    geom = mapped_column(Geometry("LINESTRING", srid=4326, spatial_index=False), nullable=False)
    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)