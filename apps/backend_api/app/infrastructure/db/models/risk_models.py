from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base


class FactorRiesgoZona(Base):
    __tablename__ = "factores_riesgo_zona"

    id_factor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    id_zona: Mapped[int] = mapped_column(ForeignKey("zonas.id_zona"), nullable=False)
    id_fuente: Mapped[int | None] = mapped_column(ForeignKey("fuentes_datos.id_fuente"), nullable=True)

    fecha_inicio = mapped_column(DateTime, nullable=True)
    fecha_fin = mapped_column(DateTime, nullable=True)

    reportes_score = mapped_column(Numeric(5, 2), nullable=False, default=0)
    luz_score = mapped_column(Numeric(5, 2), nullable=False, default=50)
    reputacion_score = mapped_column(Numeric(5, 2), nullable=False, default=50)
    hora_score = mapped_column(Numeric(5, 2), nullable=False, default=0)
    camaras_score = mapped_column(Numeric(5, 2), nullable=False, default=50)
    flujo_personas_score = mapped_column(Numeric(5, 2), nullable=False, default=50)
    comportamiento_score = mapped_column(Numeric(5, 2), nullable=False, default=0)

    riesgo_total = mapped_column(Numeric(5, 2), nullable=False, default=0)

    created_at = mapped_column(DateTime, server_default=func.now(), nullable=False)

    zona = relationship("Zona", back_populates="factores_riesgo")
    fuente = relationship("FuenteDatos", back_populates="factores_riesgo")


class HistorialRiesgoZona(Base):
    __tablename__ = "historial_riesgo_zona"

    id_historial: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_zona: Mapped[int] = mapped_column(ForeignKey("zonas.id_zona"), nullable=False)

    riesgo_total = mapped_column(Numeric(5, 2), nullable=False)
    desglose = mapped_column(JSONB, nullable=True)
    algoritmo: Mapped[str | None] = mapped_column(String(120), nullable=True)

    fecha_calculo = mapped_column(DateTime, server_default=func.now(), nullable=False)

    zona = relationship("Zona", back_populates="historial_riesgo")