# Modulos de python.
import sys, json
from typing import List, Dict
from pathlib import Path

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button
from gamestates.main_menu.title import Title
from gamestates.main_menu.load_game import LoadGame
from gamestates.town.town import Town

from utils import constants as c
from config import FONTS_DIR, MAIN_MENU_DIR, SAVE_DIR

class MainMenu(State):
    # Estado principal del menu, contiene sub-estados como title y load_game.
    def __init__(self, parent_state_machine, sound_manager) -> None:
        self.sound_manager = sound_manager
        self.parent_state_machine = parent_state_machine

        # Fuente para el texto.
        font_pirata_one = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 23)
        font_pirata_one_big = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 50)

        # Cargar imagenes de la pantalla de titulo.
        title_images: Dict[str, pg.Surface] = load_title_images()
        # Cargar botones de la pantalla de titulo.
        title_buttons: Dict[str, Button] = load_title_buttons(font_pirata_one)

        # Crear state machine interna.
        self.state_machine = StateMachine()

        # Instanciar estados de la maquina.
        title = Title(title_buttons, title_images, self.state_machine, self.sound_manager)
        load_game = LoadGame(self.state_machine, font_pirata_one, font_pirata_one_big,
                             title_images["background"], title_images["pomodoro"],
                             title_images["tower_defense"], self.sound_manager)

        # Agregar estados a la maquina.
        self.state_machine.add_state("title", title)
        self.state_machine.add_state("load_game", load_game)

        # Establecer estado inicial.
        self.state_machine.set_starting_state("title")

    def handle_events(self, events: List[pg.event.Event]) -> None:
        # Pasa eventos a la sub-maquina.
        self.state_machine.handle_events(events)

    def update(self, dt: float) -> None:
        # Actualiza la sub-maquina y maneja la salida hacia el pueblo.
        if self.state_machine.exit_state == None:
            self.state_machine.update(dt)
        elif self.state_machine.exit_state == "save1":
            slot = 1
            save_path = SAVE_DIR / f"save{slot}.json"
            if save_path.exists():
                with save_path.open('r') as f:
                    save_data = json.load(f)
            else:
                save_data = None

            town_state = Town(self.parent_state_machine, save_data=save_data, save_slot=slot, sound_manager=self.sound_manager)
            self.parent_state_machine.add_state("town", town_state)
            self.parent_state_machine.current_state = "town"
            self.state_machine.exit_state = None
            self.state_machine.current_state = "title"

        elif self.state_machine.exit_state == "save2":
            slot = 2
            save_path = SAVE_DIR / f"save{slot}.json"
            if save_path.exists():
                with save_path.open('r') as f:
                    save_data = json.load(f)
            else:
                save_data = None

            town_state = Town(self.parent_state_machine, save_data=save_data, save_slot=slot, sound_manager=self.sound_manager)
            self.parent_state_machine.add_state("town", town_state)
            self.parent_state_machine.current_state = "town"
            self.state_machine.exit_state = None
            self.state_machine.current_state = "title"

        elif self.state_machine.exit_state == "save3":
            slot = 3
            save_path = SAVE_DIR / f"save{slot}.json"
            if save_path.exists():
                with save_path.open('r') as f:
                    save_data = json.load(f)
            else:
                save_data = None

            town_state = Town(self.parent_state_machine, save_data=save_data, save_slot=slot, sound_manager=self.sound_manager)
            self.parent_state_machine.add_state("town", town_state)
            self.parent_state_machine.current_state = "town"
            self.state_machine.exit_state = None
            self.state_machine.current_state = "title"

        else:
            self.parent_state_machine.terminate_machine(self.state_machine.exit_state)

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja el estado actual de la sub-maquina.
        self.state_machine.draw(surface)

def load_title_buttons(font_text: pg.font.Font) -> Dict[str, Button]:
    # Crea los botones para la pantalla de titulo.
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
    title_buttons["close"] = Button(x = 552, y = 503, w = 177, h = 58,
                                    color_bg = c.COLOUR_BROWN,
                                    color_fg = c.COLOUR_CREAM,
                                    color_select = c.COLOUR_DARK_BROWN,
                                    font = font_text,
                                    caption = "Cerrar",
                                    radius = 6
                                    )
    return title_buttons

def load_title_images() -> Dict[str, pg.Surface]:
    # Carga las imagenes necesarias para la pantalla de titulo.
    title_images: Dict[str, pg.Surface] = {}
    title_images["background"] = pg.image.load(str(MAIN_MENU_DIR / "main_menu_bg.png"))
    title_images["container_centre"] = pg.image.load(str(MAIN_MENU_DIR / "container_centre.png"))
    title_images["title"] = None
    title_images["pomodoro"] = pg.image.load(str(MAIN_MENU_DIR / "pomodoro.png"))
    title_images["tower_defense"] = pg.image.load(str(MAIN_MENU_DIR / "tower_defense.png"))

    return title_images