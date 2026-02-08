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

        # Crea m�quina de estados.
        self.state_machine = StateMachine()

        # Intanciar estados de la maquina.
        main_menu = MainMenu(self.state_machine)

        # NOTA: Este estado debe ser creado desde otra parte.
        # El estado tower defence en realidad sera cargado desde la pantalla del pueblo,
        # debido a que es necesario tener acceso a los datos del archivo de guardado
        # cargado.
        tower_defence = TowerDefence(self.state_machine, "level1")

        # Agregar estados a la maquina.
        self.state_machine.add_state("main_menu", main_menu)
        self.state_machine.add_state("tower_defence", tower_defence)

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

    def draw(self) -> None:
        self.state_machine.draw(self.surface)
        
    
