# Modulos de python.
import sys
from typing import List, Dict

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button, TextBox
from utils import constants as c

class LoadGame(State):
    def __init__(self, parent_state_machine, font, font_big, background) -> None:
        self.parent_state_machine = parent_state_machine


        self.text_items: List[TextBox] = []
        
        load_text = TextBox(511, 75, font_big, "Cargar Partida", c.COLOUR_CREAM)
        self.text_items.append(load_text)
        
        save1_text = TextBox(0, 0, font, "Archivo 1", c.COLOUR_BLACK)
        save1_text.caption_rect.center = (332, 215)
        self.text_items.append(save1_text)
        
        save2_text = TextBox(0, 0, font, "Archivo 2", c.COLOUR_BLACK)
        save2_text.caption_rect.center = (640, 215)
        self.text_items.append(save2_text)
        
        save3_text = TextBox(0, 0, font, "Archivo 3", c.COLOUR_BLACK)
        save3_text.caption_rect.center = (948, 215)
        self.text_items.append(save3_text)
        
        # Cargar botones
        self.buttons: Dict[str, Button] = {}
        self.buttons["save1"] = Button(x = 185, y = 183, w = 294, h = 418,
                                       color_bg = c.COLOUR_CREAM,
                                       color_fg = c.COLOUR_BLACK,
                                       color_select = c.COLOUR_BROWN,
                                       font = None,
                                       caption = None,
                                       border = 0,
                                       color_border = None, 
                                       radius = 0
                                       )
        self.buttons["save2"] = Button(x = 493, y = 183, w = 294, h = 418,
                                       color_bg = c.COLOUR_CREAM,
                                       color_fg = c.COLOUR_BLACK,
                                       color_select = c.COLOUR_BROWN,
                                       font = None,
                                       caption = None,
                                       border = 0,
                                       color_border = None, 
                                       radius = 0
                                       )
        self.buttons["save3"] = Button(x = 801, y = 183, w = 294, h = 418,
                                       color_bg = c.COLOUR_CREAM,
                                       color_fg = c.COLOUR_BLACK,
                                       color_select = c.COLOUR_BROWN,
                                       font = None,
                                       caption = None,
                                       border = 0,
                                       color_border = None, 
                                       radius = 0
                                       )
        self.buttons["return"] = Button(x = 10, y = 10, w = 177, h = 58,
                                       color_bg = c.COLOUR_BROWN,
                                       color_fg = c.COLOUR_CREAM,
                                       color_select = c.COLOUR_DARK_BROWN,
                                       font = font,
                                       caption = "Volver",
                                       border = 0,
                                       color_border = None, 
                                       radius = 0
                                       )

        self.background: pg.Surface = background
        self.mask: pg.Surface = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), SRCALPHA)
        self.mask.fill(c.COLOUR_BLACK)
        self.mask.set_alpha(150)

    def handle_events(self, events: List[pg.event.Event]) -> None:
        for event in events:
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    for button in self.buttons:
                        if self.buttons[button].is_hovered:
                            self.buttons[button].is_clicked = True
            elif event.type == KEYUP:
                pass

    def update(self, dt: float) -> None:
        button_pressed: str = None
        for button in self.buttons:
            self.buttons[button].update()

            if self.buttons[button].is_clicked:
                self.buttons[button].is_clicked = False
                button_pressed = button
                break

        if button_pressed == "return":
            self.parent_state_machine.prev_state = "load_game"
            self.parent_state_machine.current_state = "title"
        elif button_pressed == "save1" or button_pressed == "save2" or button_pressed == "save3":
            self.parent_state_machine.prev_state = "load_game"
            self.parent_state_machine.terminate_machine(button_pressed)

    def draw(self, surface: pg.Surface) -> None:
        surface.blit(self.background, (0, 0))
        surface.blit(self.mask, (0, 0))
        
        for button in self.buttons:
            self.buttons[button].draw(surface)

        for text in self.text_items:
            text.draw(surface)
