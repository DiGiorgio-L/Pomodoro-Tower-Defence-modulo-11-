# -*- coding: latin-1 -*-
import json
from typing import List, Dict
import pygame as pg
from pygame.locals import *
from classes.state_machine import State, StateMachine
from classes.gui import Button, TextBox
from utils import constants as c
from config import SAVE_DIR

class LoadGame(State):
    # Estado para cargar una partida desde uno de los tres slots.
    def __init__(self, parent_state_machine, font, font_big, background, text1, text2, sound_manager) -> None:
        self.sound_manager = sound_manager
        self.parent_state_machine = parent_state_machine

        self.text_items: List[TextBox] = []

        load_text = TextBox(511, 75, font_big, "Cargar Partida", c.COLOUR_CREAM)
        self.text_items.append(load_text)

        # Textos de titulo para cada archivo
        save1_text = TextBox(0, 0, font, "Archivo 1", c.COLOUR_BLACK)
        save1_text.caption_rect.center = (332, 215)
        self.text_items.append(save1_text)

        save2_text = TextBox(0, 0, font, "Archivo 2", c.COLOUR_BLACK)
        save2_text.caption_rect.center = (640, 215)
        self.text_items.append(save2_text)

        save3_text = TextBox(0, 0, font, "Archivo 3", c.COLOUR_BLACK)
        save3_text.caption_rect.center = (948, 215)
        self.text_items.append(save3_text)

        self.text1 = text1
        self.text2 = text2

        # Botones para cada slot y el de regresar.
        self.buttons: Dict[str, Button] = {}
        self.buttons["save1"] = Button(x = 185, y = 183, w = 294, h = 418,
                                       color_bg = c.COLOUR_CREAM,
                                       color_fg = c.COLOUR_BLACK,
                                       color_select = c.COLOUR_BROWN,
                                       font = None,
                                       caption = None,
                                       border = 0,
                                       color_border = None,
                                       radius = 0)
        self.buttons["save2"] = Button(x = 493, y = 183, w = 294, h = 418,
                                       color_bg = c.COLOUR_CREAM,
                                       color_fg = c.COLOUR_BLACK,
                                       color_select = c.COLOUR_BROWN,
                                       font = None,
                                       caption = None,
                                       border = 0,
                                       color_border = None,
                                       radius = 0)
        self.buttons["save3"] = Button(x = 801, y = 183, w = 294, h = 418,
                                       color_bg = c.COLOUR_CREAM,
                                       color_fg = c.COLOUR_BLACK,
                                       color_select = c.COLOUR_BROWN,
                                       font = None,
                                       caption = None,
                                       border = 0,
                                       color_border = None,
                                       radius = 0)
        self.buttons["return"] = Button(x = 10, y = 10, w = 177, h = 58,
                                       color_bg = c.COLOUR_BROWN,
                                       color_fg = c.COLOUR_CREAM,
                                       color_select = c.COLOUR_DARK_BROWN,
                                       font = font,
                                       caption = "Volver",
                                       border = 0,
                                       color_border = None,
                                       radius = 0)

        self.font = font
        self.font_big = font_big

        # Botones de eliminar para cada slot.
        self.delete_buttons = {}
        delete_size = 30
        for slot in ["save1", "save2", "save3"]:
            btn_rect = self.buttons[slot].rect
            x = btn_rect.right - delete_size - 5
            y = btn_rect.top + 5
            self.delete_buttons[slot] = Button(
                x, y, delete_size, delete_size,
                c.COLOUR_RED, c.COLOUR_WHITE, c.COLOUR_DARK_BROWN,
                self.font, "X", radius=3
            )

        self.background: pg.Surface = background
        self.mask: pg.Surface = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), SRCALPHA)
        self.mask.fill(c.COLOUR_BLACK)
        self.mask.set_alpha(150)

        # Cargar datos de los archivos de guardado.
        self.saves_data = {}
        for i in range(1, 4):
            slot = f"save{i}"
            path = SAVE_DIR / f"{slot}.json"
            if path.exists():
                with path.open('r') as f:
                    data = json.load(f)
                self.saves_data[slot] = data
            else:
                self.saves_data[slot] = None

    def handle_events(self, events: List[pg.event.Event]) -> None:
        # Procesa eventos del mouse y teclado.
        for event in events:
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    # Botones de eliminar.
                    for slot, btn in self.delete_buttons.items():
                        if btn.is_hovered:
                            self.sound_manager.play_sound("click")
                            path = SAVE_DIR / f"{slot}.json"
                            if path.exists():
                                path.unlink()
                                self.saves_data[slot] = None
                            return

                    # Botones de slot y regresar.
                    for button in self.buttons:
                        if self.buttons[button].is_hovered:
                            self.sound_manager.play_sound("click")
                            self.buttons[button].is_clicked = True
            elif event.type == KEYUP:
                pass

    def update(self, dt: float) -> None:
        # Actualiza los datos de los slots y maneja clics en botones.
        self.refresh_saves()
        button_pressed: str = None
        for button in self.buttons:
            self.buttons[button].update()

            if self.buttons[button].is_clicked:
                self.buttons[button].is_clicked = False
                button_pressed = button
                break

        # Actualizar botones de eliminar.
        for btn in self.delete_buttons.values():
            btn.update()

        if button_pressed == "return":
            self.parent_state_machine.prev_state = "load_game"
            self.parent_state_machine.current_state = "title"
        elif button_pressed in ["save1", "save2", "save3"]:
            self.parent_state_machine.prev_state = "load_game"
            self.parent_state_machine.terminate_machine(button_pressed)

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja la interfaz de carga.
        surface.blit(self.background, (0, 0))
        surface.blit(self.text1, (368, 120))
        surface.blit(self.text2, (240, 155))
        surface.blit(self.mask, (0, 0))

        # Dibujar botones base.
        for button in self.buttons:
            self.buttons[button].draw(surface)

        for btn in self.delete_buttons.values():
            btn.draw(surface)

        # Dibujar textos de titulos.
        for text in self.text_items:
            text.draw(surface)

        # Dibujar informacion de cada archivo de guardado.
        for i, slot in enumerate(["save1", "save2", "save3"]):
            data = self.saves_data[slot]
            x = self.buttons[slot].rect.x + 20
            y = self.buttons[slot].rect.y + 60

            if data is None:
                # Archivo vacio.
                empty_text = self.font.render("Vacio", True, c.COLOUR_BLACK)
                surface.blit(empty_text, (x, y))
            else:
                # Mostrar recursos.
                money_text = self.font.render(f"Oro: {data.get('money', 0)}", True, c.COLOUR_BLACK)
                surface.blit(money_text, (x, y))
                time_text = self.font.render(f"Tiempo: {data.get('time_units', 0)}", True, c.COLOUR_BLACK)
                surface.blit(time_text, (x, y + 25))

                # Mostrar niveles de edificios.
                buildings = data.get('buildings', {})
                y_offset = y + 60
                for name, info in buildings.items():
                    if name == "wheat_field":
                        display = "Trigo"
                    elif name == "smithing_house":
                        display = "Herreria"
                    elif name == "shooting_range":
                        display = "Tiro"
                    else:
                        display = name
                    lvl_text = self.font.render(f"{display}: {info.get('level', 0)}", True, c.COLOUR_BLACK)
                    surface.blit(lvl_text, (x, y_offset))
                    y_offset += 22

    def refresh_saves(self):
        # Vuelve a leer los archivos de guardado para actualizar los datos.
        for i in range(1, 4):
            slot = f"save{i}"
            path = SAVE_DIR / f"{slot}.json"
            if path.exists():
                with path.open('r') as f:
                    data = json.load(f)
                self.saves_data[slot] = data
            else:
                self.saves_data[slot] = None