import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


class GestorPuntuaciones:
    def __init__(self, nombre_archivo: str | Path = "puntuaciones.json") -> None:
        ruta = str(nombre_archivo)
        if not ruta.strip():
            raise ValueError("El nombre del archivo no puede estar vacío.")
        self.nombre_archivo = ruta

    def guardar_puntuacion(self, nombre: str, puntaje: int) -> str:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del jugador no puede estar vacío.")
        if isinstance(puntaje, bool) or not isinstance(puntaje, int) or puntaje < 0:
            raise ValueError("El puntaje debe ser un entero no negativo.")

        historial = self._leer_historial()
        identificador = str(uuid4())
        historial.append(
            {
                "id": identificador,
                "nombre": nombre.strip(),
                "puntaje": puntaje,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        ruta = Path(self.nombre_archivo)
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with ruta.open("w", encoding="utf-8") as archivo:
                json.dump(historial, archivo, ensure_ascii=False, indent=2)
                archivo.write("\n")
        except OSError as error:
            raise OSError(f"No se pudo guardar el historial de puntuaciones: {ruta}") from error
        return identificador

    def obtener_mejores_puntuaciones(self, n: int = 5) -> list[dict[str, str | int]]:
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError("n debe ser un entero no negativo.")
        historial = self._leer_historial()
        ordenados = sorted(
            historial,
            key=lambda registro: registro["puntaje"],
            reverse=True,
        )
        return ordenados[:n]

    def _leer_historial(self) -> list[dict[str, str | int]]:
        ruta = Path(self.nombre_archivo)
        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                contenido = archivo.read()
        except FileNotFoundError:
            return []
        except OSError as error:
            raise OSError(f"No se pudo leer el historial de puntuaciones: {ruta}") from error

        if not contenido.strip():
            return []

        try:
            historial = json.loads(contenido)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"El archivo de puntuaciones contiene JSON inválido: {ruta}"
            ) from error

        if not isinstance(historial, list):
            raise ValueError("El historial JSON debe contener una lista de registros.")

        for indice, registro in enumerate(historial):
            if (
                not isinstance(registro, dict)
                or set(registro)
                not in (
                    {"id", "nombre", "puntaje"},
                    {"id", "nombre", "puntaje", "fecha"},
                )
                or not isinstance(registro.get("id"), str)
                or not registro["id"]
                or not isinstance(registro.get("nombre"), str)
                or not registro["nombre"].strip()
                or isinstance(registro.get("puntaje"), bool)
                or not isinstance(registro.get("puntaje"), int)
                or registro["puntaje"] < 0
            ):
                raise ValueError(
                    f"El registro de puntuación en la posición {indice} no es válido."
                )
            registro.setdefault("fecha", "Sin fecha")
            if not isinstance(registro["fecha"], str):
                raise ValueError(
                    f"La fecha de puntuación en la posición {indice} no es válida."
                )
        return historial
