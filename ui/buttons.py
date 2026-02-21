"""
Botones y UI del juego
"""
import pygame
import math


class OracleOfKimi:
    """Oráculo que recomienda movimientos"""
    
    def __init__(self):
        self.advice = ""
        self.recommended_tile = None
    
    def analyze_battlefield(self, selected_unit, selected_tile, grid, player_units, enemy_units):
        from config.constants import ZONE_ENEMY_Y
        
        self.recommended_tile = None
        
        if not selected_unit or not selected_tile:
            self.advice = "Selecciona una unidad"
            return
        
        neighbors = selected_tile.get_neighbors(grid)
        valid_moves = [n for n in neighbors if n.is_empty()]
        
        if not valid_moves:
            self.advice = "Sin movimientos disponibles"
            return
        
        best_score = -float('inf')
        best_tile = None
        
        for move_tile in valid_moves:
            score = 0
            
            for enemy in enemy_units:
                if not enemy.is_alive():
                    continue
                
                enemy_tile = None
                for t in grid.values():
                    if getattr(t, 'unit', None) == enemy:
                        enemy_tile = t
                        break
                
                if enemy_tile:
                    dist = math.sqrt((move_tile.x - enemy_tile.x)**2 + 
                                   (move_tile.y - enemy_tile.y)**2)
                    attack_range = selected_unit.get_attack_range_pixels()
                    
                    if dist <= attack_range:
                        score += 200 + enemy.attack * 2
                    else:
                        score += max(0, 100 - dist/5)
            
            health_ratio = selected_unit.health / selected_unit.max_health
            if health_ratio < 0.5:
                score -= 50
            
            if selected_unit.unit_type == "sniper":
                score += 80
            elif selected_unit.unit_type == "berserker":
                score += 60
            
            dist_to_enemy_zone = abs(move_tile.y - ZONE_ENEMY_Y)
            score += (500 - dist_to_enemy_zone) / 10
            
            if score > best_score:
                best_score = score
                best_tile = move_tile
        
        if best_tile:
            self.recommended_tile = best_tile
            best_tile.oracle_recommended = True
            self.advice = "¡Mueve a la casilla DORADA!"
        else:
            self.advice = "Posición defensiva recomendada"
            if valid_moves:
                self.recommended_tile = valid_moves[0]
                self.recommended_tile.oracle_recommended = True
    
    def clear_recommendation(self, grid):
        for tile in grid.values():
            tile.oracle_recommended = False
        self.recommended_tile = None
    
    def draw(self, screen, font):
        from config.constants import SCREEN_WIDTH, COLOR_HONEY_BORDER
        
        if not self.advice:
            return
        
        panel_x = SCREEN_WIDTH // 2 - 220
        panel_y = 110
        
        panel = pygame.Surface((440, 70), pygame.SRCALPHA)
        pygame.draw.rect(panel, (40, 30, 10, 220), (0, 0, 440, 70), border_radius=10)
        pygame.draw.rect(panel, COLOR_HONEY_BORDER, (0, 0, 440, 70), 3, border_radius=10)
        screen.blit(panel, (panel_x, panel_y))
        
        star_points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = 15 if i % 2 == 0 else 8
            sx = panel_x + 30 + radius * math.cos(angle)
            sy = panel_y + 35 + radius * math.sin(angle)
            star_points.append((sx, sy))
        pygame.draw.polygon(screen, COLOR_HONEY_BORDER, star_points)
        pygame.draw.polygon(screen, (255, 255, 200), star_points, 2)
        
        text = font.render("KIMI:", True, COLOR_HONEY_BORDER)
        screen.blit(text, (panel_x + 55, panel_y + 8))
        
        text = font.render(self.advice, True, (255, 255, 220))
        screen.blit(text, (panel_x + 55, panel_y + 35))


class StyledButton:
    """Botón estilizado"""
    
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.hovered = False
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if self.action:
                self.action()
            return True
        return False
    
    def draw(self, screen, font):
        color = self.hover_color if self.hovered else self.color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
