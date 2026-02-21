# Modulos de python.
import sys
from typing import Tuple

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from utils import constants as c

class TextBox():
    def __init__(self,
                 x: int,
                 y: int,
                 font: pg.font.Font,
                 caption: str,
                 color: Tuple[int, int, int]
                 ) -> None:

        self.caption: pg.Surface = font.render(caption, True, color)
        self.caption_rect: pg.Rect = self.caption.get_rect()
        self.caption_rect.topleft = (x, y)

    def draw(self, surface: pg.Surface) -> None:
        surface.blit(self.caption, self.caption_rect)

# Definicion de una clase para crear botones
class Button():
    def __init__(self,
                 x: int, # Coordenada en x de la esquina superior izquierda.
                 y: int, # Coordenada en y de la esquina superior izquierda.
                 w: int, # Ancho del boton.
                 h: int, # Alto del boton.
                 color_bg: Tuple[int, int, int], # Color para el fondo del boton.
                 color_fg: Tuple[int, int, int], # Color para el texto del boton.
                 color_select: Tuple[int, int, int], # Color para cuando el boton es seleccionado.
                 font: pg.font.Font = None, # Objeto que represente la fuenta a usar.
                 caption: str = None, # Texto que se ubicará en el centro del boton.
                 border: int = 0, # Grosor del borde. (por defecto, sin borde)
                 color_border: Tuple[int, int, int] = None, # Color para el borde del boton.
                 radius: int = 0 # Radio de las esquinas del boton.
                 ) -> None:
        
        # Datos del boton.
        self.rect: pg.Rect = pg.Rect(x, y, w, h)
        self.color_bg: Tuple[int, int, int] = color_bg
        self.color_fg: Tuple[int, int, int] = color_fg
        self.color_select: Tuple[int, int, int] = color_select
        self.radius: int = radius

        # Si han sido suministrados parametros para el borde.
        if border > 0 and color_border != None:
            self.border = border
            self.color_border: Tuple[int, int, int] = color_border
        else:
            self.border = 0
            self.color_border: Tuple[int, int, int] = None

        # Si han sido suministrados parametros para el texto del boton.
        if caption != None and font != None:
            self.caption: pg.Surface = font.render(caption, True, self.color_fg)
            self.caption_rect: pg.Rect = self.caption.get_rect()
            self.caption_rect.center = self.rect.center
        else:
            self.caption: pg.Surface = None
            self.caption_rect: pg.Rect = None

        # Variables de estado.
        self.is_hovered: bool = False # Verdadero si el puntero está sobre el area del boton.
        self.is_clicked: bool = False # Verdadero si el boton ha sido presionado.
        
    def draw(self, surface: pg.Surface) -> None:
        # Dibujar el fondo del boton.
        pg.draw.rect(surface, self.color_bg, self.rect, 0, border_radius = self.radius)

        if self.border > 0 and self.color_border != None:
            pg.draw.rect(surface, self.color_border, self.rect, 5, self.radius)
        
        # Dibujar texto del boton.
        if self.caption != None:
            surface.blit(self.caption, self.caption_rect)



        # Dibujar borde para mostrar que el puntero esta sobre el boton.
        
        if self.is_hovered:
            pg.draw.rect(surface, self.color_select, self.rect, 5, self.radius)

    def update(self) -> None:
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def set_caption(self, new_caption: str, font: pg.font.Font):
        self.caption = font.render(new_caption, True, self.color_fg)
        self.caption_rect = self.caption.get_rect(center=self.rect.center)

class ButtonCustom():
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
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.is_hovered = True
        else:
            self.is_hovered = False        
