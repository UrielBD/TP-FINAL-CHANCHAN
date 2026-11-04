# TP-FINAL-CHANCHAN
Trabajo final de programación
Integrantes:
Uriel Braslavsky ,
Catalina Ayala

Juego de Pacman desarrollado con Python y programación orientada a objetos. El
modelo administra el laberinto, los movimientos, los puntos, las colisiones y
las vidas sin depender de Tkinter. La interfaz dibuja el estado del modelo y
envía las teclas; el gestor de puntuaciones conserva cada partida en un archivo
JSON.
Al comenzar se solicita el nombre del jugador. La aplicación crea
"puntuaciones.json"

Controles y reglas

 Flechas: mover a Pacman.
- Botón Nuevo jugador o "Ctrl+N" va acomenzar otra partida con un nombre nuevo.
- Las paredes bloquean el movimiento
- Pacman suma 10 puntos por cada punto
  recogido.
- El laberinto predeterminado tiene 16 columnas y 16 filas, con pasillos
  irregulares y cuatro fantasmas: Leiru, Atac, Edef y Mairim. (Nombres al reves de los Greco"
- Una colisión en la misma casilla o un cruce frontal resta una vida y reinicia
  las posiciones de las entidades.
- La partida termina al consumir todos los puntos o al perder las tres vidas.
  La puntuación se guarda automáticamente al terminar.

En el laberinto, "#" representa una pared, "." un punto y un espacio una casilla
vacía.

En el codigo se presentan principios de:
Abstracción: "Entidad" es abstracta
Herencia: Pacman y Fantasma heredan de Entidad
Polimorfismo: Cada subclase redefine "actualizar()" el tablero recorre
  las entidades y usa ese método común.
Encapsulamiento: El estado interno usa atributos protegidos y propiedades
  con validación.
- **Composición:** `TableroJuego` crea y administra el Pacman y sus fantasmas.
