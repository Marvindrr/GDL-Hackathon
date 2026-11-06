"""agregar puntos seguridad

Revision ID: 55a64bac03e6
Revises: 221f559e94f2
Create Date: 2026-05-19 16:14:38.962115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '55a64bac03e6'
down_revision: Union[str, None] = '221f559e94f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear la tabla principal
    op.create_table('puntos_seguridad',
        sa.Column('id_punto_seguridad', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('id_fuente', sa.Integer(), nullable=True),
        sa.Column('id_municipio', sa.Integer(), nullable=True),
        sa.Column('id_zona', sa.Integer(), nullable=True),
        sa.Column('id_externo', sa.String(length=120), nullable=True),
        sa.Column('nombre', sa.String(length=220), nullable=False),
        sa.Column('marca', sa.String(length=120), nullable=True),
        sa.Column('tipo_punto', sa.String(length=80), nullable=False),
        sa.Column('direccion', sa.Text(), nullable=True),
        sa.Column('colonia', sa.String(length=180), nullable=True),
        sa.Column('codigo_postal', sa.String(length=20), nullable=True),
        sa.Column('telefono', sa.String(length=80), nullable=True),
        sa.Column('sitio_web', sa.Text(), nullable=True),
        sa.Column('horario', sa.Text(), nullable=True),
        sa.Column('es_24h', sa.Boolean(), nullable=False),
        sa.Column('lat', sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column('lon', sa.Numeric(precision=10, scale=7), nullable=False),
        sa.Column('ubicacion', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
        sa.Column('validado_c5', sa.Boolean(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('nivel_confianza', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('peso_seguridad', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id_fuente'], ['fuentes_datos.id_fuente'], ),
        sa.ForeignKeyConstraint(['id_municipio'], ['municipios.id_municipio'], ),
        sa.ForeignKeyConstraint(['id_zona'], ['zonas.id_zona'], ),
        sa.PrimaryKeyConstraint('id_punto_seguridad'),
        sa.UniqueConstraint('id_fuente', 'id_externo', name='uq_puntos_seguridad_fuente_externo')
    )

    # 2. Agregar los índices personalizados para la nueva tabla
    op.create_index(
        "idx_puntos_seguridad_ubicacion",
        "puntos_seguridad",
        ["ubicacion"],
        postgresql_using="gist",
    )
    op.create_index(
        "idx_puntos_seguridad_tipo",
        "puntos_seguridad",
        ["tipo_punto"],
    )
    op.create_index(
        "idx_puntos_seguridad_marca",
        "puntos_seguridad",
        ["marca"],
    )
    op.create_index(
        "idx_puntos_seguridad_activo",
        "puntos_seguridad",
        ["activo"],
    )
    
    # Nota: Se eliminaron todos los op.drop_index basura que Alembic generó por error para las otras tablas.


def downgrade() -> None:
    # 1. Eliminar los índices en el downgrade (orden inverso al upgrade)
    op.drop_index("idx_puntos_seguridad_activo", table_name="puntos_seguridad")
    op.drop_index("idx_puntos_seguridad_marca", table_name="puntos_seguridad")
    op.drop_index("idx_puntos_seguridad_tipo", table_name="puntos_seguridad")
    op.drop_index("idx_puntos_seguridad_ubicacion", table_name="puntos_seguridad")

    # 2. Eliminar la tabla
    op.drop_table('puntos_seguridad')
    
    # Nota: Se eliminaron todos los op.create_index basura que Alembic generó por error para las otras tablas.