from decimal import Decimal, InvalidOperation


def first_value(item: dict, keys: list[str], default=None):
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
    return default


def to_decimal(value):
    if value in (None, ""):
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def get_denue_id(item: dict):
    return str(first_value(item, [
        "Id",
        "id",
        "id_establecimiento",
        "Id_establecimiento",
        "idEstablecimiento",
    ], ""))


def get_nombre(item: dict):
    return str(first_value(item, [
        "Nombre",
        "nombre",
        "nom_estab",
        "Nombre_establecimiento",
    ], "")).strip()


def get_razon_social(item: dict):
    return str(first_value(item, [
        "Razon_social",
        "Razón social",
        "raz_social",
        "RazonSocial",
    ], "")).strip()


def get_lat(item: dict):
    return to_decimal(first_value(item, [
        "Latitud",
        "latitud",
        "lat",
        "Lat",
    ]))


def get_lon(item: dict):
    return to_decimal(first_value(item, [
        "Longitud",
        "longitud",
        "lon",
        "Lon",
        "lng",
    ]))


def get_calle(item: dict):
    return str(first_value(item, [
        "Calle",
        "calle",
        "Tipo_vialidad",
        "Vialidad",
    ], "")).strip()


def get_num_ext(item: dict):
    return str(first_value(item, [
        "Num_Exterior",
        "Número exterior",
        "num_ext",
        "numero_ext",
    ], "")).strip()


def get_colonia(item: dict):
    return str(first_value(item, [
        "Colonia",
        "colonia",
        "Tipo_asentamiento",
        "asentamiento",
    ], "")).strip()


def get_cp(item: dict):
    return str(first_value(item, [
        "CP",
        "Código postal",
        "codigo_postal",
        "cod_postal",
    ], "")).strip()


def get_telefono(item: dict):
    return str(first_value(item, [
        "Telefono",
        "Teléfono",
        "telefono",
    ], "")).strip()


def get_sitio_web(item: dict):
    return str(first_value(item, [
        "Sitio_internet",
        "Página de internet",
        "www",
        "sitio_web",
    ], "")).strip()


def build_direccion(item: dict):
    calle = get_calle(item)
    num_ext = get_num_ext(item)
    colonia = get_colonia(item)
    cp = get_cp(item)

    partes = []

    if calle:
        partes.append(calle)

    if num_ext:
        partes.append(f"#{num_ext}")

    if colonia:
        partes.append(f"Col. {colonia}")

    if cp:
        partes.append(f"C.P. {cp}")

    return ", ".join(partes) if partes else None