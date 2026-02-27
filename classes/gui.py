# Modulos de python.
import sys
from typing import Tuple

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from utils import constants as c

class TextBox():
    # Cuadro de texto simple para mostrar texto en pantalla.
    def __init__(self,
                 x: int,
                 y: int,
                 font: pg.font.Font,
                 caption: str,
                 color: Tuple[int, int, int]
                 ) -> None:
        # Inicializa el texto y su rectangulo.
        self.caption: pg.Surface = font.render(caption, True, color)
        self.caption_rect: pg.Rect = self.caption.get_rect()
        self.caption_rect.topleft = (x, y)

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja el texto en la superficie.
        surface.blit(self.caption, self.caption_rect)

class Button():
    # Boton interactivo con texto y colores.
    def __init__(self,
                 x: int, # Coordenada x de la esquina superior izquierda.
                 y: int, # Coordenada y de la esquina superior izquierda.
                 w: int, # Ancho del boton.
                 h: int, # Alto del boton.
                 color_bg: Tuple[int, int, int], # Color de fondo.
                 color_fg: Tuple[int, int, int], # Color del texto.
                 color_select: Tuple[int, int, int], # Color cuando el mouse esta encima.
                 font: pg.font.Font = None, # Fuente para el texto.
                 caption: str = None, # Texto del boton.
                 border: int = 0, # Grosor del borde (0 = sin borde).
                 color_border: Tuple[int, int, int] = None, # Color del borde.
                 radius: int = 0 # Radio de las esquinas.
                 ) -> None:
        # Datos del boton.
        self.rect: pg.Rect = pg.Rect(x, y, w, h)
        self.color_bg: Tuple[int, int, int] = color_bg
        self.color_fg: Tuple[int, int, int] = color_fg
        self.color_select: Tuple[int, int, int] = color_select
        self.radius: int = radius

        # Configurar borde si se proporciona.
        if border > 0 and color_border != None:
            self.border = border
            self.color_border: Tuple[int, int, int] = color_border
        else:
            self.border = 0
            self.color_border: Tuple[int, int, int] = None

        # Configurar texto si se proporciona.
        if caption != None and font != None:
            self.caption: pg.Surface = font.render(caption, True, self.color_fg)
            self.caption_rect: pg.Rect = self.caption.get_rect()
            self.caption_rect.center = self.rect.center
        else:
            self.caption: pg.Surface = None
            self.caption_rect: pg.Rect = None

        # Variables de estado.
        self.is_hovered: bool = False
        self.is_clicked: bool = False

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja el fondo y el borde del boton.
        pg.draw.rect(surface, self.color_bg, self.rect, 0, border_radius = self.radius)

        if self.border > 0 and self.color_border != None:
            pg.draw.rect(surface, self.color_border, self.rect, 5, self.radius)

        # Dibuja el texto.
        if self.caption != None:
            surface.blit(self.caption, self.caption_rect)

        # Dibuja un borde de seleccion si el mouse esta encima.
        if self.is_hovered:
            pg.draw.rect(surface, self.color_select, self.rect, 5, self.radius)

    def update(self) -> None:
        # Actualiza el estado hover segun la posicion del mouse.
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def set_caption(self, new_caption: str, font: pg.font.Font):
        # Cambia el texto del boton.
        self.caption = font.render(new_caption, True, self.color_fg)
        self.caption_rect = self.caption.get_rect(center=self.rect.center)

class ButtonCustom():
    # Boton que usa dos imagenes (normal y hover).
    def __init__(self,
                 x,
                 y,
                 img_idle,
                 img_hovered
                 ) -> None:
        self.img_idle = img_idle
        self.img_hovered = img_hovered
        self.rect = img_idle
        self.rect.topleft = (x, y)

        self.is_hovered = False
        self.is_pressed = False

    def update(self) -> None:
        # Actualiza el estado hover segun la posicion del mouse.
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.is_hovered = True
        else:
            self.is_hovered = False