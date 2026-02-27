import pygame as pg
import os

class SoundManager:
    # Gestiona la carga y reproduccion de efectos de sonido y musica.
    def __init__(self):
        pg.mixer.init()
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7

    def load_sound(self, name, path):
        # Carga un efecto de sonido y lo almacena con un nombre.
        try:
            sound = pg.mixer.Sound(path)
            self.sounds[name] = sound
        except Exception as e:
            print(f"Error cargando sonido {name} desde {path}: {e}")

    def play_sound(self, name, volume=None):
        # Reproduce un sonido por su nombre.
        if name in self.sounds:
            sound = self.sounds[name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sfx_volume)
            sound.play()
        else:
            print(f"Sonido {name} no encontrado")

    def set_sfx_volume(self, volume):
        # Ajusta el volumen de los efectos (0.0 a 1.0).
        self.sfx_volume = max(0.0, min(1.0, volume))

    def play_music(self, path, loop=True):
        # Reproduce musica de fondo.
        try:
            pg.mixer.music.load(path)
            pg.mixer.music.set_volume(self.music_volume)
            if loop:
                pg.mixer.music.play(-1)
            else:
                pg.mixer.music.play()
        except Exception as e:
            print(f"Error cargando musica {path}: {e}")

    def stop_music(self):
        # Detiene la musica.
        pg.mixer.music.stop()

    def set_music_volume(self, volume):
        # Ajusta el volumen de la musica.
        self.music_volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self.music_volume)