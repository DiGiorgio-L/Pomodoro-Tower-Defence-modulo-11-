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

class PomodoroTD(GameBase):
    def __init__(self):
        pg.init()
        metadata = GameMetadata(
            title="Pomodoro Tower Defence",
            description="Vacio",
            authors=["Leonardo Di Giorgio, Ricardo Trevison, Victor Alcala, Camila Reyes"],
            group_number=11
        )

        super().__init__(metadata)

        # Crea maquina de estados.
        self.state_machine = StateMachine()

        # Cargar sonidos
        self.sound_manager = SoundManager()
        self.sound_manager.load_sound("click", "assets/sounds/click.wav")
        self.sound_manager.load_sound("purchase", "assets/sounds/purchase.wav")
        self.sound_manager.load_sound("upgrade", "assets/sounds/upgrade.wav")
        self.sound_manager.load_sound("enemy_escape", "assets/sounds/enemy_escape.wav")
        self.sound_manager.load_sound("bow_shot", "assets/sounds/bow_shot.wav")
        self.sound_manager.load_sound("mortar_shell", "assets/sounds/mortar_shell.wav")
        self.sound_manager.load_sound("mortar_explosion", "assets/sounds/mortar_explosion.wav")
        self.sound_manager.load_sound("game_over", "assets/sounds/game_over.wav")
        self.sound_manager.load_sound("victory", "assets/sounds/victory.wav")
        self.sound_manager.load_sound("notification", "assets/sounds/notification.wav")

        # Intanciar estados de la maquina.
        main_menu = MainMenu(self.state_machine, self.sound_manager)

        town = Town(self.state_machine)
        
        # NOTA: Este estado debe ser creado desde otra parte.
        # El estado tower defence en realidad sera cargado desde la pantalla del pueblo,
        # debido a que es necesario tener acceso a los datos del archivo de guardado
        # cargado.
        tower_defence = TowerDefence(self.state_machine, "level1", self.sound_manager)

        # Agregar estados a la maquina.
        self.state_machine.add_state("main_menu", main_menu)
        self.state_machine.add_state("tower_defence", tower_defence)
        self.state_machine.add_state("town", town)

        # Establecer estado inicial.
        self.state_machine.set_starting_state("main_menu")

    def on_start(self) -> None:
        self.state_machine.states["tower_defence"].optimize_images()

    def handle_events(self, events: List[pg.event.Event]) -> None:
        self.state_machine.handle_events(events)
    
    def update(self, dt: float) -> None:
        if self.state_machine.exit_state == None:
            self.state_machine.update(dt)
        elif self.state_machine.exit_state == "tower_defence":
            self.state_machine.current_state = "tower_defence"
            self.state_machine.exit_state = None 
        elif self.state_machine.exit_state == "main_menu":
            self.state_machine.current_state = "main_menu"
            self.state_machine.exit_state = None

    def draw(self) -> None:
        self.state_machine.draw(self.surface)
        
    
