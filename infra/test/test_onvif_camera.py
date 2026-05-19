from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

IP = "192.168.100.241"
PORT = 8000

PASSWORD = "Uriel115"

USERS_TO_TEST = [
    "admin",
    "Admin",
    "administrator",
    "root",
]


def try_camera(user: str):
    print("=" * 60)
    print(f"Probando usuario: {user}")

    try:
        cam = ONVIFCamera(IP, PORT, user, PASSWORD, no_cache=True)

        print("Probando servicio Device Management...")
        devicemgmt = cam.create_devicemgmt_service()

        try:
            info = devicemgmt.GetDeviceInformation()
            print("Información del dispositivo:")
            print(info)
        except Exception as e:
            print("No se pudo obtener DeviceInformation:")
            print(e)

        print("Creando servicio Media...")
        media_service = cam.create_media_service()

        print("Obteniendo perfiles...")
        profiles = media_service.GetProfiles()

        if not profiles:
            print("No se encontraron perfiles.")
            return False

        print(f"Perfiles encontrados: {len(profiles)}")

        for profile in profiles:
            print("\nPerfil:")
            print("Nombre:", getattr(profile, "Name", "Sin nombre"))
            print("Token:", profile.token)

            request = media_service.create_type("GetStreamUri")
            request.StreamSetup = {
                "Stream": "RTP-Unicast",
                "Transport": {
                    "Protocol": "RTSP"
                }
            }
            request.ProfileToken = profile.token

            uri = media_service.GetStreamUri(request)

            print("URI RTSP encontrada:")
            print(uri.Uri)

        return True

    except ONVIFError as e:
        print("Error ONVIF:")
        print(e)
        return False

    except Exception as e:
        print("Error general:")
        print(e)
        return False


def main():
    print(f"Probando cámara ONVIF en {IP}:{PORT}")

    for user in USERS_TO_TEST:
        ok = try_camera(user)

        if ok:
            print("\nConexión ONVIF exitosa.")
            return

    print("\nNo funcionó con los usuarios probados.")
    print("Revisa usuario/contraseña ONVIF en la app Steren Home.")


if __name__ == "__main__":
    main()