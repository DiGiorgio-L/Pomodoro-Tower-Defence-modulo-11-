# Modulos de python.
import sys
from typing import List, Dict
from abc import ABC, abstractmethod

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.

class State(ABC):
    # Clase base abstracta para un estado de la maquina de estados.
    def __init__(self) -> None:
        pass

    @abstractmethod
    def handle_events(self) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pg.Surface) -> None:
        pass

class StateMachine():
    # Maquina de estados que gestiona la transicion entre diferentes estados.
    def __init__(self) -> None:
        self.states: Dict[str, State] = {}
        self.prev_state = None
        self.current_state = None
        self.exit_state = None
        self.shared_data = {}

    def set_starting_state(self, key: str):
        # Establece el estado inicial.
        self.current_state = key

    def add_state(self, key: str, state: State) -> None:
        # Agrega un estado a la maquina.
        self.states[key] = state

    def remove_state(self, key: str) -> None:
        # Elimina un estado de la maquina.
        self.states.pop(key)

    def terminate_machine(self, exit_state: str) -> str:
        # Marca el estado de salida.
        self.exit_state = exit_state

    def handle_events(self, events: List[pg.event.Event]) -> None:
        # Pasa los eventos al estado actual.
        self.states[self.current_state].handle_events(events)

    def update(self, dt: float) -> None:
        # Actualiza el estado actual si no hay estado de salida.
        if self.exit_state == None:
            self.states[self.current_state].update(dt)

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja el estado actual.
        self.states[self.current_state].draw(surface)