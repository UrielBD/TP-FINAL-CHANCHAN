

from abc import ABC, abstractmethod
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
        """Desplaza la entidad y valida la nueva posición."""
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
        pass


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

    def actualizar(
        self,
        movimientos_permitidos: tuple[tuple[int, int], ...] | None = None,
    ) -> None:
        """Avanza una celda en la dirección elegida por el jugador."""
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
        """Nombre identificador del fantasma."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre del fantasma debe ser un texto no vacío.")
        self._nombre = valor

    @property
    def pos_inicial(self) -> tuple[int, int]:
        """Posición original, expuesta como una tupla inmutable."""
        return self._pos_inicial

    def reiniciar_posicion(self) -> None:
        """Vuelve a la posición inicial del fantasma."""
        self.pos_x, self.pos_y = self.pos_inicial

    # Herencia: Fantasma redefine actualizar() con movimiento autónomo.
    def actualizar(
        self,
        movimientos_permitidos: tuple[tuple[int, int], ...] | None = None,
    ) -> None:
        """Elige un paso aleatorio entre los movimientos disponibles."""
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
