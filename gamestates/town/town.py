# Módulos de python.
import sys, os, json
from typing import List, Dict

# Módulos de pygame.
import pygame as pg
from pygame.locals import *

# Módulos custom.
from classes.state_machine import State, StateMachine
from classes.gui import Button
from utils import constants as c

class Town(State):
    def __init__(self, parent_state_machine, save_data=None, save_slot=None, sound_manager=None) -> None:
        self.sound_manager = sound_manager
        self.save_slot = save_slot
        self.parent_state_machine = parent_state_machine

        # Dimensiones del pueblo (20x15 casillas de 48x48)
        self.grid_width = 20
        self.grid_height = 15
        self.tile_size = c.TILE_SIZE  # 48

        # Estado del pomodoro
        self.pomodoro_active = False      # True si el temporizador está en ejecución (no pausado)
        self.pomodoro_paused = False      # True si está en pausa
        self.pomodoro_remaining = 0       # tiempo restante en segundos
        self.pomodoro_elapsed = 0.0
        
        # Cargar imágenes del pueblo (fondo, edificios, sidebar)
        self.background = pg.image.load("assets/town/town_background.png")
        self.sidebar_img = pg.image.load("assets/town/sidebar.png")

        self.building_images = {
            "wheat_field": pg.image.load("assets/town/wheat_field.png"),
            "smithing_house": pg.image.load("assets/town/smithing_house.png"),
            "shooting_range": pg.image.load("assets/town/shooting_range.png")
        }

        self.building_positions = {
            "wheat_field": (12.2, 9),
            "smithing_house": (1.85 , 5),
            "shooting_range": (13, 0)           
        }

        self.building_rects = {}
        for name, (gx, gy) in self.building_positions.items():
            img = self.building_images[name]
            rect = img.get_rect()
            rect.topleft = (gx * self.tile_size, gy * self.tile_size)
            self.building_rects[name] = rect

        # Posición de la sidebar (similar a tower defence)
        self.sidebar_rect = self.sidebar_img.get_rect()
        self.sidebar_rect.topleft = (self.grid_width * self.tile_size, 0)

        # Fuentes
        self.font = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 20)
        self.font_big = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 27)

        # Recursos iniciales (si es nueva partida)
        if save_data is None:
            self.money = 0          # Oro ganado en defensas
            self.time_units = 0     # Unidades de tiempo (pomodoros completados)
            self.buildings = {
                "wheat_field":    {"level": 0, "cost_gold": 100, "cost_time": 1},
                "smithing_house": {"level": 0, "cost_gold": 150, "cost_time": 1},
                "shooting_range": {"level": 0, "cost_gold": 200, "cost_time": 2}
            }
        else:
            # Cargar datos guardados
            self.money = save_data.get("money", 0)
            self.time_units = save_data.get("time_units", 0)
            self.buildings = save_data.get("buildings", {})

        # Temporizador pomodoro (25 minutos = 1500 segundos)
        self.pomodoro_duration = 25 * 60  # en segundos

        # Edificio seleccionado (para mejora)
        self.selected_building = None

        # Crear botones de la sidebar
        self.create_buttons()
        
    def create_buttons(self):
        btn_w, btn_h = 160, 33
        x = self.sidebar_rect.x + 20

        # Sección central: información y botón de mejora
        self.info_y_start = 325
        self.upgrade_btn = Button(
            x, self.info_y_start + 107, btn_w - 30, btn_h,
            c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
            self.font, "Mejorar", radius=5
        )

        # Sección inferior: botones de control
        control_y = 600
        self.pomodoro_btn = Button(
            x, control_y, btn_w, btn_h,
            c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
            self.font, "Iniciar Pomodoro", radius=5
        )
        
        self.start_defense_btn = Button(
            x, control_y + 50, btn_w, btn_h,
            c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
            self.font, "Iniciar Defensa", radius=5
        )

        # Botones del overlay del pomodoro (centrados)
        overlay_btn_w, overlay_btn_h = 200, 50
        center_x = c.WIN_WIDTH // 2
        center_y = c.WIN_HEIGHT // 2

        self.pomodoro_pause_btn = Button(
            center_x - overlay_btn_w - 10, center_y + 50, overlay_btn_w, overlay_btn_h,
            c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
            self.font, "Pausar", radius=5
        )
        self.pomodoro_cancel_btn = Button(
            center_x + 10, center_y + 50, overlay_btn_w, overlay_btn_h,
            c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
            self.font, "Cancelar", radius=5
        )

        # Botón de regresar (esquina superior izquierda)
        self.return_btn = Button(
            10, 10, 120, 40,
            c.COLOUR_BROWN, c.COLOUR_CREAM, c.COLOUR_DARK_BROWN,
            self.font, "Regresar", radius=5
        )

    def start_pomodoro(self):
        self.pomodoro_active = True
        self.pomodoro_paused = False
        self.pomodoro_elapsed = 0.0
        self.pomodoro_remaining = self.pomodoro_duration
        self.pomodoro_btn.set_caption("Pomodoro en curso", self.font)
        self.pomodoro_pause_btn.set_caption("Pausar", self.font)  # Asegurar texto inicial

    def pause_pomodoro(self):
        if self.pomodoro_active and not self.pomodoro_paused:
            self.pomodoro_paused = True
            self.pomodoro_pause_btn.set_caption("Reanudar", self.font)

    def resume_pomodoro(self):
        if self.pomodoro_active and self.pomodoro_paused:
            self.pomodoro_paused = False
            self.pomodoro_pause_btn.set_caption("Pausar", self.font)

    def cancel_pomodoro(self):
        self.pomodoro_active = False
        self.pomodoro_paused = False
        self.pomodoro_elapsed = 0.0
        self.pomodoro_remaining = 0
        self.pomodoro_btn.set_caption("Iniciar Pomodoro", self.font)

    def complete_pomodoro(self):
        self.sound_manager.play_sound("notification")
        self.time_units += 1
        self.pomodoro_active = False
        self.pomodoro_paused = False
        self.pomodoro_elapsed = 0.0
        self.pomodoro_remaining = 0
        self.pomodoro_btn.set_caption("Iniciar Pomodoro", self.font)
        print("¡Pomodoro completado! +1 unidad de tiempo")
        self.save_current_state()

        
    def handle_events(self, events: List[pg.event.Event]) -> None:
        for event in events:
            if event.type == MOUSEBUTTONUP and event.button == 1:
                if self.return_btn.is_hovered:
                    self.sound_manager.play_sound("click")
                    self.parent_state_machine.current_state = "main_menu"
                    self.save_current_state()
                    return
                
                if self.pomodoro_active:
                    # Botones del overlay
                    if self.pomodoro_pause_btn.is_hovered:
                        self.sound_manager.play_sound("click")
                        if self.pomodoro_paused:
                            self.resume_pomodoro()
                        else:
                            self.sound_manager.play_sound("click")
                            self.pause_pomodoro()
                    elif self.pomodoro_cancel_btn.is_hovered:
                        self.sound_manager.play_sound("click")
                        self.cancel_pomodoro()
                else:
                    # Detectar clics en el mapa (edificios)
                    if event.pos[0] < self.grid_width * self.tile_size:
                        self.handle_building_click(event.pos)
                    else:
                        # Clic en la sidebar
                        self.handle_sidebar_click(event.pos)

            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    # Volver al menú principal (o pausa)
                    if self.pomodoro_active:
                        self.cancel_pomodoro()

    def handle_building_click(self, pos):
        for name, rect in self.building_rects.items():
            if rect.collidepoint(pos):
                self.sound_manager.play_sound("click")
                self.selected_building = name
                return
            self.selected_building = None

    def handle_sidebar_click(self, pos):
        if self.start_defense_btn.rect.collidepoint(pos):
            self.sound_manager.play_sound("click")
            self.start_defense()
        elif self.upgrade_btn.rect.collidepoint(pos):
            self.sound_manager.play_sound("click")
            self.upgrade_selected_building()
        elif self.pomodoro_btn.rect.collidepoint(pos):
            self.sound_manager.play_sound("click")
            if not self.pomodoro_active:
                self.start_pomodoro()

    def start_defense(self):
        multipliers = self.get_upgrade_multipliers()
        td = self.parent_state_machine.states["tower_defence"]
        td.set_multipliers(multipliers)
        td.set_initial_money(200)
        
        self.parent_state_machine.current_state = "tower_defence"

    def upgrade_selected_building(self):
        if self.selected_building is None:
            return
        building = self.buildings[self.selected_building]
        cost_gold = building["cost_gold"]
        cost_time = building["cost_time"]
        if self.money >= cost_gold and self.time_units >= cost_time:
            self.money -= cost_gold
            self.time_units -= cost_time
            building["level"] += 1
            # Aumentar costo para la siguiente mejora (opcional)
            building["cost_gold"] = int(building["cost_gold"] * 1.5)
            building["cost_time"] += 1
            print(f"{self.selected_building} mejorado a nivel {building['level']}")
            self.save_current_state()

    def update(self, dt: float) -> None:
        # Actualizar temporizador pomodoro
        if self.pomodoro_active and not self.pomodoro_paused:
            self.pomodoro_elapsed += dt
            self.pomodoro_remaining = self.pomodoro_duration - self.pomodoro_elapsed
            if self.pomodoro_remaining <= 0:
                self.complete_pomodoro()

        # Actualizar estado de los botones (hover)
        self.start_defense_btn.update()
        self.upgrade_btn.update()
        self.pomodoro_btn.update()
        self.return_btn.update()
        
        if self.pomodoro_active:
            self.pomodoro_pause_btn.update()
            self.pomodoro_cancel_btn.update()

        reward = self.parent_state_machine.shared_data.get("defense_reward", 0)
        if reward != 0:
            self.money += reward
            self.parent_state_machine.shared_data['defense_reward'] = 0
            print(f"¡Recibiste {reward} oro de la defensa!")
            self.save_current_state()

    def draw_pomodoro_overlay(self, surface):
        """Dibuja la superposición del pomodoro."""
        # Fondo semitransparente
        overlay = pg.Surface((c.WIN_WIDTH, c.WIN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Tiempo restante grande
        minutes = int(self.pomodoro_remaining // 60)
        seconds = int(self.pomodoro_remaining % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        font_big = pg.font.Font("assets/fonts/PirataOne-Regular.ttf", 72)
        time_surf = font_big.render(time_str, True, c.COLOUR_CREAM)
        time_rect = time_surf.get_rect(center=(c.WIN_WIDTH // 2, c.WIN_HEIGHT // 2 - 50))
        surface.blit(time_surf, time_rect)

        # Botones
        self.pomodoro_pause_btn.draw(surface)
        self.pomodoro_cancel_btn.draw(surface)
        
    def draw(self, surface: pg.Surface) -> None:
        # Dibujar fondo del pueblo
        surface.blit(self.background, (0, 0))

        # Dibujar edificios
        for name, (gx, gy) in self.building_positions.items():
            img = self.building_images[name]
            rect = img.get_rect(topleft=(gx * self.tile_size, gy * self.tile_size))
            surface.blit(img, rect)

            # Mostrar nivel
            level = self.buildings[name]["level"]
            level_text = self.font.render(str(level), True, c.COLOUR_WHITE)
            level_rect = level_text.get_rect(center=rect.center)
            surface.blit(level_text, level_rect)

        # Resaltar edificio seleccionado
        if self.selected_building:
            gx, gy = self.building_positions[self.selected_building]
            rect = self.building_rects[self.selected_building]
            pg.draw.rect(surface, c.COLOUR_GREEN, rect, 3)

        # Dibujar botón de regresar (siempre visible)
        self.return_btn.draw(surface)
            
        # Dibujar sidebar
        surface.blit(self.sidebar_img, self.sidebar_rect)

        # --- Sección Estadísticas ---
        stats_label = self.font_big.render("Estadísticas", True, c.COLOUR_CREAM)
        surface.blit(stats_label, (self.sidebar_rect.x + 103, 32))

        # Recursos
        money_text = self.font.render(f"Oro: {self.money}", True, c.COLOUR_BLACK)
        surface.blit(money_text, (self.sidebar_rect.x + 20, 80))
        time_text = self.font.render(f"Tiempo: {self.time_units}", True, c.COLOUR_BLACK)
        surface.blit(time_text, (self.sidebar_rect.x + 20, 100))

        # --- Sección Edificios ---
        buildings_label = self.font_big.render("Edificios", True, c.COLOUR_CREAM)
        surface.blit(buildings_label, (self.sidebar_rect.x + 118, self.info_y_start - 52))

        # Sección central: información del edificio seleccionado
        if self.selected_building:
            b = self.buildings[self.selected_building]
            # Nombre bonito
            building_names = {
                "wheat_field": "Campo de Trigo",
                "smithing_house": "Herrería",
                "shooting_range": "Campo de Tiro"
            }
            name_str = building_names.get(self.selected_building, self.selected_building)
            name_surf = self.font.render(name_str, True, c.COLOUR_BLACK)
            surface.blit(name_surf, (self.sidebar_rect.x + 20, self.info_y_start))

            # Nivel
            level_surf = self.font.render(f"Nivel: {b['level']}", True, c.COLOUR_BLACK)
            surface.blit(level_surf, (self.sidebar_rect.x + 20, self.info_y_start + 25))

            # Efecto
            effects = {
                "wheat_field": "Reduce costo de compra de torretas",
                "smithing_house": "Reduce costo de mejora de torretas",
                "shooting_range": "Aumenta cadencia y daño de torretas"
            }
            effect_surf = self.font.render(effects[self.selected_building], True, c.COLOUR_BLACK)
            surface.blit(effect_surf, (self.sidebar_rect.x + 20, self.info_y_start + 50))

            # Costo de mejora
            cost_surf = self.font.render(f"Costo: ${b['cost_gold']} + {b['cost_time']}t", True, c.COLOUR_BLACK)
            surface.blit(cost_surf, (self.sidebar_rect.x + 20, self.info_y_start + 75))

            # Texto del efecto a la derecha del botón
            effect_x = self.upgrade_btn.rect.right + 10
            effect_y = self.upgrade_btn.rect.centery - 10  # centrado verticalmente
            
            if self.selected_building == "wheat_field":
                effect_text = f"{-b['level'] + 1 * 5}% costo compra"
            elif self.selected_building == "smithing_house":
                effect_text = f"{-b['level'] + 1 * 5}% costo mejora"
            elif self.selected_building == "shooting_range":
                effect_text = f"CD {-b['level'] + 1 * 3}% | Daño +{b['level']*2}%"
            effect_surf = self.font.render(effect_text, True, c.COLOUR_BLACK)
            surface.blit(effect_surf, (self.sidebar_rect.x + 160, self.info_y_start + 110))

            
            # Botón de mejorar
            self.upgrade_btn.draw(surface)
        else:
            # Mensaje si no hay selección
            msg_surf = self.font.render("Selecciona un edificio...", True, c.COLOUR_BLACK)
            surface.blit(msg_surf, (self.sidebar_rect.x + 20, self.info_y_start))

        # --- Sección Selección de Fase ---
        phase_label = self.font_big.render("Selección de fase", True, c.COLOUR_CREAM)
        surface.blit(phase_label, (self.sidebar_rect.x + 77, 512))  # Ajusta según control_y
        
        # Botones de control (siempre visibles)
        self.pomodoro_btn.draw(surface)
        self.start_defense_btn.draw(surface)

        # Si el pomodoro está activo, dibujar el overlay encima de todo
        if self.pomodoro_active:
            self.draw_pomodoro_overlay(surface)

    def get_save_data(self):
        return {
            "money": self.money,
            "time_units": self.time_units,
            "buildings": self.buildings
        }

    def get_upgrade_multipliers(self):
        wheat_level = self.buildings["wheat_field"]["level"]
        smith_level = self.buildings["smithing_house"]["level"]
        range_level = self.buildings["shooting_range"]["level"]
        return {
            "purchase_cost": 1 - (wheat_level * 0.05),
            "upgrade_cost": 1 - (smith_level * 0.05),
            "cooldown": 1 - (range_level * 0.03),
            "damage": 1 + (range_level * 0.02)
        }
    def save_current_state(self):
        if self.save_slot is None:
            return
        os.makedirs(c.SAVE_DIR, exist_ok=True)
        data = self.get_save_data()
        with open(os.path.join(c.SAVE_DIR, f"save{self.save_slot}.json"), 'w') as f:
            json.dump(data, f, indent=4)
