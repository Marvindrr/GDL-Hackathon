import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.infrastructure.db.base import Base
from app.infrastructure.db import models  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://segury:segury123@postgres_postgis:5432/segurytech"
)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


POSTGIS_INTERNAL_TABLES = {
    "spatial_ref_sys",
    "geometry_columns",
    "geography_columns",
    "raster_columns",
    "raster_overviews",

    # PostGIS / Tiger / Topology
    "addr",
    "addrfeat",
    "bg",
    "county",
    "county_lookup",
    "countysub_lookup",
    "cousub",
    "direction_lookup",
    "edges",
    "faces",
    "featnames",
    "geocode_settings",
    "geocode_settings_default",
    "layer",
    "loader_lookuptables",
    "loader_platform",
    "loader_variables",
    "pagc_gaz",
    "pagc_lex",
    "pagc_rules",
    "place",
    "place_lookup",
    "secondary_unit_lookup",
    "state",
    "state_lookup",
    "street_type_lookup",
    "tabblock",
    "tabblock20",
    "topology",
    "tract",
    "zcta5",
    "zip_lookup",
    "zip_lookup_all",
    "zip_lookup_base",
    "zip_state",
    "zip_state_loc",
}


def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "table" and name in POSTGIS_INTERNAL_TABLES:
        return False

    if type_ == "index":
        table_name = getattr(object_.table, "name", None)
        if table_name in POSTGIS_INTERNAL_TABLES:
            return False

    return True


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()