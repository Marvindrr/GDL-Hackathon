from .gdl_colonias_loader import load_json_file, cargar_colonias_jalisco


class GdlMapaService:

    @staticmethod
    def obtener_colonias():
        return cargar_colonias_jalisco()

    @staticmethod
    def obtener_puntos_turisticos():
        return load_json_file(
            "apps/frontend_web/static/modules/gdl_turismo/data/gdl_puntos_turisticos_ruta.json"
        )

    @staticmethod
    def obtener_zonas_turisticas():
        return load_json_file(
            "apps/frontend_web/static/modules/gdl_turismo/data/gdl_zonas_turisticas_normalizadas.json"
        )

    @staticmethod
    def obtener_resumen_modulo():
        colonias = GdlMapaService.obtener_colonias()
        puntos = GdlMapaService.obtener_puntos_turisticos()
        zonas = GdlMapaService.obtener_zonas_turisticas()

        return {
            "modulo": "gdl_turismo",
            "nombre": "Módulo turístico GDL",
            "total_colonias": len(colonias) if isinstance(colonias, list) else 1,
            "total_puntos_turisticos": len(puntos) if isinstance(puntos, list) else 1,
            "total_zonas_turisticas": len(zonas) if isinstance(zonas, list) else 1,
        }