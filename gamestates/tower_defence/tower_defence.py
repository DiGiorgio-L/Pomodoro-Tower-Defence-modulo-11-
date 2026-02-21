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

class WaveManager:
    def __init__(self, enemy_group, waypoints, enemy_types, game_duration=300,
                 on_enemy_escape=None):
        self.enemy_group = enemy_group
        self.waypoints = waypoints
        self.enemy_types = enemy_types      # dict: nombre -> (imagen, vida, velocidad, recompensa)
        self.game_duration = game_duration  # segundos

        self.start_time = pg.time.get_ticks()  # referencia (no se usa directamente)
        self.current_time = 0.0                # tiempo acumulado en ms
        self.elapsed = 0.0

        # ParÃ¡metros de oleadas
        self.wave_interval = 30          # segundos entre inicios de oleada
        self.initial_delay = 5           # segundos antes de la primera oleada
        self.wave_number = 0
        self.next_wave_time = self.initial_delay * 1000.0  # ms

        self.current_wave_enemies = []   # lista de nombres de enemigos a spawnear
        self.spawn_index = 0
        self.next_spawn_time = 0.0
        self.spawning = False

        self.game_over = False
        self.victory = False
        self.started = False
        self.wave_in_progress = False
        self.on_enemy_escape = on_enemy_escape

    def start(self):
        self.started = True
        self.current_time = 0.0
        self.elapsed = 0.0
        self.next_wave_time = 0.0
        self.wave_in_progress = False

    def update(self, dt):
        # dt en segundos -> convertir a ms
        dt_ms = dt * 1000.0
        self.current_time += dt_ms
        self.elapsed = self.current_time

        if not self.started:
            return
        
        # Comprobar si se acabÃ³ el tiempo
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
            # Spawnear enemigos de la oleada actual
            if self.spawn_index < len(self.current_wave_enemies):
                if self.current_time >= self.next_spawn_time:
                    self.spawn_enemy()
            else:
                # TerminÃ³ de spawnear esta oleada
                self.spawning = False
                

    def start_next_wave(self):
        self.wave_number += 1
        self.current_wave_enemies = self.generate_wave(self.wave_number)
        self.spawn_index = 0
        self.spawning = True
        self.wave_in_progress = True
        self.next_spawn_time = self.current_time   # spawn inmediato
        # Programar la siguiente oleada
        self.next_wave_time = self.current_time + self.wave_interval * 1000.0

    def generate_wave(self, wave_num):
        enemies = []
        if wave_num == 1:
            enemies = ["goblin"] * 5
        elif wave_num == 2:
            enemies = ["goblin"] * 3 + ["troll"] * 2
        elif wave_num == 3:
            enemies = ["goblin"] * 2 + ["troll"] * 2 + ["giant"] * 1
        else:
            # Oleadas progresivas
            base = wave_num - 3
            enemies = (["goblin"] * (2 + base) +
                       ["troll"] * (2 + base // 2) +
                       ["giant"] * (1 + base // 3))
        return enemies

    def spawn_enemy(self):
        enemy_type = self.current_wave_enemies[self.spawn_index]
        self.spawn_index += 1
        img, health, speed, reward = self.enemy_types[enemy_type]

        enemy = Enemy(self.waypoints, img, health, speed, self.on_enemy_escape)
        enemy.reward = reward   # para cuando implementemos economÃ­a
        self.enemy_group.add(enemy)

        # Siguiente enemigo en 0.5 segundos
        self.next_spawn_time = self.current_time + 500.0  # 0.5 s en ms


class TowerDefence(State):
    def __init__(self, parent_state_machine, level: str) -> None:
        # Referencia a la state machine que llamara a este estado
        self.parent_state_machine = parent_state_machine

        # Cargas datos del mapa.
        if level == "level1":
            with open("assets/levels/level1.tmj") as file:
                level_data = json.load(file)                
            level_img  = pg.image.load("assets/levels/level1.png")
            select_img = pg.image.load("assets/levels/select_tile.png")

        # Crear mapa.
        self.level = Level(level_img, level_data, select_img)

        # Cargar texturas de enemigos
        self.enemy1_img = pg.image.load("assets/enemies/goblin.png")
        self.enemy2_img = pg.image.load("assets/enemies/troll.png")
        self.enemy3_img = pg.image.load("assets/enemies/giant.png")

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

        # Cargar imágenes de torretas
        self.turret_images = {
            "shortbow": pg.image.load("assets/turrets/shortbow.png"),
            "longbow": pg.image.load("assets/turrets/longbow.png"),
            "mortar": pg.image.load("assets/turrets/mortar.png")
        }
        
        # Crear grupos de enemigos y torretas.
        self.turret_group = pg.sprite.Group()
        self.enemy_group  = pg.sprite.Group()

        self.base_health = 10
        self.game_over = False
        self.paused = False

        self.wave_manager = WaveManager(self.enemy_group, self.level.waypoints,
                                        self.enemy_types, 300, self.enemy_escaped)
        
        # Elementos de la interfaz.
        self.sidebar_img = pg.image.load("assets/levels/sidebar.png")
        self.sidebar_rect = self.sidebar_img.get_rect()
        self.sidebar_rect.topleft = ((self.level.w) * c.TILE_SIZE, 0)
        self.buttons_list = []

        # Imagen para resaltar la casilla por la que esta pasando el cursor.
        self.highlight_hover = pg.surface.Surface((c.TILE_SIZE, c.TILE_SIZE), SRCALPHA)
        self.highlight_hover.fill((255, 255, 255, 100))
        self.highlight_hover_rect = pg.Rect((0, 0), (c.TILE_SIZE, c.TILE_SIZE))

        # Posicion del cursor.
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_posx = self.mouse_pos[0] // c.TILE_SIZE # Posicion en casillas.
        self.mouse_posy = self.mouse_pos[1] // c.TILE_SIZE

        self.font = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 20)

        # Crear botones de torretas en el sidebar
        self.turret_buttons = {}
        button_width = 160
        button_height = 33
        y_offset = 100
        names = ["Arco Corto", "Arco Largo", "Cañón"]
        count = 0
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
                caption=f"{names[count]} (${cost})",
                radius=5
            )
            count += 1
            self.turret_buttons[ttype] = btn

        self.selected_turret = None
        
        self.upgrade_button = Button(
            x=self.sidebar_rect.x + 20,
            y=325,  # ajustado para dejar espacio
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

        # Botones de pausa
        self.pause_buttons = [
            Button(center_x - btn_w//2, base_y, btn_w, btn_h,
                   c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
                   self.font, "Reanudar", radius=5),
            Button(center_x - btn_w//2, base_y + 60, btn_w, btn_h,
                   c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
                   self.font, "Menú Principal", radius=5)
        ]

        # Botones de game over / victoria
        self.end_buttons = {
            "menu": Button(center_x - btn_w//2, base_y + 120, btn_w, btn_h,
                           c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
                           self.font, "Regresar", radius=5)
        }

        # Estadísticas de la partida
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
        self.turret_group.empty()
        self.enemy_group.empty()
        self.money = 200
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
        for event in events:
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    if self.game_over or self.wave_manager.victory:
                        # Si ya terminó, ESC vuelve al menú
                        self.parent_state_machine.current_state = "main_menu"
                    else:
                        # Alternar pausa
                        self.paused = not self.paused
                elif event.key == K_SPACE:
                    if not self.wave_manager.started and not self.game_over and not self.paused:
                        self.wave_manager.start()
                        self.start_time = pg.time.get_ticks()
                        print("Inicio de oleadas!")
                elif event.key == K_F1:
                    # Debug: colocar torreta sin costo (solo si no estÃ¡ en pausa ni terminado)
                    if not self.paused and not self.game_over and not self.wave_manager.victory:
                        if self.level.selected_tile and self.selected_turret_type:
                            img = self.turret_images[self.selected_turret_type]
                            turret = Turret(img, self.level.selected_tile[0], self.level.selected_tile[1], self.selected_turret_type)
                            self.turret_group.add(turret)

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                # Si hay game over o victoria, solo se procesan los botones finales
                if self.game_over or self.wave_manager.victory:
                    for key, btn in self.end_buttons.items():
                        if btn.is_hovered:
                            if key == "menu":
                                self.parent_state_machine.current_state = "main_menu"
                                self.restart() 
                            return
                # Si está en pausa, solo procesar botones de pausa
                elif self.paused:
                    for i, btn in enumerate(self.pause_buttons):
                        if btn.is_hovered:
                            if i == 0:  # Reanudar
                                self.paused = False
                            elif i == 1:  # Menú Principal
                                self.parent_state_machine.current_state = "main_menu"
                                self.restart() 
                            return
                else:
                    # Juego normal: procesar botones de torreta y mejora
                    # Comprobar clic en botones de torreta
                    clicked_button = None
                    for ttype, btn in self.turret_buttons.items():
                        if btn.is_hovered:
                            clicked_button = ttype
                            break
                    if clicked_button:
                        self.selected_turret_type = clicked_button
                        print(f"Torreta seleccionada: {clicked_button}")
                        continue

                    # Comprobar clic en botón de mejora
                    if self.upgrade_button.is_hovered:
                        if self.selected_turret:
                            cost = self.selected_turret.get_upgrade_cost()
                            if cost and self.money >= cost:
                                self.selected_turret.upgrade()
                                self.money -= cost
                                self.stats["money_spent"] += cost
                        continue

                    # Clic en el mapa
                    if self.mouse_posx < self.level.w:
                        tile_index = self.mouse_posy * self.level.w + self.mouse_posx
                        if self.level.tiles[tile_index] == 43:
                            # Casilla construible
                            if self.selected_turret_type and self.money >= self.turret_costs[self.selected_turret_type]:
                                if not self.is_tile_occupied(self.mouse_posx, self.mouse_posy):
                                    # Colocar torreta
                                    img = self.turret_images[self.selected_turret_type]
                                    turret = Turret(img, self.mouse_posx, self.mouse_posy, self.selected_turret_type)
                                    self.turret_group.add(turret)
                                    self.money -= self.turret_costs[self.selected_turret_type]
                                    self.stats["money_spent"] += self.turret_costs[self.selected_turret_type]
                                    self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                                    self.selected_turret_type = None
                                else:
                                    print("Casilla ocupada por otra torreta")
                                    self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                            else:
                                # Solo seleccionar la casilla
                                self.level.selected_tile = (self.mouse_posx, self.mouse_posy)
                        else:
                            self.level.selected_tile = None
                    else:
                        self.level.selected_tile = None

                    # Actualizar torreta seleccionada segÃºn la casilla
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
        for turret in self.turret_group:
            if turret.tile_x == tile_x and turret.tile_y == tile_y:
                return True
        return False

    def enemy_escaped(self):
        if self.game_over:
            return
        self.base_health -= 1
        if self.base_health <= 0:
            self.game_over = True
            self.end_time = pg.time.get_ticks()

    def update(self, dt: float) -> None:
        # Actualizar posiciÃ³n del cursor (siempre)
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_posx = self.mouse_pos[0] // c.TILE_SIZE
        self.mouse_posy = self.mouse_pos[1] // c.TILE_SIZE

        # Actualizar botones de pausa y fin (hover)
        for btn in self.pause_buttons:
            btn.update()
        for btn in self.end_buttons.values():
            btn.update()

        # Actualizar botones de torreta y mejora (hover)
        for btn in self.turret_buttons.values():
            btn.update()
        self.upgrade_button.update()

        # Si está en pausa, game over o victoria, no actualizar el juego
        if self.paused or self.game_over or self.wave_manager.victory:
            return

        # Actualizar lógica de los enemigos.
        self.enemy_group.update(dt)

        # Actualizar oleadas
        self.wave_manager.update(dt)

        # Detectar victoria por tiempo y guardar tiempo final
        if self.wave_manager.victory and self.end_time == 0:
            self.end_time = pg.time.get_ticks()

        # Si game_over se activó por otra razón y no se guardó, se guarda aquí
        if self.game_over and self.end_time == 0:
            self.end_time = pg.time.get_ticks()

        # Actualizar lógica de las torretas.
        same_location = False
        for turret in self.turret_group:
            turret.update(self.enemy_group, dt)

            # Determinar si la casilla seleccionada tiene una torreta.
            if self.level.selected_tile is not None:
                if (self.level.selected_tile[0] == turret.tile_x and
                    self.level.selected_tile[1] == turret.tile_y):
                    same_location = True
                    turret.show_range = True
                else:
                    turret.show_range = False
            else:
                turret.show_range = False

        # Recompensas por enemigos muertos
        for enemy in self.enemy_group:
            if enemy.current_health <= 0:
                self.money += enemy.reward
                self.stats["enemies_killed"] += 1
                self.stats["money_earned"] += enemy.reward
                enemy.kill()

    def draw(self, surface: pg.Surface) -> None:
        # Dibujar imagen de fondo.
        self.level.draw(surface)

        # Dibujar torretas colocadas.
        for turret in self.turret_group:
            turret.draw(surface)

        # Dibujar enemigos.
        self.enemy_group.draw(surface)
        for enemy in self.enemy_group:
            enemy.health_bar.draw(surface)

        # Sidebar y overlay de selecciÃ³n
        surface.blit(self.sidebar_img, self.sidebar_rect)
        self.level.draw_overlay(surface)

        # Resaltar casilla bajo el cursor si es construible
        if self.mouse_posx < self.level.w:
            # NOTA: Reemplazar 20 por self.level.w para generalidad
            tile_index = self.mouse_posy * self.level.w + self.mouse_posx
            if self.level.tiles[tile_index] == 43:
                self.highlight_hover_rect.topleft = (c.TILE_SIZE * self.mouse_posx,
                                                      c.TILE_SIZE * self.mouse_posy)
                surface.blit(self.highlight_hover, self.highlight_hover_rect)

        # Información en el sidebar (siempre visible)
        if hasattr(self, 'wave_manager'):
            wm = self.wave_manager
            # Oleada
            wave_surf = self.font.render(f"Oleada: {wm.wave_number}", True, c.COLOUR_BLACK)
            surface.blit(wave_surf, (self.sidebar_rect.x + 20, 560))

            # Tiempo
            if not wm.started:
                time_surf = self.font.render("Tiempo: 0:00", True, c.COLOUR_BLACK)
            else:
                remaining = max(0, 300 - wm.elapsed / 1000.0)
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                time_surf = self.font.render(f"Tiempo: {minutes}:{seconds:02d}", True, c.COLOUR_BLACK)
            surface.blit(time_surf, (self.sidebar_rect.x + 18, 582))

            # Vida de la base
            health_surf = self.font.render(f"Base: {self.base_health}", True, c.COLOUR_BLACK)
            surface.blit(health_surf, (self.sidebar_rect.x + 20, 605))

            # Dinero
            money_surf = self.font.render(f"Dinero: ${self.money}", True, c.COLOUR_BLACK)
            surface.blit(money_surf, (self.sidebar_rect.x + 20, 627))

            # Mensaje de inicio
            if not wm.started and not self.game_over and not wm.victory:
                msg = "Presiona SPACE para comenzar..."
                msg_surf = self.font.render(msg, True, c.COLOUR_CREAM)
                msg_rect = msg_surf.get_rect(center=((c.WIN_WIDTH // 2) - 100, c.WIN_HEIGHT - 50))
                surface.blit(msg_surf, msg_rect)

        # Botones de torreta y mejora (solo si no hay pausa ni fin)
        if not self.paused and not self.game_over and not self.wave_manager.victory:
            for btn in self.turret_buttons.values():
                btn.draw(surface)
            self.upgrade_button.draw(surface)

            # Resaltar botón del tipo seleccionado
            if self.selected_turret_type:
                btn = self.turret_buttons[self.selected_turret_type]
                pg.draw.rect(surface, c.COLOUR_GREEN, btn.rect, 3)

            # Información de la torreta seleccionada
            if self.selected_turret:
                turret = self.selected_turret
                info_y = self.upgrade_button.rect.bottom + 5
                lvl_surf = self.font.render(f"Nivel: {turret.level}", True, c.COLOUR_BLACK)
                surface.blit(lvl_surf, (self.sidebar_rect.x + 20, info_y))
                dmg_surf = self.font.render(f"Daño: {turret.damage}", True, c.COLOUR_BLACK)
                surface.blit(dmg_surf, (self.sidebar_rect.x + 20, info_y + 22))
                rng_surf = self.font.render(f"Rango: {turret.range}", True, c.COLOUR_BLACK)
                surface.blit(rng_surf, (self.sidebar_rect.x + 20, info_y + 44))
                cd_surf = self.font.render(f"CD: {turret.cooldown}ms", True, c.COLOUR_BLACK)
                surface.blit(cd_surf, (self.sidebar_rect.x + 20, info_y + 66))
                cost = turret.get_upgrade_cost()
                if cost:
                    color = c.COLOUR_GREEN if self.money >= cost else c.COLOUR_RED
                    cost_surf = self.font.render(f"Mejorar: ${cost}", True, color)
                    surface.blit(cost_surf, (self.sidebar_rect.x + 20, info_y + 88))

        # Dibujar overlays según estado
        if self.paused:
            self.draw_pause_overlay(surface)
        elif self.game_over:
            self.draw_game_over_overlay(surface)
        elif self.wave_manager.victory:
            self.draw_victory_overlay(surface)

    def draw_pause_overlay(self, surface):
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_big = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 72)
        text = font_big.render("PAUSA", True, c.COLOUR_CREAM)
        text_rect = text.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 100))
        surface.blit(text, text_rect)

        for btn in self.pause_buttons:
            btn.draw(surface)

    def draw_game_over_overlay(self, surface):
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_big = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 72)
        text = font_big.render("GAME OVER", True, c.COLOUR_RED)
        text_rect = text.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 130))
        surface.blit(text, text_rect)

        # Calcular tiempo jugado (usando end_time fijo)
        if self.end_time > 0 and self.start_time > 0:
            elapsed = (self.end_time - self.start_time) / 1000.0
        else:
            elapsed = 0

        # Actualizar estadísticas (solo para mostrarlas)
        self.stats["time_played"] = elapsed
        self.stats["waves_completed"] = self.wave_manager.wave_number


        # Mostrar estadísticas
        font_small = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 28)
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

        # Botones
        for btn in self.end_buttons.values():
            btn.draw(surface)

    def draw_victory_overlay(self, surface):
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        font_big = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 72)
        text = font_big.render("VICTORIA!", True, c.COLOUR_GREEN)
        text_rect = text.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 130))
        surface.blit(text, text_rect)


        # Calcular tiempo jugado (usando end_time fijo)
        if self.end_time > 0 and self.start_time > 0:
            elapsed = (self.end_time - self.start_time) / 1000.0
        else:
            elapsed = 0

        # Actualizar estadísticas (solo para mostrarlas)
        self.stats["time_played"] = elapsed
        self.stats["waves_completed"] = self.wave_manager.wave_number
        
        # Mostrar estadísticas
        font_small = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 28)
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

        # Botones
        for btn in self.end_buttons.values():
            btn.draw(surface)

    def optimize_images(self):
        self.level.image = self.level.image.convert()
        self.level.select_tile_img = self.level.select_tile_img.convert_alpha()
        self.enemy1_img = self.enemy1_img.convert_alpha()
        self.enemy2_img = self.enemy2_img.convert_alpha()
        self.enemy3_img = self.enemy3_img.convert_alpha()
        self.sidebar_img = self.sidebar_img.convert()

        for turret in self.turret_images:
            self.turret_images[turret].convert_alpha()
