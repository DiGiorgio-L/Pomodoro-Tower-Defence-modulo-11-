# -*- coding: latin-1 -*-

# Modulos de python.
import sys
from typing import List, Dict
import json

# Modulos de pygame.
import pygame as pg
from pygame.locals import *

# Modulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button, ButtonCustom
from classes.level import Level
from classes.turret import Turret
from classes.enemy import Enemy

from utils import constants as c
from config import LEVELS_DIR, ENEMIES_DIR, TURRETS_DIR, FONTS_DIR

class WaveManager:
    # Gestiona la generacion de oleadas de enemigos.
    def __init__(self, enemy_group, waypoints, enemy_types, game_duration=300,
                 on_enemy_escape=None):
        self.enemy_group = enemy_group
        self.waypoints = waypoints
        self.enemy_types = enemy_types      # dict: nombre -> (imagen, vida, velocidad, recompensa)
        self.game_duration = game_duration  # segundos

        self.start_time = pg.time.get_ticks()
        self.current_time = 0.0
        self.elapsed = 0.0

        # Parametros de oleadas.
        self.wave_interval = 30
        self.initial_delay = 5
        self.wave_number = 0
        self.next_wave_time = self.initial_delay * 1000.0

        self.current_wave_enemies = []
        self.spawn_index = 0
        self.next_spawn_time = 0.0
        self.spawning = False

        self.game_over = False
        self.victory = False
        self.started = False
        self.wave_in_progress = False
        self.on_enemy_escape = on_enemy_escape

    def start(self):
        # Inicia el contador de oleadas.
        self.started = True
        self.current_time = 0.0
        self.elapsed = 0.0
        self.next_wave_time = 0.0
        self.wave_in_progress = False

    def update(self, dt):
        # Actualiza el estado de las oleadas (tiempo, spawn).
        dt_ms = dt * 1000.0
        self.current_time += dt_ms
        self.elapsed = self.current_time

        if not self.started:
            return

        # Comprobar si se acabo el tiempo.
        if self.elapsed >= self.game_duration * 1000.0:
            if not self.spawning and len(self.enemy_group) == 0:
                self.victory = True
                self.game_over = True
                self.wave_in_progress = False
            return

        if not self.spawning:
            if self.current_time >= self.next_wave_time:
                self.start_next_wave()
        else:
            if self.spawn_index < len(self.current_wave_enemies):
                if self.current_time >= self.next_spawn_time:
                    self.spawn_enemy()
            else:
                self.spawning = False

    def start_next_wave(self):
        # Prepara la siguiente oleada.
        self.wave_number += 1
        self.current_wave_enemies = self.generate_wave(self.wave_number)
        self.spawn_index = 0
        self.spawning = True
        self.wave_in_progress = True
        self.next_spawn_time = self.current_time
        self.next_wave_time = self.current_time + self.wave_interval * 1000.0

    def generate_wave(self, wave_num):
        # Genera una lista de nombres de enemigos para la oleada.
        enemies = []
        if wave_num == 1:
            enemies = ["goblin"] * 5
        elif wave_num == 2:
            enemies = ["goblin"] * 3 + ["troll"] * 2
        elif wave_num == 3:
            enemies = ["goblin"] * 2 + ["troll"] * 2 + ["giant"] * 1
        else:
            base = wave_num - 3
            enemies = (["goblin"] * (2 + base) +
                       ["troll"] * (2 + base // 2) +
                       ["giant"] * (1 + base // 3))
        return enemies

    def spawn_enemy(self):
        # Crea un enemigo y lo agrega al grupo.
        enemy_type = self.current_wave_enemies[self.spawn_index]
        self.spawn_index += 1
        img, health, speed, reward = self.enemy_types[enemy_type]

        enemy = Enemy(self.waypoints, img, health, speed, self.on_enemy_escape)
        enemy.reward = reward
        self.enemy_group.add(enemy)

        self.next_spawn_time = self.current_time + 500.0

class TowerDefence(State):
    # Estado principal del modo defensa de torres.
    def __init__(self, parent_state_machine, level: str, sound_manager) -> None:
        self.parent_state_machine = parent_state_machine
        self.sound_manager = sound_manager

        # Cargar datos del mapa.
        if level == "level1":
            with open(LEVELS_DIR / "level1.tmj", 'r') as file:
                level_data = json.load(file)
            level_img  = pg.image.load(str(LEVELS_DIR / "level1.png"))
            select_img = pg.image.load(str(LEVELS_DIR / "select_tile.png"))

        self.level = Level(level_img, level_data, select_img)

        # Cargar texturas de enemigos.
        self.enemy1_img = pg.image.load(str(ENEMIES_DIR / "goblin.png"))
        self.enemy2_img = pg.image.load(str(ENEMIES_DIR / "troll.png"))
        self.enemy3_img = pg.image.load(str(ENEMIES_DIR / "giant.png"))

        self.enemy_types = {
            "goblin": (self.enemy1_img, 50, 120, 10),
            "troll":  (self.enemy2_img, 120, 80, 25),
            "giant":  (self.enemy3_img, 250, 50, 50)
        }

        self.money = 200
        self.selected_turret_type = None
        self.turret_costs = {
            "shortbow": 100,
            "longbow": 150,
            "mortar": 200
        }

        # Cargar imagenes de torretas.
        self.turret_images = {
            "shortbow": pg.image.load(str(TURRETS_DIR / "shortbow.png")),
            "longbow": pg.image.load(str(TURRETS_DIR / "longbow.png")),
            "mortar": pg.image.load(str(TURRETS_DIR / "mortar.png"))
        }

        self.turret_names = {
            "shortbow": "Arco Corto",
            "longbow": "Arco Largo",
            "mortar": "Canon"
        }

        self.turret_group = pg.sprite.Group()
        self.enemy_group  = pg.sprite.Group()

        self.base_health = 10
        self.game_over = False
        self.paused = False

        self.multipliers = {"purchase_cost": 1.0, "upgrade_cost": 1.0,
                            "cooldown": 1.0, "damage": 1.0}
        self.start_money = 200

        self.wave_manager = WaveManager(self.enemy_group, self.level.waypoints,
                                        self.enemy_types, 300, self.enemy_escaped)

        # Elementos de la interfaz.
        self.sidebar_img = pg.image.load(str(LEVELS_DIR / "sidebar.png"))
        self.sidebar_rect = self.sidebar_img.get_rect()
        self.sidebar_rect.topleft = ((self.level.w) * c.TILE_SIZE, 0)
        self.buttons_list = []

        self.highlight_hover = pg.surface.Surface((c.TILE_SIZE, c.TILE_SIZE), SRCALPHA)
        self.highlight_hover.fill((255, 255, 255, 100))
        self.highlight_hover_rect = pg.Rect((0, 0), (c.TILE_SIZE, c.TILE_SIZE))

        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_posx = self.mouse_pos[0] // c.TILE_SIZE
        self.mouse_posy = self.mouse_pos[1] // c.TILE_SIZE

        self.font = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 20)
        # Fuente mas grande para titulos de seccion
        self.font_big = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 27)

        # Botones de torreta en la barra lateral.
        self.turret_buttons = {}
        button_width = 160
        button_height = 33
        y_offset = 100
        for i, (ttype, cost) in enumerate(self.turret_costs.items()):
            btn = Button(
                x=self.sidebar_rect.x + 20,
                y=y_offset + i * (button_height + 10),
                w=button_width,
                h=button_height,
                color_bg=c.COLOUR_BROWN,
                color_fg=c.COLOUR_CREAM,
                color_select=c.COLOUR_DARK_BROWN,
                font=self.font,
                caption=f"{self.turret_names[ttype]} (${cost})",
                radius=5
            )
            self.turret_buttons[ttype] = btn

        self.selected_turret = None

        self.upgrade_button = Button(
            x=self.sidebar_rect.x + 20,
            y=325,
            w=160,
            h=25,
            color_bg=c.COLOUR_BROWN,
            color_fg=c.COLOUR_CREAM,
            color_select=c.COLOUR_DARK_BROWN,
            font=self.font,
            caption="Mejorar",
            radius=5
        )

        btn_w, btn_h = 200, 50
        center_x = c.WIN_WIDTH // 2
        base_y = c.WIN_HEIGHT // 2 - 30

        # Botones de pausa.
        self.pause_buttons = [
            Button(center_x - btn_w//2, base_y, btn_w, btn_h,
                   c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
                   self.font, "Reanudar", radius=5),
            Button(center_x - btn_w//2, base_y + 60, btn_w, btn_h,
                   c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
                   self.font, "Regresar", radius=5)
        ]

        # Botones de game over / victoria.
        self.end_buttons = {
            "return": Button(center_x - btn_w//2, base_y + 120, btn_w, btn_h,
                           c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
                           self.font, "Regresar", radius=5)
        }

        # Estadisticas de la partida.
        self.stats = {
            "waves_completed": 0,
            "enemies_killed": 0,
            "money_spent": 0,
            "money_earned": 0,
            "time_played": 0.0
        }
        self.start_time = 0
        self.end_time = 0

    def restart(self):
        # Reinicia el estado a valores iniciales.
        self.turret_group.empty()
        self.enemy_group.empty()
        self.money = self.start_money
        self.base_health = 10
        self.game_over = False
        self.paused = False
        self.wave_manager = WaveManager(self.enemy_group, self.level.waypoints,
                                        self.enemy_types, 300, self.enemy_escaped)
        self.level.selected_tile = None
        self.selected_turret_type = None
        self.selected_turret = None
        self.stats = {
            "waves_completed": 0,
            "enemies_killed": 0,
            "money_spent": 0,
            "money_earned": 0,
            "time_played": 0.0
        }
        self.start_time = 0
        self.end_time = 0

    def handle_events(self, events: List[pg.event.Event]) -> None:
        # Procesa eventos de teclado y mouse.
        for event in events:
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    if self.game_over or self.wave_manager.victory:
                        pass
                    else:
                        self.paused = not self.paused
                elif event.key == K_SPACE:
                    if not self.wave_manager.started and not self.game_over and not self.paused:
                        self.wave_manager.start()
                        self.start_time = pg.time.get_ticks()
                        print("Inicio de oleadas!")
                elif event.key == K_F1:
                    if not self.paused and not self.game_over and not self.wave_manager.victory:
                        if self.level.selected_tile and self.selected_turret_type:
                            img = self.turret_images[self.selected_turret_type]
                            turret = Turret(img, self.level.selected_tile[0], self.level.selected_tile[1], self.selected_turret_type)
                            self.turret_group.add(turret)
                elif event.key == K_F2:
                    self.wave_manager.victory = True

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if self.game_over or self.wave_manager.victory:
                    for key, btn in self.end_buttons.items():
                        if btn.is_hovered:
                            self.sound_manager.play_sound("click")
                            if key == "return":
                                reward = self.money - self.start_money
                                if reward >= 0:
                                    self.parent_state_machine.shared_data["defense_reward"] = reward
                                self.parent_state_machine.current_state = "town"
                                self.restart()
                            return
                elif self.paused:
                    for i, btn in enumerate(self.pause_buttons):
                        if btn.is_hovered:
                            self.sound_manager.play_sound("click")
                            if i == 0:
                                self.paused = False
                            elif i == 1:
                                self.parent_state_machine.current_state = "town"
                                self.restart()
                            return
                else:
                    clicked_button = None
                    for ttype, btn in self.turret_buttons.items():
                        if btn.is_hovered:
                            clicked_button = ttype
                            break
                    if clicked_button:
                        self.sound_manager.play_sound("click")
                        self.selected_turret_type = clicked_button
                        print(f"Torreta seleccionada: {clicked_button}")
                        continue

                    if self.upgrade_button.is_hovered:
                        if self.selected_turret:
                            base_cost = self.selected_turret.get_upgrade_cost()
                            if base_cost:
                                cost = int(base_cost * self.multipliers["upgrade_cost"])
                                if self.money >= cost:
                                    self.sound_manager.play_sound("upgrade")
                                    self.selected_turret.upgrade()
                                    self.money -= cost
                                    self.stats["money_spent"] += cost
                        continue

                    if self.mouse_posx < self.level.w:
                        tile_index = self.mouse_posy * self.level.w + self.mouse_posx
                        if self.level.tiles[tile_index] == 43:
                            if self.selected_turret_type and self.money >= self.turret_costs[self.selected_turret_type]:
                                cost = int(self.turret_costs[self.selected_turret_type] * self.multipliers["purchase_cost"])
                                if self.money >= cost:
                                    if not self.is_tile_occupied(self.mouse_posx, self.mouse_posy):
                                        self.sound_manager.play_sound("purchase")
                                        img = self.turret_images[self.selected_turret_type]
                                        turret = Turret(img, self.mouse_posx, self.mouse_posy, self.selected_turret_type, self.sound_manager)
                                        turret.cooldown = int(turret.cooldown * self.multipliers["cooldown"])
                                        turret.damage = int(turret.damage * self.multipliers["damage"])
                                        self.turret_group.add(turret)
                                        self.money -= cost
                                        self.stats["money_spent"] += cost
                                        self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                                        self.selected_turret_type = None
                                    else:
                                        print("Casilla ocupada por otra torreta")
                                        self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                            else:
                                self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                        else:
                            self.level.selected_tile = None
                    else:
                        self.level.selected_tile = None

                    if self.level.selected_tile:
                        tx, ty = self.level.selected_tile
                        found = None
                        for turret in self.turret_group:
                            if turret.tile_x == tx and turret.tile_y == ty:
                                found = turret
                                break
                        self.selected_turret = found
                    else:
                        self.selected_turret = None

    def is_tile_occupied(self, tile_x, tile_y):
        # Verifica si una casilla ya tiene una torreta.
        for turret in self.turret_group:
            if turret.tile_x == tile_x and turret.tile_y == tile_y:
                return True
        return False

    def enemy_escaped(self):
        # Reduce la vida de la base cuando un enemigo escapa.
        if self.game_over:
            return
        self.base_health -= 1
        if self.base_health <= 0:
            self.sound_manager.play_sound("game_over")
            self.game_over = True
            self.end_time = pg.time.get_ticks()
            return
        self.sound_manager.play_sound("enemy_escape")

    def set_multipliers(self, multipliers):
        # Aplica multiplicadores por mejoras de edificios.
        self.multipliers = multipliers
        self.update_turret_button_captions()

    def set_initial_money(self, money):
        self.money = money
        self.start_money = money

    def update(self, dt: float) -> None:
        # Actualiza la logica del juego (enemigos, torretas, oleadas).
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_posx = self.mouse_pos[0] // c.TILE_SIZE
        self.mouse_posy = self.mouse_pos[1] // c.TILE_SIZE

        for btn in self.pause_buttons:
            btn.update()
        for btn in self.end_buttons.values():
            btn.update()

        for btn in self.turret_buttons.values():
            btn.update()
        self.upgrade_button.update()

        if self.paused or self.game_over or self.wave_manager.victory:
            return

        self.enemy_group.update(dt)
        self.wave_manager.update(dt)

        if self.wave_manager.victory and self.end_time == 0:
            self.sound_manager.play_sound("victory")
            self.end_time = pg.time.get_ticks()

        if self.game_over and self.end_time == 0:
            self.end_time = pg.time.get_ticks()

        same_location = False
        for turret in self.turret_group:
            turret.update(self.enemy_group, dt)

            if self.level.selected_tile is not None:
                if (self.level.selected_tile[0] == turret.tile_x and
                    self.level.selected_tile[1] == turret.tile_y):
                    same_location = True
                    turret.show_range = True
                else:
                    turret.show_range = False
            else:
                turret.show_range = False

        for enemy in self.enemy_group:
            if enemy.current_health <= 0:
                self.money += enemy.reward
                self.stats["enemies_killed"] += 1
                self.stats["money_earned"] += enemy.reward
                enemy.kill()

    def draw(self, surface: pg.Surface) -> None:
        # Dibuja todos los elementos del juego.
        self.level.draw(surface)

        for turret in self.turret_group:
            turret.draw(surface)

        self.enemy_group.draw(surface)
        for enemy in self.enemy_group:
            enemy.health_bar.draw(surface)

        surface.blit(self.sidebar_img, self.sidebar_rect)
        self.level.draw_overlay(surface)

        if self.mouse_posx < self.level.w:
            tile_index = self.mouse_posy * self.level.w + self.mouse_posx
            if self.level.tiles[tile_index] == 43:
                self.highlight_hover_rect.topleft = (c.TILE_SIZE * self.mouse_posx,
                                                      c.TILE_SIZE * self.mouse_posy)
                surface.blit(self.highlight_hover, self.highlight_hover_rect)

        # Tienda (arriba)
        tienda_surf = self.font_big.render("Tienda", True, c.COLOUR_CREAM)
        surface.blit(tienda_surf, (self.sidebar_rect.x + 125, 32))
        # Mejoras (encima del boton de mejora)
        mejoras_surf = self.font_big.render("Mejoras", True, c.COLOUR_CREAM)
        surface.blit(mejoras_surf, (self.sidebar_rect.x + 118, 273))
        # Estadisticas (encima de los datos de oleada)
        estadisticas_surf = self.font_big.render("Estadisticas", True, c.COLOUR_CREAM)
        surface.blit(estadisticas_surf, (self.sidebar_rect.x + 100, 512))

        if hasattr(self, 'wave_manager'):
            wm = self.wave_manager
            wave_surf = self.font.render(f"Oleada: {wm.wave_number}", True, c.COLOUR_BLACK)
            surface.blit(wave_surf, (self.sidebar_rect.x + 20, 560))

            if not wm.started:
                time_surf = self.font.render("Tiempo: 0:00", True, c.COLOUR_BLACK)
            else:
                remaining = max(0, 300 - wm.elapsed / 1000.0)
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                time_surf = self.font.render(f"Tiempo: {minutes}:{seconds:02d}", True, c.COLOUR_BLACK)
            surface.blit(time_surf, (self.sidebar_rect.x + 18, 582))

            health_surf = self.font.render(f"Base: {self.base_health}", True, c.COLOUR_BLACK)
            surface.blit(health_surf, (self.sidebar_rect.x + 20, 605))

            money_surf = self.font.render(f"Dinero: ${self.money}", True, c.COLOUR_BLACK)
            surface.blit(money_surf, (self.sidebar_rect.x + 20, 627))

            if not wm.started and not self.game_over and not wm.victory:
                msg = "Presiona SPACE para comenzar..."
                msg_surf = self.font.render(msg, True, c.COLOUR_CREAM)
                msg_rect = msg_surf.get_rect(center=((c.WIN_WIDTH // 2) - 100, c.WIN_HEIGHT - 50))
                surface.blit(msg_surf, msg_rect)

        if not self.paused and not self.game_over and not self.wave_manager.victory:
            for btn in self.turret_buttons.values():
                btn.draw(surface)
            self.upgrade_button.draw(surface)

            if self.selected_turret_type:
                btn = self.turret_buttons[self.selected_turret_type]
                pg.draw.rect(surface, c.COLOUR_GREEN, btn.rect, 3)

            if self.selected_turret:
                turret = self.selected_turret
                info_y = self.upgrade_button.rect.bottom + 5
                lvl_surf = self.font.render(f"Nivel: {turret.level}", True, c.COLOUR_BLACK)
                surface.blit(lvl_surf, (self.sidebar_rect.x + 20, info_y))
                dmg_surf = self.font.render(f"Danio: {turret.damage}", True, c.COLOUR_BLACK)
                surface.blit(dmg_surf, (self.sidebar_rect.x + 20, info_y + 22))
                rng_surf = self.font.render(f"Rango: {turret.range}", True, c.COLOUR_BLACK)
                surface.blit(rng_surf, (self.sidebar_rect.x + 20, info_y + 44))
                cd_surf = self.font.render(f"CD: {turret.cooldown}ms", True, c.COLOUR_BLACK)
                surface.blit(cd_surf, (self.sidebar_rect.x + 20, info_y + 66))
                cost = turret.get_upgrade_cost()
                if cost:
                    real_cost = int(cost * self.multipliers["upgrade_cost"])
                    color = c.COLOUR_GREEN if self.money >= real_cost else c.COLOUR_RED
                    cost_surf = self.font.render(f"Mejorar: ${real_cost}", True, color)
                    surface.blit(cost_surf, (self.sidebar_rect.x + 20, info_y + 88))

        if self.paused:
            self.draw_pause_overlay(surface)
        elif self.game_over:
            self.draw_game_over_overlay(surface)
        elif self.wave_manager.victory:
            self.draw_victory_overlay(surface)

    def draw_pause_overlay(self, surface):
        # Dibuja la pantalla de pausa.
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_big = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 72)
        text = font_big.render("PAUSA", True, c.COLOUR_CREAM)
        text_rect = text.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 100))
        surface.blit(text, text_rect)

        for btn in self.pause_buttons:
            btn.draw(surface)

    def draw_game_over_overlay(self, surface):
        # Dibuja la pantalla de game over con estadisticas.
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_big = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 72)
        text = font_big.render("GAME OVER", True, c.COLOUR_RED)
        text_rect = text.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 130))
        surface.blit(text, text_rect)

        if self.end_time > 0 and self.start_time > 0:
            elapsed = (self.end_time - self.start_time) / 1000.0
        else:
            elapsed = 0

        self.stats["time_played"] = elapsed
        self.stats["waves_completed"] = self.wave_manager.wave_number

        font_small = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 28)
        stats_lines = [
            f"Oleadas completadas: {self.stats['waves_completed']}",
            f"Enemigos eliminados: {self.stats['enemies_killed']}",
            f"Dinero gastado: ${self.stats['money_spent']}",
            f"Dinero ganado: ${self.stats['money_earned']}",
            f"Tiempo jugado: {int(elapsed//60)}:{int(elapsed%60):02d}"
        ]
        y_offset = c.WIN_HEIGHT // 2 - 60
        for line in stats_lines:
            surf = font_small.render(line, True, c.COLOUR_CREAM)
            rect = surf.get_rect(center=(c.WIN_WIDTH // 2, y_offset))
            surface.blit(surf, rect)
            y_offset += 30

        for btn in self.end_buttons.values():
            btn.draw(surface)

    def update_turret_button_captions(self):
        # Actualiza los textos de los botones de torreta con los multiplicadores.
        for ttype, btn in self.turret_buttons.items():
            base_cost = self.turret_costs[ttype]
            real_cost = int(base_cost * self.multipliers["purchase_cost"])
            btn.set_caption(f"{self.turret_names[ttype]} (${real_cost})", self.font)

    def draw_victory_overlay(self, surface):
        # Dibuja la pantalla de victoria con estadisticas.
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_big = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 72)
        text = font_big.render("VICTORIA!", True, c.COLOUR_GREEN)
        text_rect = text.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 130))
        surface.blit(text, text_rect)

        if self.end_time > 0 and self.start_time > 0:
            elapsed = (self.end_time - self.start_time) / 1000.0
        else:
            elapsed = 0

        self.stats["time_played"] = elapsed
        self.stats["waves_completed"] = self.wave_manager.wave_number

        font_small = pg.font.Font(str(FONTS_DIR / "PirataOne-Regular.ttf"), 28)
        stats_lines = [
            f"Oleadas completadas: {self.stats['waves_completed']}",
            f"Enemigos eliminados: {self.stats['enemies_killed']}",
            f"Dinero gastado: ${self.stats['money_spent']}",
            f"Dinero ganado: ${self.stats['money_earned']}",
            f"Tiempo jugado: {int(elapsed//60)}:{int(elapsed%60):02d}"
        ]
        y_offset = c.WIN_HEIGHT // 2 - 60
        for line in stats_lines:
            surf = font_small.render(line, True, c.COLOUR_CREAM)
            rect = surf.get_rect(center=(c.WIN_WIDTH // 2, y_offset))
            surface.blit(surf, rect)
            y_offset += 30

        for btn in self.end_buttons.values():
            btn.draw(surface)

    def optimize_images(self):
        # Optimiza las imagenes para mejorar el rendimiento.
        self.level.image = self.level.image.convert()
        self.level.select_tile_img = self.level.select_tile_img.convert_alpha()
        self.enemy1_img = self.enemy1_img.convert_alpha()
        self.enemy2_img = self.enemy2_img.convert_alpha()
        self.enemy3_img = self.enemy3_img.convert_alpha()
        self.sidebar_img = self.sidebar_img.convert()

        for turret in self.turret_images:
            self.turret_images[turret].convert_alpha()