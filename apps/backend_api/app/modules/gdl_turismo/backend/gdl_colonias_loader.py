import os
import json
from pathlib import Path


def get_project_root() -> Path:
    """
    Busca la raíz del proyecto cuando se ejecuta localmente.
    En Docker es mejor usar variables de entorno.
    """
    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "apps").exists() and (parent / "data").exists():
            return parent

    raise RuntimeError("No se pudo encontrar la raíz del proyecto GDL-Hackathon.")


def get_data_dir() -> Path:
    """
    En Docker usa DATA_DIR=/workspace/data.
    En local intenta resolver desde la raíz del proyecto.
    """
    data_dir_env = os.getenv("DATA_DIR")

    if data_dir_env:
        return Path(data_dir_env)

    project_root = get_project_root()
    return project_root / "data"


def load_json_file(relative_path: str):
    data_dir = get_data_dir()
    json_path = data_dir / relative_path

    if not json_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON: {json_path}")

    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def cargar_colonias_jalisco():
    return load_json_file("gdl_turismo/gdl_colonias_jalisco.json")