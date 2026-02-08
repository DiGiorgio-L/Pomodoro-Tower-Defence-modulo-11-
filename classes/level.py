# Modulos de python.
import sys
from typing import List, Dict
import json

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from utils import constants as c

class Level():
    def __init__(self,
                 level_image, # Imagen que representa el nivel.
                 level_data,  # Datos del nivel. Resultado de llamar json.load().
                 select_tile_img # Imagen de selector de casilla
                 ) -> None:
        # Datos del mundo y casillas.
        self.data = level_data
        self.tiles = None

        # Imagenes.
        self.image = level_image
        self.select_tile_img = select_tile_img

        # Dimensiones del nivel en casillas.
        self.w = self.image.get_rect().right  // c.TILE_SIZE
        self.h = self.image.get_rect().bottom // c.TILE_SIZE

        # Puntos de control para el movimiento de los enemigos.
        self.waypoint_origin = None
        self.waypoints = []

        # Variables de estado del nivel.
        self.selected_tile = None # Contiene la posicion de la casilla seleccionada

        self.parse_data()
        
    def parse_data(self) -> None:
        for layer in self.data["layers"]:
            if layer["name"] == "Waypoints":
                for obj in layer["objects"]:
                    self.waypoints_origin = (obj.get("x"), obj.get("y"))
                    waypoints_data = obj["polyline"]
                    self.process_waypoints(waypoints_data)
            elif layer["name"] == "Tilemap":
                self.tiles = layer["data"]

    def process_waypoints(self, waypoints_data) -> None:
        original_x = self.waypoints_origin[0]
        original_y = self.waypoints_origin[1]
        for point in waypoints_data:
            temp_x = point.get("x")
            temp_y = point.get("y")
            self.waypoints.append((original_x + temp_x, original_y + temp_y))

    def draw(self, surface: pg.Surface) -> None:
        surface.blit(self.image, (0, 0))

    def draw_overlay(self, surface: pg.Surface) -> None:
        if self.selected_tile != None:
            surface.blit(self.select_tile_img,
                         (self.selected_tile[0] * c.TILE_SIZE,
                          self.selected_tile[1] * c.TILE_SIZE))
