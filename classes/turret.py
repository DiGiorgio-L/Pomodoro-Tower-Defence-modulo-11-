# -*- coding: latin-1 -*-

# Python modules
import sys
import math
from typing import List, Dict

# Pygame modules
import pygame as pg
from pygame.locals import *

# Custom modules
from utils import constants as c
from data.turret_data import TURRET_DATA

class Turret(pg.sprite.Sprite):
    def __init__(self,
                 image: pg.Surface,
                 tile_x: int,
                 tile_y: int,
                 type: str,
                 sound_manager) -> None:
        # Inicializar clase padre Sprite
        pg.sprite.Sprite.__init__(self)
        self.sound_manager = sound_manager

        # Parametros basicos de la torreta.
        self.type = type
        self.level_limit = 2 # Limite superior inclusivo de nivel de la torreta.
        self.level = 1 # Nivel de la torre, se usa para asignar sus estadísticas.
        self.splash_radius = TURRET_DATA[self.type][self.level - 1]["splash_radius"]
        self.range = TURRET_DATA[self.type][self.level - 1]["range"] # Rango de la torre.
        self.damage = TURRET_DATA[self.type][self.level -1]["damage"]
        self.cooldown = TURRET_DATA[self.type][self.level - 1]["cooldown"] # Cadencia de disparo.
        self.last_shot = pg.time.get_ticks() # Tiempo de juego al momento del último disparo.
        self.target = None # Objetivo de la torreta.

        # Localizacion de la torreta en casillas.
        self.tile_x = tile_x
        self.tile_y = tile_y

        # Localizacion de la torreta en pixeles.
        self.x = (tile_x + 0.5) * c.TILE_SIZE
        self.y = (tile_y + 0.5) * c.TILE_SIZE

        # Datos del sprite.
        self.angle = 90 # Angulo de la torreta.
        self.image = image # Imagen original de la torreta.
        
        # Imagen rotada de la torreta; usada para renderizar.
        self.rotated_image = pg.transform.rotate(self.image, self.angle)
        self.rect = image.get_rect() # Rectangulo de la imagen.
        self.rect.center = (self.x, self.y)

        # Datos del rango de la torreta.
        self.show_range = False # Verdadero si se deberia mostrar el rango de la torre.
        
        # NOTA: se multiplica por 2 para tomar en cuenta que el rango parte desde el centro
        # y se extiende en todas direcciones; sera un circulo.
        self.range_img = pg.Surface((self.range * 2, self.range * 2))

        # Crear imagen transparente para mostrar el rango de la torreta.
        self.range_img.fill((0, 0, 0))
        self.range_img.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_img, (245, 245, 245), (self.range, self.range), self.range)
        self.range_img.set_alpha(75)
        self.range_rect = self.range_img.get_rect()
        self.range_rect.center = self.rect.center

    def update(self, enemy_group, dt: float) -> None:
        if self.target != None:
            x_dist = self.target.pos[0] - self.x
            y_dist = self.target.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)            
            if dist < self.range:
                if (pg.time.get_ticks() - self.last_shot) > self.cooldown:
                    self.shoot_to_target(enemy_group)
            else:
                self.target = None
                print("Target lost!")

            self.angle = math.degrees(math.atan2(-y_dist, x_dist))
        else:
            self.pick_target(enemy_group)
            if self.target:
                if pg.time.get_ticks() - self.last_shot > self.cooldown:
                    self.shoot_to_target(enemy_group)

    def shoot_to_target(self, enemy_group) -> None:
        self.last_shot = pg.time.get_ticks()
        # Daño al objetivo principal
        self.target.current_health -= self.damage
        # Daño en área si corresponde
        if self.splash_radius > 0 and self.target is not None:
            for enemy in enemy_group:
                if enemy != self.target:
                    dist = math.hypot(enemy.pos[0] - self.target.pos[0],
                                      enemy.pos[1] - self.target.pos[1])
                    if dist < self.splash_radius:
                        enemy.current_health -= self.damage
        # Comprobar si el objetivo murió
        if self.target.current_health <= 0:
            self.target = None
        print("Shot!")
        if self.type == "shortbow":
            self.sound_manager.play_sound("bow_shot")
        elif self.type == "longbow":
            self.sound_manager.play_sound("longbow_shot")
        elif self.type == "mortar":
            if self.splash_radius > 0:
                self.sound_manager.play_sound("mortar_explosion")

    def pick_target(self, enemy_group):
        # Buscar un enemigo al que disparar.
        x_dist = 0
        y_dist = 0
        dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
        # Comprobar distancia hasta cada enemigo y determinar si este en rango.
        for enemy in enemy_group:
            x_dist = enemy.pos[0] - self.x
            y_dist = enemy.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < self.range:
                self.target = enemy
                print("New target locked!")

    def draw(self, surface):
        self.rotated_image = pg.transform.rotate(self.image, self.angle - 90)
        self.rect = self.rotated_image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.rotated_image, self.rect)

        if self.show_range:
            surface.blit(self.range_img, self.range_rect)

    def get_upgrade_cost(self):
        if self.level < self.level_limit:
            # El siguiente nivel tiene índice self.level (porque level empieza en 1)
            next_level_data = TURRET_DATA[self.type][self.level]
            return next_level_data.get("upgrade_cost", 0)
        return None
            
    def upgrade(self):
        # Si esta dentro del limite, subir de nivel.
        if self.level < self.level_limit:
            self.level += 1
            self.range = TURRET_DATA[self.type][self.level - 1]["range"]
            self.cooldown = TURRET_DATA[self.type][self.level - 1]["cooldown"]
            self.damge = TURRET_DATA[self.type][self.level - 1]["damage"]
            self.splash_radius = TURRET_DATA[self.type][self.level - 1]["splash_radius"]

            # Actualizar imagen de rango de la torreta.
            self.range_img = pg.Surface((self.range * 2, self.range * 2))
            self.range_img.fill((0, 0, 0))
            self.range_img.set_colorkey((0, 0, 0))
            pg.draw.circle(self.range_img, (245, 245, 245), (self.range, self.range), self.range)
            self.range_img.set_alpha(75)
            self.range_rect = self.range_img.get_rect()
            self.range_rect.center = self.rect.center

