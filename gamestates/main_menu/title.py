# Modulos de python.
import sys
from typing import List, Dict

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button
from utils import constants as c

class Title(State):
    # Pantalla de titulo con botones para nueva partida, cargar y cerrar.
    def __init__(self, buttons: Dict[str, Button],
                 images: Dict[str, pg.Surface],
                 parent_state_machine: StateMachine,
                 sound_manager) -> None:
        self.sound_manager = sound_manager
        self.buttons = buttons
        self.images = images
        self.parent_state_machine = parent_state_machine

    def handle_events(self, events: List[pg.event.Event]) -> None:
        # Procesa eventos de mouse.
        for event in events:
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    for button in self.buttons:
                        if self.buttons[button].is_hovered:
                            self.sound_manager.play_sound("click")
                            self.buttons[button].is_clicked = True
            elif event.type == KEYUP:
                if event.key == K_UP:
                    print("UP")

    def update(self, dt: float) -> None:
        # Actualiza botones y maneja clics.
        button_pressed: str = None
        for button in self.buttons:
            self.buttons[button].update()

            if self.buttons[button].is_clicked:
               self.buttons[button].is_clicked = False
               button_pressed = button
               break

        if button_pressed == "close":
            pg.event.post(pg.event.Event(pg.QUIT))
        elif button_pressed == "new_game":
            self.parent_state_machine.prev_state = "title"
            self.parent_state_machine.current_state = "load_game"
        elif button_pressed == "load_game":
            self.parent_state_machine.prev_state = "title"
            self.parent_state_machine.current_state = "load_game"
        elif button_pressed == "settings":
            self.parent_state_machine.prev_state = "title"
            self.parent_state_machine.current_state = "settings"

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja la pantalla de titulo.
        surface.blit(self.images["background"], (0, 0))
        surface.blit(self.images["container_centre"], (513, 0))
        surface.blit(self.images["pomodoro"], (368, 120))
        surface.blit(self.images["tower_defense"], (240, 155))

        # Dibujar botones.
        for button in self.buttons:
            self.buttons[button].draw(surface)