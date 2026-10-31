rom abc import ABC, abstractmethod
import random
PARED = "#"
PUNTO = "."
CAMINO = " "


class Entidad(ABC):

    def __init__(self, pos_x: int, pos_y: int, color: str) -> None:
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.color = color

    @property
    def pos_x(self) -> int:
        return self._pos_x

    @pos_x.setter
    def pos_x(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError("pos_x debe ser un entero no negativo.")
        self._pos_x = valor

    @property
    def pos_y(self) -> int:
        return self._pos_y

    @pos_y.setter
    def pos_y(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError("pos_y debe ser un entero no negativo.")
        self._pos_y = valor

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El color debe ser un texto no vacío.")
        self._color = valor

    def mover(self, desplazamiento_x: int, desplazamiento_y: int) -> None:
        for desplazamiento in (desplazamiento_x, desplazamiento_y):
            if isinstance(desplazamiento, bool) or not isinstance(desplazamiento, int):
                raise ValueError("Los desplazamientos deben ser enteros.")
        nueva_x = self.pos_x + desplazamiento_x
        nueva_y = self.pos_y + desplazamiento_y
        if nueva_x < 0 or nueva_y < 0:
            raise ValueError("La posición resultante no puede ser negativa.")
        self.pos_x = nueva_x
        self.pos_y = nueva_y

    @abstractmethod
    def actualizar(
        self,
        movimientos_permitidos: tuple[tuple[int, int], ...] | None = None,
    ) -> None:
     

class Pacman(Entidad):
    _DESPLAZAMIENTOS = {
        "arriba": (0, -1),
        "abajo": (0, 1),
        "izquierda": (-1, 0),
        "derecha": (1, 0),
        "quieto": (0, 0),
    }

    def __init__(
        self,
        pos_x: int,
        pos_y: int,
        color: str = "yellow",
        vidas: int = 3,
    ) -> None:
        super().__init__(pos_x, pos_y, color)
        self._pos_inicial = (pos_x, pos_y)
        self.direccion = "quieto"
        self.vidas = vidas

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        if not isinstance(valor, str) or valor not in self._DESPLAZAMIENTOS:
            opciones = ", ".join(self._DESPLAZAMIENTOS)
            raise ValueError(f"direccion debe ser una de estas opciones: {opciones}.")
        self._direccion = valor

    @property
    def vidas(self) -> int:
        return self._vidas

    @vidas.setter
    def vidas(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
            raise ValueError("Las vidas deben ser un entero no negativo.")
        self._vidas = valor

    def perder_vida(self) -> None:
        if self.vidas > 0:
            self.vidas -= 1

    def reiniciar_posicion(self) -> None:
        self.pos_x, self.pos_y = self._pos_inicial
        self.direccion = "quieto"

    # Herencia: Pacman redefine el comportamiento abstracto de Entidad.
    def actualizar(
        self,
        movimientos_permitidos: tuple[tuple[int, int], ...] | None = None,
    ) -> None:
        desplazamiento = self._DESPLAZAMIENTOS[self.direccion]
        if desplazamiento == (0, 0):
            return

        nueva_x = self.pos_x + desplazamiento[0]
        nueva_y = self.pos_y + desplazamiento[1]
        dentro_de_limites = nueva_x >= 0 and nueva_y >= 0
        permitido_por_el_tablero = (
            movimientos_permitidos is None
            or desplazamiento in movimientos_permitidos
        )
        if dentro_de_limites and permitido_por_el_tablero:
            self.mover(*desplazamiento)


class Fantasma(Entidad):

    _DESPLAZAMIENTOS = (
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0),
    )

    def __init__(
        self,
        nombre: str,
        pos_x: int,
        pos_y: int,
        color: str = "red",
    ) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del fantasma debe ser un texto no vacío.")
        super().__init__(pos_x, pos_y, color)
        self.nombre = nombre
        self._pos_inicial = (pos_x, pos_y)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
        self._nombre = valor

    @property
    def pos_inicial(self) -> tuple[int, int]:
        return self._pos_inicial

    def reiniciar_posicion(self) -> None:
        self.pos_x, self.pos_y = self.pos_inicial

    # Herencia: Fantasma redefine actualizar() con movimiento autónomo.
    def actualizar(
        self,
        movimientos_permitidos: tuple[tuple[int, int], ...] | None = None,
    ) -> None:
        if movimientos_permitidos is None:
            movimientos_validos = tuple(
                (dx, dy)
                for dx, dy in self._DESPLAZAMIENTOS
                if self.pos_x + dx >= 0 and self.pos_y + dy >= 0
            )
        else:
            movimientos_validos = movimientos_permitidos
        if not movimientos_validos:
            return
        desplazamiento = random.choice(movimientos_validos)
        self.mover(*desplazamiento)


class TableroJuego:
    """Administra el laberinto, las entidades y los ciclos de movimiento."""

    LABERINTO_PREDETERMINADO = [
        list("################"),
        list("#....#.......#.#"),
        list("#.##.#.##....#.#"),
        list("#.##.#....#....#"),
        list("#....#....#....#"),
        list("#..###....#..#.#"),
        list("#..#.....#...#.#"),
        list("#.##.....#.....#"),
        list("#.....#...##...#"),
        list("#.####..#....#.#"),
        list("#..#.#.##.####.#"),
        list("#....#..#.##...#"),
        list("#...##.##..#...#"),
        list("#.#...........##"),
        list("####...#....####"),
        list("################"),
    ]
    FANTASMAS_PREDETERMINADOS = (
        ("Leiru", 14, 1, "blue"),
        ("Atac", 4, 14, "pink"),
        ("Edef", 11, 14, "green"),
        ("Mairim", 8, 8, "red"),
    )

    def __init__(
        self,
        laberinto: list[list[str]] | None = None,
        pos_inicial_pacman: tuple[int, int] = (1, 1),
        posiciones_fantasmas: tuple[tuple[str, int, int, str], ...] | None = None,
    ) -> None:
        matriz = laberinto if laberinto is not None else self.LABERINTO_PREDETERMINADO
        self._laberinto = self._copiar_y_validar_laberinto(matriz)
        self._puntaje = 0
        self._juego_terminado = False
        self._victoria = False

        x_pacman, y_pacman = self._validar_posicion(pos_inicial_pacman)
        self._validar_casilla_transitable(x_pacman, y_pacman)
        # Composición: el tablero crea y administra las entidades de esta partida.
        self._pacman = Pacman(x_pacman, y_pacman)

        configuracion_fantasmas = (
            posiciones_fantasmas
            if posiciones_fantasmas is not None
            else self.FANTASMAS_PREDETERMINADOS
        )
        self._fantasmas: list[Fantasma] = []
        for nombre, x, y, color in configuracion_fantasmas:
            self._validar_casilla_transitable(x, y)
            self._fantasmas.append(Fantasma(nombre, x, y, color))

        self._recoger_punto()
        self._comprobar_victoria()

    @property
    def laberinto(self) -> list[list[str]]:
        return [fila.copy() for fila in self._laberinto]

    @property
    def pacman(self) -> Pacman:
        return self._pacman

    @property
    def fantasmas(self) -> list[Fantasma]:
        return self._fantasmas.copy()

    @property
    def puntaje(self) -> int:
        return self._puntaje

    @property
    def juego_terminado(self) -> bool:
        return self._juego_terminado

    @property
    def victoria(self) -> bool:
        return self._victoria

    @staticmethod
    def _validar_posicion(posicion: tuple[int, int]) -> tuple[int, int]:
        if (
            not isinstance(posicion, tuple)
            or len(posicion) != 2
            or any(
                isinstance(coordenada, bool)
                or not isinstance(coordenada, int)
                or coordenada < 0
                for coordenada in posicion
            )
        ):
            raise ValueError("La posición debe ser una tupla de dos enteros no negativos.")
        return posicion

    @staticmethod
    def _copiar_y_validar_laberinto(
        laberinto: list[list[str]],
    ) -> list[list[str]]:
        if not isinstance(laberinto, list) or not laberinto:
            raise ValueError("El laberinto debe ser una matriz no vacía.")
        if any(not isinstance(fila, list) or not fila for fila in laberinto):
            raise ValueError("Cada fila del laberinto debe ser una lista no vacía.")

        ancho = len(laberinto[0])
        if any(len(fila) != ancho for fila in laberinto):
            raise ValueError("Todas las filas del laberinto deben tener el mismo ancho.")
        if any(casilla not in (PARED, PUNTO, CAMINO) for fila in laberinto for casilla in fila):
            raise ValueError("El laberinto solo puede contener pared, punto o camino vacío.")
        return [fila.copy() for fila in laberinto]

    def _validar_casilla_transitable(self, x: int, y: int) -> None:
        x, y = self._validar_posicion((x, y))
        if y >= len(self._laberinto) or x >= len(self._laberinto[0]):
            raise ValueError("La posición inicial debe estar dentro del laberinto.")
        if self._laberinto[y][x] == PARED:
            raise ValueError("Una entidad no puede comenzar sobre una pared.")

    def _movimientos_validos(self, entidad: Entidad) -> tuple[tuple[int, int], ...]:
        movimientos = (
            Pacman._DESPLAZAMIENTOS.values()
            if isinstance(entidad, Pacman)
            else Fantasma._DESPLAZAMIENTOS
        )
        return tuple(
            (dx, dy)
            for dx, dy in movimientos
            if self._es_transitable(entidad.pos_x + dx, entidad.pos_y + dy)
        )

    def _es_transitable(self, x: int, y: int) -> bool:
        return (
            0 <= y < len(self._laberinto)
            and 0 <= x < len(self._laberinto[0])
            and self._laberinto[y][x] != PARED
        )

    def _recoger_punto(self) -> None:
        x, y = self._pacman.pos_x, self._pacman.pos_y
        if self._laberinto[y][x] == PUNTO:
            self._laberinto[y][x] = CAMINO
            self._puntaje += 10

    def actualizar_ciclo(self) -> None:
        """Mueve las entidades y resuelve colisiones, puntos y victoria."""
        if self._juego_terminado:
            return

        posicion_anterior_pacman = (self._pacman.pos_x, self._pacman.pos_y)
        posiciones_anteriores_fantasmas = [
            (fantasma.pos_x, fantasma.pos_y) for fantasma in self._fantasmas
        ]
        entidades: tuple[Entidad, ...] = (self._pacman, *self._fantasmas)
        for entidad in entidades:
            movimientos = self._movimientos_validos(entidad)
            # Polimorfismo: cada entidad aplica su propio comportamiento de actualización.
            entidad.actualizar(movimientos)

        if self._detectar_colision(
            posicion_anterior_pacman,
            posiciones_anteriores_fantasmas,
        ):
            self._pacman.perder_vida()
            self._reiniciar_posiciones_entidades()
            if self._pacman.vidas == 0:
                self._juego_terminado = True
            return

        self._recoger_punto()
        self._comprobar_victoria()

    def _detectar_colision(
        self,
        posicion_anterior_pacman: tuple[int, int],
        posiciones_anteriores_fantasmas: list[tuple[int, int]],
    ) -> bool:
        posicion_actual_pacman = (self._pacman.pos_x, self._pacman.pos_y)
        for fantasma, posicion_anterior_fantasma in zip(
            self._fantasmas,
            posiciones_anteriores_fantasmas,
        ):
            posicion_actual_fantasma = (fantasma.pos_x, fantasma.pos_y)
            misma_celda = posicion_actual_pacman == posicion_actual_fantasma
            # Cruce frontal: Pacman y el fantasma intercambiaron sus posiciones.
            cruce_frontal = (
                posicion_anterior_pacman == posicion_actual_fantasma
                and posicion_actual_pacman == posicion_anterior_fantasma
            )
            if misma_celda or cruce_frontal:
                return True
        return False

    def _comprobar_victoria(self) -> None:
        if not any(PUNTO in fila for fila in self._laberinto):
            self._victoria = True
            self._juego_terminado = True

    def _reiniciar_posiciones_entidades(self) -> None:
        self._pacman.reiniciar_posicion()
        for fantasma in self._fantasmas:
            fantasma.reiniciar_posicion()
