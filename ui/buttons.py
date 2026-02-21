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
    """Botón estilizado con animaciones"""
    
    # Color tema del juego - Azul acero dorado
    COLOR_BASE = (45, 55, 75)        # Azul oscuro acero
    COLOR_HOVER = (65, 85, 115)      # Azul más claro
    COLOR_ACTIVE = (85, 115, 155)    # Azul brillante
    COLOR_BORDER = (218, 165, 32)    # Dorado
    COLOR_TEXT = (240, 240, 220)     # Blanco hueso
    
    def __init__(self, x, y, width, height, text, action=None, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.icon = icon  # Emoji o símbolo opcional
        
        # Estado
        self.hovered = False
        self.pressed = False
        self.press_anim = 0.0  # Animación de presión 0-1
        self.hover_anim = 0.0  # Animación de hover 0-1
        
        # Efectos
        self.glow_intensity = 0.0
        
    def update(self, mouse_pos, dt=0.016):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        # Animación de hover suave
        target_hover = 1.0 if self.hovered else 0.0
        self.hover_anim += (target_hover - self.hover_anim) * 10 * dt
        
        # Animación de presión
        target_press = 1.0 if self.pressed else 0.0
        self.press_anim += (target_press - self.press_anim) * 15 * dt
        
        # Glow pulsante cuando está hovered
        if self.hovered:
            self.glow_intensity = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2 * 0.5 + 0.5
        else:
            self.glow_intensity = 0.0
    
    def handle_click(self, mouse_pos, pressed=True):
        if self.rect.collidepoint(mouse_pos):
            if pressed:
                self.pressed = True
            else:
                # Release - ejecutar acción
                self.pressed = False
                if self.action:
                    self.action()
                    return True
        else:
            self.pressed = False
        return False
    
    def draw(self, screen, font):
        import pygame
        
        # Offset por animación de presión
        press_offset = int(self.press_anim * 3)
        
        # Rectángulo con animación
        anim_rect = self.rect.copy()
        anim_rect.y += press_offset
        
        # Glow exterior cuando hovered
        if self.hover_anim > 0.1:
            glow_color = (*self.COLOR_BORDER[:3], int(self.hover_anim * 100))
            for i in range(3, 0, -1):
                glow_rect = anim_rect.inflate(i*4, i*4)
                pygame.draw.rect(screen, glow_color, glow_rect, border_radius=10)
        
        # Color base interpolado
        base = self._lerp_color(self.COLOR_BASE, self.COLOR_HOVER, self.hover_anim)
        active = self._lerp_color(base, self.COLOR_ACTIVE, self.press_anim)
        
        # Fondo del botón
        pygame.draw.rect(screen, active, anim_rect, border_radius=8)
        
        # Borde dorado brillante
        border_alpha = 150 + int(self.hover_anim * 105)
        border_color = (*self.COLOR_BORDER[:3], border_alpha)
        pygame.draw.rect(screen, border_color, anim_rect, 2, border_radius=8)
        
        # Línea decorativa superior
        line_y = anim_rect.y + 4
        pygame.draw.line(screen, (255, 255, 255, 80), 
                        (anim_rect.x + 8, line_y), 
                        (anim_rect.right - 8, line_y), 1)
        
        # Texto centrado con truncamiento inteligente
        display_text = self.text
        text_surf = font.render(display_text, True, self.COLOR_TEXT)
        
        # Truncar si es muy largo
        max_width = anim_rect.width - 20
        if text_surf.get_width() > max_width:
            while len(display_text) > 3 and font.render(display_text + "...", True, self.COLOR_TEXT).get_width() > max_width:
                display_text = display_text[:-1]
            display_text = display_text + "..."
            text_surf = font.render(display_text, True, self.COLOR_TEXT)
        
        # Centrar texto
        text_rect = text_surf.get_rect(center=anim_rect.center)
        text_rect.y -= 1  # Ajuste fino
        screen.blit(text_surf, text_rect)
    
    def _lerp_color(self, c1, c2, t):
        """Interpolación lineal entre colores."""
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


class PersistentMenu:
    """Menú persistente a la izquierda con estilo unificado"""
    
    COLOR_BG = (25, 30, 40, 230)
    COLOR_BORDER = (218, 165, 32)
    
    def __init__(self, x=20, y=100, width=160):
        self.x = x
        self.y = y
        self.width = width
        self.buttons = []
        self.visible = True
        self.title = "ACCIONES"
        self.anim_offset = 0.0
        
    def clear(self):
        self.buttons = []
        
    def add_button(self, text, action, enabled=True):
        """Agrega un botón al menú."""
        height = 38
        spacing = 6
        y_pos = self.y + 40 + len(self.buttons) * (height + spacing)
        
        btn = StyledButton(
            self.x, y_pos, self.width, height, 
            text, action=action if enabled else None
        )
        btn.enabled = enabled
        self.buttons.append(btn)
        return btn
    
    def update(self, mouse_pos, dt=0.016):
        """Actualiza todos los botones."""
        # Animación de entrada
        target = 0.0 if self.visible else -20.0
        self.anim_offset += (target - self.anim_offset) * 10 * dt
        
        for btn in self.buttons:
            btn.update(mouse_pos, dt)
    
    def handle_click(self, mouse_pos, pressed=True):
        """Maneja clicks en los botones."""
        for btn in self.buttons:
            if btn.handle_click(mouse_pos, pressed):
                return btn.action
        return None
    
    def draw(self, screen, font):
        if not self.visible:
            return
        
        import pygame
        
        # Fondo del panel
        total_height = 50 + len(self.buttons) * 44
        panel = pygame.Surface((self.width + 20, total_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, self.COLOR_BG, (0, 0, self.width + 20, total_height), border_radius=10)
        pygame.draw.rect(panel, self.COLOR_BORDER, (0, 0, self.width + 20, total_height), 2, border_radius=10)
        screen.blit(panel, (self.x - 10, self.y - 10))
        
        # Título
        title_surf = font.render(self.title, True, self.COLOR_BORDER)
        screen.blit(title_surf, (self.x, self.y - 5))
        
        # Línea separadora
        pygame.draw.line(screen, self.COLOR_BORDER, 
                        (self.x, self.y + 20), 
                        (self.x + self.width, self.y + 20), 2)
        
        # Botones
        for btn in self.buttons:
            btn.draw(screen, font)
