"""
Renderer - Sistema de Renderizado
==================================
Maneja todo el dibujado del juego: UI, unidades, efectos, etc.
"""
import pygame
from config.constants import *


class GameRenderer:
    """Renderiza todos los elementos del juego."""
    
    def __init__(self, screen, font_large, font_medium, font_small):
        self.screen = screen
        self.font_large = font_large
        self.font_medium = font_medium
        self.font_small = font_small
    
    def clear_screen(self):
        """Limpia la pantalla con color de fondo."""
        self.screen.fill(COLOR_BG)
    
    def draw_background(self, grass_system, neutral_zone_y):
        """Dibuja el fondo y zonas."""
        grass_system.draw(self.screen)
        
        # Zona de juego
        pygame.draw.rect(self.screen, (30, 40, 35), 
                        (0, ZONE_ENEMY_Y - 30, SCREEN_WIDTH, 
                         ZONE_PLAYER_Y - ZONE_ENEMY_Y + GRID_ROWS * HEX_HEIGHT + 100))
        
        # Línea neutral
        pygame.draw.line(self.screen, COLOR_HONEY_BORDER, 
                        (50, neutral_zone_y), (SCREEN_WIDTH-50, neutral_zone_y), 4)
        
        # Etiquetas de zona
        self.screen.blit(self.font_medium.render("ZONA ENEMIGA", True, (255, 150, 150)), 
                        (SCREEN_WIDTH//2 - 100, ZONE_ENEMY_Y - 45))
        self.screen.blit(self.font_medium.render("TU ZONA", True, (150, 255, 150)), 
                        (SCREEN_WIDTH//2 - 60, ZONE_PLAYER_Y + GRID_ROWS * HEX_HEIGHT + 25))
    
    def draw_grid(self, grid_manager):
        """Dibuja el grid hexagonal."""
        tiles = grid_manager.get_tiles_sorted_by_y()
        for tile in tiles:
            tile.draw(self.screen)
    
    def draw_units_and_towers(self, grid_manager):
        """Dibuja todas las unidades y torres."""
        items = grid_manager.get_all_units_and_towers(sorted_by_y=True)
        
        for y_pos, obj, tile in items:
            if hasattr(obj, 'is_moving'):
                if obj.is_moving:
                    obj.draw(self.screen, obj.visual_x, obj.visual_y + tile.wall_height//2)
                else:
                    obj.draw(self.screen, tile.x, tile.y + tile.wall_height//2)
            else:
                obj.draw(self.screen, tile.x, tile.y + tile.wall_height//2)
    
    def draw_projectiles(self, projectiles):
        """Dibuja los proyectiles."""
        for proj in projectiles:
            proj.draw(self.screen)
    
    def draw_particles(self, particle_system):
        """Dibuja el sistema de partículas."""
        particle_system.draw(self.screen)
    
    def draw_ui(self, turn_system, unit_manager, selected_tile, oracle, menu):
        """Dibuja la interfaz de usuario principal."""
        # Panel superior
        self._draw_top_panel(turn_system, unit_manager)
        
        # Mensaje de ayuda
        self._draw_help_text(turn_system)
        
        # Oracle y menú
        oracle.draw(self.screen, self.font_small)
        menu.draw(self.screen, self.font_small)
        
        # Info de unidad seleccionada
        if selected_tile and selected_tile.unit:
            self._draw_unit_info(selected_tile.unit)
    
    def _draw_top_panel(self, turn_system, unit_manager):
        """Dibuja el panel superior con información del turno."""
        # Fondo del panel
        panel_top = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        pygame.draw.rect(panel_top, (20, 25, 35, 240), (0, 0, SCREEN_WIDTH, 60))
        self.screen.blit(panel_top, (0, 0))
        
        # Info de fase
        phase_name = turn_system.get_phase_name()
        phase_color = turn_system.get_phase_color()
        
        # Ronda y estado
        self.screen.blit(self.font_medium.render(f"Ronda {turn_system.turn_number} - {phase_name}", 
                                                True, phase_color), (20, 8))
        
        # Info de unidad activa
        active = turn_system.active_unit
        if active:
            is_hero = getattr(active, 'is_hero', False)
            name = getattr(active, 'name', getattr(active, 'unit_type', 'Unidad'))
            name_color = (255, 215, 0) if is_hero else \
                        (100, 255, 100) if turn_system.is_troop_turn() else (255, 100, 100)
            
            name_text = f"Activa: {name}"
            self.screen.blit(self.font_small.render(name_text, True, name_color), (20, 38))
            
            # AP solo para héroe
            if is_hero and hasattr(active, 'action_points'):
                ap = active.action_points
                ap_color = (100, 255, 100) if ap.current >= 4 else \
                          (255, 255, 100) if ap.current >= 2 else (255, 100, 100)
                ap_text = f"AP: {ap.current}/{ap.maximum}"
                self.screen.blit(self.font_medium.render(ap_text, True, ap_color), (300, 8))
        
        # Panel derecho (stats)
        px = SCREEN_WIDTH - 180
        pygame.draw.rect(self.screen, (30, 35, 45), (px, 5, 170, 50))
        alive_p = len(unit_manager.get_alive_player_units())
        alive_e = len(unit_manager.get_alive_enemy_units())
        self.screen.blit(self.font_small.render(f"Aliados: {alive_p}", True, (100, 255, 100)), (px+10, 10))
        self.screen.blit(self.font_small.render(f"Enemigos: {alive_e}", True, (255, 100, 100)), (px+10, 30))
    
    def _draw_help_text(self, turn_system):
        """Dibuja el texto de ayuda contextual."""
        help_y = 65
        
        if turn_system.is_hero_turn():
            msg = "HÉROE: Click=Mover(gratis) | Click enemigo=Ataque básico | Menú=Poderes especiales"
        elif turn_system.is_troop_turn():
            msg = "TROPA: Click=Mover | Click enemigo=Atacar | ESPACIO=Terminar"
        elif turn_system.is_enemy_turn():
            msg = "El enemigo está actuando..."
        else:
            msg = ""
        
        if msg:
            self.screen.blit(self.font_small.render(msg, True, (200, 220, 255)), (20, help_y))
    
    def _draw_unit_info(self, unit):
        """Dibuja la información de la unidad seleccionada."""
        x = 20
        y = SCREEN_HEIGHT - 140
        
        # Panel de fondo
        is_hero = getattr(unit, 'is_hero', False)
        panel_h = 140 if is_hero else 110
        pygame.draw.rect(self.screen, (20, 25, 35, 200), (x-10, y-5, 180, panel_h))
        
        # Título
        title_color = (255, 215, 0) if is_hero else \
                     (100, 255, 100) if unit.owner == "player" else (255, 100, 100)
        title = f"{'★ ' if is_hero else ''}{unit.unit_type.upper()}"
        self.screen.blit(self.font_small.render(title, True, title_color), (x, y))
        
        # Info básica
        info_lines = [
            f"Salud: {unit.health}/{unit.max_health}",
            f"Ataque: {unit.attack}",
            f"Rango: {unit.range}",
            f"Velocidad: {unit.speed}",
        ]
        
        # Solo mostrar AP si es el héroe
        if is_hero and hasattr(unit, 'action_points'):
            ap = unit.action_points
            info_lines.append(f"AP: {ap.current}/{ap.maximum}")
            
            # Barra de AP visual
            bar_w = 100
            bar_ratio = ap.current / ap.maximum
            bar_color = (100, 255, 100) if bar_ratio > 0.4 else \
                       (255, 255, 100) if bar_ratio > 0.2 else (255, 100, 100)
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y + 110, bar_w, 8))
            pygame.draw.rect(self.screen, bar_color, (x, y + 110, bar_w * bar_ratio, 8))
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y + 110, bar_w, 8), 1)
        
        for i, text in enumerate(info_lines):
            self.screen.blit(self.font_small.render(text, True, (220, 220, 220)), (x, y + 22 + i*20))
    
    def draw_victory_screen(self, btn_restart):
        """Dibuja la pantalla de victoria."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 100, 0, 150), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        self.screen.blit(self.font_large.render("¡VICTORIA!", True, (255, 215, 0)), 
                        (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
        
        self.screen.blit(self.font_medium.render("Has derrotado a todos los enemigos", True, (255, 255, 200)), 
                        (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 + 10))
        
        btn_restart.draw(self.screen, self.font_small)
    
    def draw_defeat_screen(self, btn_restart):
        """Dibuja la pantalla de derrota."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (100, 0, 0, 150), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        self.screen.blit(self.font_large.render("DERROTA", True, (255, 100, 100)), 
                        (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
        
        self.screen.blit(self.font_medium.render("Tus fuerzas han caído", True, (255, 200, 200)), 
                        (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 + 30))
        
        btn_restart.draw(self.screen, self.font_small)
    
    def flip_display(self):
        """Actualiza la pantalla."""
        pygame.display.flip()
