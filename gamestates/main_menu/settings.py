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

class Settings(State):
    def __init__(self) -> None:
        pass

    def handle_events(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pg.Surface) -> None:
        pass
