from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

from modelo import CAMINO, PARED, PUNTO, TableroJuego
from persistencia import GestorPuntuaciones


TAMANO_CASILLA = 32
INTERVALO_CICLO_MS = 150


def _formatear_fecha(fecha: str) -> str:
    if fecha == "Sin fecha":
        return fecha
    try:
        return datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S").strftime(
            "%d/%m/%Y %H:%M"
        )
    except ValueError:
        return fecha


class AplicacionPacman:

    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Sistema Pacman POO")
        self.raiz.resizable(False, False)

        archivo_puntuaciones = Path(__file__).with_name("puntuaciones.json")
        self.gestor_puntuaciones = GestorPuntuaciones(archivo_puntuaciones)
        self.jugador = ""
        self.tablero: TableroJuego | None = None
        self._after_id: str | None = None
        self._puntuacion_guardada = False

        self._crear_interfaz()
        self._conectar_teclas()

        nombre = self._pedir_nombre()
        if nombre is None:
            self.raiz.destroy()
            return
        self._iniciar_partida(nombre)

    def _crear_interfaz(self) -> None:
        contenedor = tk.Frame(self.raiz, padx=12, pady=12)
        contenedor.pack()

        panel_juego = tk.Frame(contenedor)
        panel_juego.grid(row=0, column=0, sticky="n")
        panel_lateral = tk.Frame(contenedor, padx=16)
        panel_lateral.grid(row=0, column=1, sticky="n")

        self.texto_jugador = tk.StringVar()
        self.texto_puntaje = tk.StringVar()
        self.texto_vidas = tk.StringVar()
        tk.Label(panel_juego, textvariable=self.texto_jugador).pack(anchor="w")
        tk.Label(panel_juego, textvariable=self.texto_puntaje).pack(anchor="w")
        tk.Label(panel_juego, textvariable=self.texto_vidas).pack(anchor="w")

        self.canvas = tk.Canvas(
            panel_juego,
            width=len(TableroJuego.LABERINTO_PREDETERMINADO[0]) * TAMANO_CASILLA,
            height=len(TableroJuego.LABERINTO_PREDETERMINADO) * TAMANO_CASILLA,
            background="black",
            highlightthickness=0,
            takefocus=True,
        )
        self.canvas.pack(pady=(8, 0))

        tk.Label(panel_lateral, text="Top 5", font=("TkDefaultFont", 12, "bold")).pack()
        self.texto_ranking = tk.StringVar()
        tk.Label(
            panel_lateral,
            textvariable=self.texto_ranking,
            justify="left",
            anchor="nw",
        ).pack(anchor="w", pady=(6, 14))
        tk.Button(
            panel_lateral,
            text="Nuevo jugador (Ctrl+N)",
            command=self._nuevo_jugador,
        ).pack(anchor="w")

    def _conectar_teclas(self) -> None:
        direcciones = {
            "<Up>": "arriba",
            "<Down>": "abajo",
            "<Left>": "izquierda",
            "<Right>": "derecha",
        }
        for tecla, direccion in direcciones.items():
            self.raiz.bind_all(
                tecla,
                lambda evento, nueva_direccion=direccion: self._cambiar_direccion(
                    nueva_direccion
                ),
            )
        self.raiz.bind_all("<Control-n>", self._nuevo_jugador)
        self.raiz.bind_all("<Control-N>", self._nuevo_jugador)

    def _pedir_nombre(self) -> str | None:
        while True:
            nombre = simpledialog.askstring(
                "Nuevo jugador",
                "Ingresá el nombre del jugador:",
                parent=self.raiz,
            )
            if nombre is None:
                return None
            if nombre.strip():
                return nombre.strip()
            messagebox.showwarning(
                "Nombre requerido",
                "El nombre no puede estar vacío.",
                parent=self.raiz,
            )

    def _iniciar_partida(self, nombre: str) -> None:
        self._cancelar_ciclo()
        self.jugador = nombre
        self.tablero = TableroJuego()
        self._puntuacion_guardada = False
        self._dibujar()
        self._actualizar_ranking()
        if self.tablero.juego_terminado:
            self._finalizar_partida()
        else:
            self._programar_ciclo()
        self.canvas.focus_set()

    def _nuevo_jugador(self, evento: tk.Event | None = None) -> str:
        self._cancelar_ciclo()
        nombre = self._pedir_nombre()
        if nombre is not None:
            self._iniciar_partida(nombre)
        elif self.tablero is not None and not self.tablero.juego_terminado:
            self._programar_ciclo()
        return "break"

    def _cambiar_direccion(self, direccion: str) -> str:
        if self.tablero is not None and not self.tablero.juego_terminado:
            self.tablero.pacman.direccion = direccion
        return "break"

    def _programar_ciclo(self) -> None:
        if self.tablero is not None and not self.tablero.juego_terminado:
            self._after_id = self.raiz.after(
                INTERVALO_CICLO_MS,
                self._actualizar_ciclo,
            )

    def _cancelar_ciclo(self) -> None:
        if self._after_id is not None:
            self.raiz.after_cancel(self._after_id)
            self._after_id = None

    def _actualizar_ciclo(self) -> None:
        self._after_id = None
        if self.tablero is None or self.tablero.juego_terminado:
            return

        self.tablero.actualizar_ciclo()
        self._dibujar()
        if self.tablero.juego_terminado:
            self._finalizar_partida()
        else:
            self._programar_ciclo()

    def _dibujar(self) -> None:
        if self.tablero is None:
            return

        laberinto = self.tablero.laberinto
        self.canvas.delete("all")
        for y, fila in enumerate(laberinto):
            for x, casilla in enumerate(fila):
                izquierda = x * TAMANO_CASILLA
                arriba = y * TAMANO_CASILLA
                derecha = izquierda + TAMANO_CASILLA
                abajo = arriba + TAMANO_CASILLA
                if casilla == PARED:
                    self.canvas.create_rectangle(
                        izquierda,
                        arriba,
                        derecha,
                        abajo,
                        fill="navy",
                        outline="blue",
                    )
                elif casilla == PUNTO:
                    centro_x = izquierda + TAMANO_CASILLA // 2
                    centro_y = arriba + TAMANO_CASILLA // 2
                    radio = 3
                    self.canvas.create_oval(
                        centro_x - radio,
                        centro_y - radio,
                        centro_x + radio,
                        centro_y + radio,
                        fill="white",
                        outline="white",
                    )
                elif casilla == CAMINO:
                    self.canvas.create_rectangle(
                        izquierda,
                        arriba,
                        derecha,
                        abajo,
                        fill="black",
                        outline="black",
                    )

        self._dibujar_personaje(
            self.tablero.pacman.pos_x,
            self.tablero.pacman.pos_y,
            self.tablero.pacman.color,
        )
        for fantasma in self.tablero.fantasmas:
            self._dibujar_personaje(fantasma.pos_x, fantasma.pos_y, fantasma.color)

        self.texto_jugador.set(f"Jugador: {self.jugador}")
        self.texto_puntaje.set(f"Puntaje: {self.tablero.puntaje}")
        self.texto_vidas.set(f"Vidas: {self.tablero.pacman.vidas}")

    def _dibujar_personaje(self, x: int, y: int, color: str) -> None:
        margen = 4
        izquierda = x * TAMANO_CASILLA + margen
        arriba = y * TAMANO_CASILLA + margen
        derecha = (x + 1) * TAMANO_CASILLA - margen
        abajo = (y + 1) * TAMANO_CASILLA - margen
        self.canvas.create_oval(
            izquierda,
            arriba,
            derecha,
            abajo,
            fill=color,
            outline=color,
        )

    def _actualizar_ranking(self) -> None:
        try:
            mejores = self.gestor_puntuaciones.obtener_mejores_puntuaciones(5)
        except (OSError, ValueError) as error:
            self.texto_ranking.set("No se pudo leer el ranking.")
            messagebox.showerror(
                "Error de puntuaciones",
                str(error),
                parent=self.raiz,
            )
            return

        if not mejores:
            self.texto_ranking.set("Todavía no hay puntuaciones.")
            return
        lineas = [
            f"{posicion}. {registro['nombre']} - {registro['puntaje']} pts - "
            f"{_formatear_fecha(str(registro['fecha']))}"
            for posicion, registro in enumerate(mejores, start=1)
        ]
        self.texto_ranking.set("\n".join(lineas))

    def _finalizar_partida(self) -> None:
        if self.tablero is None:
            return

        if not self._puntuacion_guardada:
            try:
                self.gestor_puntuaciones.guardar_puntuacion(
                    self.jugador,
                    self.tablero.puntaje,
                )
                self._puntuacion_guardada = True
            except (OSError, ValueError) as error:
                messagebox.showerror(
                    "Error al guardar la puntuación",
                    str(error),
                    parent=self.raiz,
                )

        self._actualizar_ranking()
        if self.tablero.victoria:
            mensaje = f"¡Victoria, {self.jugador}! Puntaje: {self.tablero.puntaje}"
        else:
            mensaje = f"Game Over, {self.jugador}. Puntaje: {self.tablero.puntaje}"
        messagebox.showinfo("Partida terminada", mensaje, parent=self.raiz)


def main() -> None:
    raiz = tk.Tk()
    AplicacionPacman(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
