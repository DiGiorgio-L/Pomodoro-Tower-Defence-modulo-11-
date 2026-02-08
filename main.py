# Python modules
import sys

# Pygame modules
import pygame as pg
from pygame.locals import *

# Custom modules
import enfocate
from game.game import PomodoroTD

if __name__ == "__main__":
    game = PomodoroTD()
    game.run_preview()
    
