# Modulos de python.
import sys
from typing import List, Dict
from abc import ABC, abstractmethod

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.

# Clase que define un posible estado de la maquina.
# Cada estado heredara de esta clase y se debera implementar su propia logica.
class State(ABC):
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

# Clase que define una state machine. Se encarga de ejecutar diferentes ramas de
# codigo basado en el estado general del juego.
class StateMachine():
    def __init__(self) -> None:
        self.states: Dict[str, State] = {}
        self.prev_state = None
        self.current_state = None
        self.exit_state = None

    def set_starting_state(self, key: str):
        self.current_state = key
        
    def add_state(self, key: str, state: State) -> None:
        self.states[key] = state

    def remove_state(self, key: str) -> None:
        self.states.pop(key)

    def terminate_machine(self, exit_state: str) -> str:
        self.exit_state = exit_state
        
    def handle_events(self, events: List[pg.event.Event]) -> None:
        self.states[self.current_state].handle_events(events)

    def update(self, dt: float) -> None:
        if self.exit_state == None:
            self.states[self.current_state].update(dt)

    def draw(self, surface: pg.Surface) -> None:
        self.states[self.current_state].draw(surface)


