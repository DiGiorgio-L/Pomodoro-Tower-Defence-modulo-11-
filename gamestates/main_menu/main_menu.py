# Modulos de python.
import sys
from typing import List, Dict

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button
from gamestates.main_menu.title import Title
from gamestates.main_menu.load_game import LoadGame

from utils import constants as c

class MainMenu(State):
    def __init__(self, parent_state_machine) -> None:
        
        # Referenacia a la state machine que llamara a este estado
        self.parent_state_machine = parent_state_machine
        
        # Fuente para el texto
        font_pirata_one = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 23)
        font_pirata_one_big = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 50)
        
        # Cargar imagenes de la pantalla de titulo
        title_images: Dict[str, pg.Surface] = load_title_images()
        # Cargar botones de la pantalla de titulo
        title_buttons: Dict[str, Button] = load_title_buttons(font_pirata_one)

        # Crear state machine
        self.state_machine = StateMachine()

        # Instanciar estados de la maquina.
        title = Title(title_buttons, title_images, self.state_machine)
        load_game = LoadGame(self.state_machine, font_pirata_one, font_pirata_one_big, title_images["background"])

        # Agregar estados a la maquina.
        self.state_machine.add_state("title", title)
        self.state_machine.add_state("load_game", load_game)
        # self.state_machine.add_state("ajustes", ajustes)

        # Establecer estado inicial.
        self.state_machine.set_starting_state("title")

    def handle_events(self, events: List[pg.event.Event]) -> None:
        self.state_machine.handle_events(events)

    def update(self, dt: float) -> None:
        if self.state_machine.exit_state == None:
            self.state_machine.update(dt)
        elif self.state_machine.exit_state == "save1":
            # TODO: Necesito hacer que al cargar el juego también tome el
            # archivo de guardado a cargar.
            self.parent_state_machine.prev_state = self.parent_state_machine.current_state
            self.parent_state_machine.current_state = "tower_defence"
        elif self.state_machine.exit_state == "save2":
            # TODO: Necesito hacer que al cargar el juego también tome el
            # archivo de guardado a cargar.
            self.parent_state_machine.prev_state = self.parent_state_machine.current_state
            self.parent_state_machine.current_state = "tower_defence"
        elif self.state_machine.exit_state == "save3":
            # TODO: Necesito hacer que al cargar el juego también tome el
            # archivo de guardado a cargar.
            self.parent_state_machine.prev_state = self.parent_state_machine.current_state
            self.parent_state_machine.current_state = "tower_defence"
        else:
            self.parent_state_machine.terminate_machine(self.state_machine.exit_state)

    def draw(self, surface: pg.Surface) -> None:
        self.state_machine.draw(surface)


def load_title_buttons(font_text: pg.font.Font) -> Dict[str, Button]:
    title_buttons: Dict[str, Button] = {}
    title_buttons["new_game"] = Button(x = 552, y = 371, w = 177, h = 58,
                                       color_bg = c.COLOUR_BROWN,
                                       color_fg = c.COLOUR_CREAM,
                                       color_select = c.COLOUR_DARK_BROWN,
                                       font = font_text,
                                       caption = "Nueva Partida",
                                       radius = 6
                                       )
    title_buttons["load_game"] = Button(x = 552, y = 437, w = 177, h = 58,
                                        color_bg = c.COLOUR_BROWN,
                                        color_fg = c.COLOUR_CREAM,
                                        color_select = c.COLOUR_DARK_BROWN,
                                        font = font_text,
                                        caption = "Cargar Partida",
                                        radius = 6
                                        )
    title_buttons["settings"] = Button(x = 552, y = 503, w = 177, h = 58,
                                       color_bg = c.COLOUR_BROWN,
                                       color_fg = c.COLOUR_CREAM,
                                       color_select = c.COLOUR_DARK_BROWN,
                                       font = font_text,
                                       caption = "Ajustes",
                                       radius = 6
                                       )
    title_buttons["close"] = Button(x = 552, y = 567, w = 177, h = 58,
                                    color_bg = c.COLOUR_BROWN,
                                    color_fg = c.COLOUR_CREAM,
                                    color_select = c.COLOUR_DARK_BROWN,
                                    font = font_text,
                                    caption = "Cerrar",
                                    radius = 6
                                    )
    return title_buttons

def load_title_images() -> Dict[str, pg.Surface]:
    title_images: Dict[str, pg.Surface] = {}
    title_images["background"] = pg.image.load("assets/main_menu/main_menu_bg.png")
    title_images["container_centre"] = pg.image.load("assets/main_menu/container_centre.png")
    title_images["title"] = None
    
    return title_images
