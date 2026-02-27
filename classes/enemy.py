# Modulos de python.
import sys
import math

# Modulos de pygame.
import pygame as pg
from pygame.locals import *
from pygame.math import Vector2
from utils import constants as c

# Modulos custom.

class HealthBar():
    # Barra de vida para una entidad.
    def __init__(self,
                 x, # posicion en x de la barra de vida
                 y, # posicion en y de la barra de vida
                 w, # ancho de la barra de vida
                 h, # alto de la barra de vida
                 max_hp # Vida maxima de la entidad
                 ) -> None:
        # Inicializa la posicion y dimensiones de la barra.
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

    def draw(self, surface) -> None:
        # Dibuja la barra de vida (fondo rojo, vida actual verde).
        ratio = self.hp/self.max_hp
        pg.draw.rect(surface, c.COLOUR_RED, (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, c.COLOUR_GREEN, (self.x, self.y, self.w * ratio, self.h))

class Enemy(pg.sprite.Sprite):
    # Representa un enemigo que se mueve a lo largo de una ruta.
    def __init__(self,
                 waypoints, # lista de puntos (x,y) que forman la ruta
                 image,     # imagen del enemigo
                 health,    # vida maxima del enemigo
                 speed,     # velocidad de movimiento
                 on_escape=None # funcion a llamar cuando el enemigo escapa
                 ) -> None:
        # Inicializar la clase padre.
        pg.sprite.Sprite.__init__(self)

        # Parametros.
        self.waypoints = waypoints
        self.pos = Vector2(waypoints[0])
        self.speed = speed
        self.target_waypoint = 1
        self.angle = 0
        self.original_image = image
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos)

        self.max_health = health
        self.current_health = health
        self.health_bar = HealthBar(self.rect.centerx - 17, self.rect.top + 5, 35, 5, self.max_health)
        self.on_escape = on_escape

    def update(self, dt: float) -> None:
        # Actualiza el movimiento, rotacion y barra de vida.
        self.move(dt)
        self.rotate()

        self.health_bar.hp = self.current_health

    def move(self, dt: float):
        # Mueve al enemigo hacia el siguiente punto de ruta.
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            # Llego al final del camino.
            if self.on_escape:
                self.on_escape()
            self.kill()

        # Distancia restante hasta el objetivo.
        dist = self.movement.length()

        # Si la distancia es mayor que la velocidad, avanza normalmente.
        if dist >= self.speed * dt:
            self.pos += self.movement.normalize() * self.speed * dt
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1

        self.rect.center = self.pos

        # Actualiza la posicion de la barra de vida.
        self.health_bar.x = self.rect.centerx - 17
        self.health_bar.y = self.rect.top + 5

    def rotate(self):
        # Calcula el angulo hacia el siguiente punto y rota la imagen.
        dist = self.target - self.pos
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect  = self.image.get_rect()
        self.rect.center = self.pos