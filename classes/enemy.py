# Modulos de python.
import sys
import math

# Modulos de pygame.
import pygame as pg
from pygame.locals import *
from pygame.math import Vector2
from utils import constants as c

# Modulos custom

class HealthBar():
    def __init__(self,
                 x, # posicion en x de la barra de vida
                 y, # posicion en y de la barra de vida
                 w, # ancho de la barra de vida
                 h, #  alto de la barra de vida
                 max_hp # Vida maxima de la entidad
                 ) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

    def draw(self, surface) -> None:
        ratio = self.hp/self.max_hp
        pg.draw.rect(surface, c.COLOUR_RED, (self.x, self.y, self.w, self.h))
        pg.draw.rect(surface, c.COLOUR_GREEN, (self.x, self.y, self.w * ratio, self.h))
    
class Enemy(pg.sprite.Sprite):
    def __init__(self,
                 waypoints,
                 image,
                 health,
                 speed,
                 on_escape=None
                 ) -> None:
        # Inicializar la clase padre.
        pg.sprite.Sprite.__init__(self)

        # Parametros.
        self.waypoints = waypoints # Puntos de ruta del enemigo.
        self.pos = Vector2(waypoints[0]) # Posicion del enemigo; inicia en el comienzo de la ruta.
        self.speed = speed # Velocidad del enemigo; multiplicar por delta time.
        self.target_waypoint = 1 # Indice del punto de ruta objetivo.
        self.angle = 0 # Angulo de la imagen del enemigo.
        self.original_image = image # Imagen original.
        self.image = pg.transform.rotate(self.original_image, self.angle) # Image rotada.
        self.rect = self.image.get_rect() # Rectangulo de la image; usado para dibujar.
        self.rect.center = (self.pos)
        
        self.max_health = health
        self.current_health = health
        self.health_bar = HealthBar(self.rect.centerx - 17, self.rect.top + 5, 35, 5, self.max_health)
        self.on_escape = on_escape

    def update(self, dt: float) -> None:
        self.move(dt)
        self.rotate()

        self.health_bar.hp = self.current_health

    def move(self, dt: float):
        if self.target_waypoint < len(self.waypoints):
            self.target = Vector2(self.waypoints[self.target_waypoint])
            self.movement = self.target - self.pos
        else:
            # Enemy has reached the end of the path
            if self.on_escape:
                self.on_escape()
            self.kill()

        # Calculate distance remaining before target
        dist = self.movement.length()

        # Check if remaining distance is greater than the enemy speed
        if dist >= self.speed * dt:
            self.pos += self.movement.normalize() * self.speed * dt
        else:
            if dist != 0:
                self.pos += self.movement.normalize() * dist
            self.target_waypoint += 1
            
        self.rect.center = self.pos
        
        self.health_bar.x = self.rect.centerx - 17
        self.health_bar.y = self.rect.top + 5

    def rotate(self):
        # Calculate distance to next waypoint
        dist = self.target - self.pos

        # Use distance to calculate angle
        self.angle = math.degrees(math.atan2(-dist[1], dist[0]))

        # Rotate image
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect  = self.image.get_rect()
        self.rect.center = self.pos
