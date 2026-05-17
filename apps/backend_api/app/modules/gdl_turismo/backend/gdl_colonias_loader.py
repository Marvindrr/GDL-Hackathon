from pathlib import Path
import json


def get_project_root() -> Path:
    current_path = Path(__file__).resolve()

    for parent in current_path.parents:
        if (parent / "apps").exists() and (parent / "data").exists():
            return parent

    raise RuntimeError("No se pudo encontrar la raíz del proyecto GDL-Hackathon.")


def load_json_file(relative_path: str):
    project_root = get_project_root()
    json_path = project_root / relative_path

    if not json_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON: {json_path}")

    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def cargar_colonias_jalisco():
    return load_json_file("data/gdl_turismo/gdl_colonias_jalisco.json")