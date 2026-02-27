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
    # Representa una torreta que dispara a los enemigos.
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
        self.level_limit = 2 # Nivel maximo (inclusive).
        self.level = 1
        self.splash_radius = TURRET_DATA[self.type][self.level - 1]["splash_radius"]
        self.range = TURRET_DATA[self.type][self.level - 1]["range"]
        self.damage = TURRET_DATA[self.type][self.level -1]["damage"]
        self.cooldown = TURRET_DATA[self.type][self.level - 1]["cooldown"]
        self.last_shot = pg.time.get_ticks()
        self.target = None

        # Localizacion en casillas.
        self.tile_x = tile_x
        self.tile_y = tile_y

        # Localizacion en pixeles.
        self.x = (tile_x + 0.5) * c.TILE_SIZE
        self.y = (tile_y + 0.5) * c.TILE_SIZE

        # Datos del sprite.
        self.angle = 90
        self.image = image
        self.rotated_image = pg.transform.rotate(self.image, self.angle)
        self.rect = image.get_rect()
        self.rect.center = (self.x, self.y)

        # Datos del rango de la torreta.
        self.show_range = False
        # Crear superficie para mostrar el rango.
        self.range_img = pg.Surface((self.range * 2, self.range * 2))
        self.range_img.fill((0, 0, 0))
        self.range_img.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_img, (245, 245, 245), (self.range, self.range), self.range)
        self.range_img.set_alpha(75)
        self.range_rect = self.range_img.get_rect()
        self.range_rect.center = self.rect.center

    def update(self, enemy_group, dt: float) -> None:
        # Actualiza el objetivo y dispara si es posible.
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
        # Dispara al objetivo, aplica daño y daño en area si corresponde.
        self.last_shot = pg.time.get_ticks()
        self.target.current_health -= self.damage
        if self.splash_radius > 0 and self.target is not None:
            for enemy in enemy_group:
                if enemy != self.target:
                    dist = math.hypot(enemy.pos[0] - self.target.pos[0],
                                      enemy.pos[1] - self.target.pos[1])
                    if dist < self.splash_radius:
                        enemy.current_health -= self.damage
        if self.target.current_health <= 0:
            self.target = None
        print("Shot!")
        # Reproducir sonido segun el tipo.
        if self.type == "shortbow":
            self.sound_manager.play_sound("bow_shot")
        elif self.type == "longbow":
            self.sound_manager.play_sound("longbow_shot")
        elif self.type == "mortar":
            if self.splash_radius > 0:
                self.sound_manager.play_sound("mortar_explosion")

    def pick_target(self, enemy_group):
        # Busca un enemigo dentro del rango y lo asigna como objetivo.
        x_dist = 0
        y_dist = 0
        dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
        for enemy in enemy_group:
            x_dist = enemy.pos[0] - self.x
            y_dist = enemy.pos[1] - self.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < self.range:
                self.target = enemy
                print("New target locked!")

    def draw(self, surface):
        # Dibuja la torreta rotada y opcionalmente el rango.
        self.rotated_image = pg.transform.rotate(self.image, self.angle - 90)
        self.rect = self.rotated_image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.rotated_image, self.rect)

        if self.show_range:
            surface.blit(self.range_img, self.range_rect)

    def get_upgrade_cost(self):
        # Devuelve el costo de mejora para el siguiente nivel, o None si no hay.
        if self.level < self.level_limit:
            next_level_data = TURRET_DATA[self.type][self.level]
            return next_level_data.get("upgrade_cost", 0)
        return None

    def upgrade(self):
        # Sube de nivel la torreta y actualiza sus estadisticas.
        if self.level < self.level_limit:
            self.level += 1
            self.range = TURRET_DATA[self.type][self.level - 1]["range"]
            self.cooldown = TURRET_DATA[self.type][self.level - 1]["cooldown"]
            self.damge = TURRET_DATA[self.type][self.level - 1]["damage"]
            self.splash_radius = TURRET_DATA[self.type][self.level - 1]["splash_radius"]

            # Actualizar imagen de rango.
            self.range_img = pg.Surface((self.range * 2, self.range * 2))
            self.range_img.fill((0, 0, 0))
            self.range_img.set_colorkey((0, 0, 0))
            pg.draw.circle(self.range_img, (245, 245, 245), (self.range, self.range), self.range)
            self.range_img.set_alpha(75)
            self.range_rect = self.range_img.get_rect()
            self.range_rect.center = self.rect.center