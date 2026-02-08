# Modulos de python.
import sys
from typing import List, Dict
import json

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button
from classes.level import Level
from classes.turret import Turret
from classes.enemy import Enemy

from utils import constants as c

class TowerDefence(State):
    def __init__(self, parent_state_machine, level: str) -> None:
        # Referencia a la state machine que llamara a este estado
        self.parent_state_machine = parent_state_machine

        # Cargas datos del mapa.
        if level == "level1":
            with open("assets/levels/level1.tmj") as file:
                level_data = json.load(file)                
            level_img  = pg.image.load("assets/levels/level1.png")
            select_img = pg.image.load("assets/levels/select_tile.png")

        # Crear mapa.
        self.level = Level(level_img, level_data, select_img)

        # Cargar texturas
        self.turret1_img = pg.image.load("assets/turrets/turret1.png")
        self.enemy1_img = pg.image.load("assets/enemies/enemy1.png")

        # Crear grupos de enemigos y torretas.
        self.turret_group = pg.sprite.Group()
        self.enemy_group  = pg.sprite.Group()

        # Elementos de la interfaz.
        self.sidebar_img = pg.image.load("assets/levels/sidebar.png")
        self.sidebar_rect = self.sidebar_img.get_rect()
        self.sidebar_rect.topleft = ((self.level.w) * c.TILE_SIZE, 0)

        # Imagen para resaltar la casilla por la que esta pasando el cursor.
        self.highlight_hover = pg.surface.Surface((c.TILE_SIZE, c.TILE_SIZE), SRCALPHA)
        self.highlight_hover.fill((255, 255, 255, 100))
        self.highlight_hover_rect = pg.Rect((0, 0), (c.TILE_SIZE, c.TILE_SIZE))

        # Posicion del cursor.
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_posx = self.mouse_pos[0] // c.TILE_SIZE # Posicion en casillas.
        self.mouse_posy = self.mouse_pos[1] // c.TILE_SIZE

        # DEBUG
        self.enemy_group.add(Enemy(self.level.waypoints, self.enemy1_img))

    def handle_events(self, events: List[pg.event.Event]) -> None:
        for event in events:
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    # Determina si el raton esta en el area del mapa.
                    if self.mouse_posx < self.level.w:
                        if self.level.tiles[self.mouse_posy * 20 + self.mouse_posx] == 43:
                            self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                        else:
                            self.level.selected_tile = None
            elif event.type == KEYUP:
                # DEBUG
                if event.key == K_F1:
                    if self.level.selected_tile != None:
                        self.turret_group.add(Turret(self.turret1_img,
                                                     self.level.selected_tile[0],
                                                     self.level.selected_tile[1]))
                elif event.key == K_ESCAPE:
                    self.level.selected_tile = None
                    
        
    def update(self, dt: float) -> None:
        # Actualizar posicion del cursor.
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_posx = self.mouse_pos[0] // c.TILE_SIZE
        self.mouse_posy = self.mouse_pos[1] // c.TILE_SIZE

        # Actualizar logica de los enemigos.
        self.enemy_group.update(dt) 
        
        # Actualizar logica de la torretas.
        same_location = False
        for turret in self.turret_group:
            turret.update(self.enemy_group, dt)

            # Determinar si la casilla seleccionada tiene una torreta.
            if self.level.selected_tile != None:
                if (self.level.selected_tile[0] == turret.tile_x and
                    self.level.selected_tile[1] == turret.tile_y):
                    same_location = True

                    # Mostrar rango de la torreta si la casilla seleccionada es la misma.
                    turret.show_range = True
                else:
                    turret.show_range = False
            else:
                turret.show_range = False
        print(1 / dt)

        
    def draw(self, surface: pg.Surface) -> None:

        # Dibujar imagen de fondo.
        self.level.draw(surface)
        surface.blit(self.sidebar_img, self.sidebar_rect)

        # Dibujar torretas colocadas.
        for turret in self.turret_group:
            turret.draw(surface)

        # Dibujar enemigos.
        self.enemy_group.draw(surface)

        # DEBUG
        pg.draw.lines(surface, (245, 245, 245), False, self.level.waypoints)
        
        self.level.draw_overlay(surface)

        # Resaltar casilla donde este ubicado el cursor.
        if self.mouse_posx < self.level.w:
            if self.level.tiles[(self.mouse_posy * 20) + self.mouse_posx] == 43:
                self.highlight_hover_rect.topleft = (c.TILE_SIZE * self.mouse_posx,
                                                c.TILE_SIZE * self.mouse_posy)
                surface.blit(self.highlight_hover, self.highlight_hover_rect)

    def optimize_images(self):
        self.level.image = self.level.image.convert()
        self.level.select_tile_img = self.level.select_tile_img.convert_alpha()
        self.turret1_img = self.turret1_img.convert_alpha()
        self.enemy1_img = self.enemy1_img.convert_alpha()
        self.sidebar_img = self.sidebar_img.convert()

    
