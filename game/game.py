# Python modules
import sys
from typing import List

# Pygame modules
import pygame as pg
from pygame.locals import *

# Custom modules
from enfocate import GameBase, GameMetadata, COLORS
from classes.state_machine import StateMachine
from gamestates.main_menu.main_menu import MainMenu
from gamestates.tower_defence.tower_defence import TowerDefence
from gamestates.town.town import Town
from classes.sound_manager import SoundManager
from config import SOUNDS_DIR

class PomodoroTD(GameBase):
    # Clase principal del juego, hereda de GameBase.
    def __init__(self):
        pg.init()
        metadata = GameMetadata(
            title="Pomodoro Tower Defence",
            description="Pomodoro Tower Defence integra la técnica Pomodoro con tower defence para ayudar a personas con TDAH a mejorar su concentración mientras se divierten.",
            authors=["Leonardo Di Giorgio, Ricardo Trevison, Victor Alcala, Camila Reyes"],
            group_number=11
        )

        super().__init__(metadata)

        # Crea maquina de estados.
        self.state_machine = StateMachine()

        # Cargar sonidos
        self.sound_manager = SoundManager()
        self.sound_manager.load_sound("click", str(SOUNDS_DIR / "click.wav"))
        self.sound_manager.load_sound("purchase", str(SOUNDS_DIR / "purchase.wav"))
        self.sound_manager.load_sound("upgrade", str(SOUNDS_DIR / "upgrade.wav"))
        self.sound_manager.load_sound("enemy_escape", str(SOUNDS_DIR / "enemy_escape.wav"))
        self.sound_manager.load_sound("bow_shot", str(SOUNDS_DIR / "bow_shot.wav"))
        self.sound_manager.load_sound("mortar_shell", str(SOUNDS_DIR / "mortar_shell.wav"))
        self.sound_manager.load_sound("mortar_explosion", str(SOUNDS_DIR / "mortar_explosion.wav"))
        self.sound_manager.load_sound("game_over", str(SOUNDS_DIR / "game_over.wav"))
        self.sound_manager.load_sound("victory", str(SOUNDS_DIR / "victory.wav"))
        self.sound_manager.load_sound("notification", str(SOUNDS_DIR / "notification.wav"))

        # Instanciar estados de la maquina.
        main_menu = MainMenu(self.state_machine, self.sound_manager)
        town = Town(self.state_machine)
        tower_defence = TowerDefence(self.state_machine, "level1", self.sound_manager)

        # Agregar estados a la maquina.
        self.state_machine.add_state("main_menu", main_menu)
        self.state_machine.add_state("tower_defence", tower_defence)
        self.state_machine.add_state("town", town)

        # Establecer estado inicial.
        self.state_machine.set_starting_state("main_menu")

    def on_start(self) -> None:
        # Se ejecuta al iniciar el juego. Optimiza imagenes del estado tower_defence.
        self.state_machine.states["tower_defence"].optimize_images()

    def handle_events(self, events: List[pg.event.Event]) -> None:
        # Pasa los eventos a la maquina de estados.
        self.state_machine.handle_events(events)

    def update(self, dt: float) -> None:
        # Actualiza la maquina de estados, manejando posibles salidas.
        if self.state_machine.exit_state == None:
            self.state_machine.update(dt)
        elif self.state_machine.exit_state == "tower_defence":
            self.state_machine.current_state = "tower_defence"
            self.state_machine.exit_state = None
        elif self.state_machine.exit_state == "main_menu":
            self.state_machine.current_state = "main_menu"
            self.state_machine.exit_state = None
        elif self.state_machine.exit_state == "close":
            self._stop_context()

    def draw(self) -> None:
        # Dibuja el estado actual en la superficie de la ventana.
        self.state_machine.draw(self.surface)