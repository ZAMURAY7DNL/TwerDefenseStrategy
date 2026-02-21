"""
Unidades del juego
"""
import pygame
import random
import math
from systems.geometry import GeometricUnit


class UltraUnit:
    """Unidad del juego con sistema visual avanzado"""
    
    def __init__(self, unit_type, owner, name=""):
        self.unit_type = unit_type
        self.owner = owner
        self.name = name or f"Unit_{random.randint(1000,9999)}"
        
        if unit_type == "berserker":
            self.max_health = 120
            self.attack = 50
            self.speed = 2
            self.range = 1
            
        elif unit_type == "assault":
            self.max_health = 100
            self.attack = 40
            self.speed = 3
            self.range = 2
            
        elif unit_type == "ranger":
            self.max_health = 90
            self.attack = 30
            self.speed = 2
            self.range = 3
            
        elif unit_type == "sniper":
            self.max_health = 70
            self.attack = 20
            self.speed = 2
            self.range = 5
        
        self.health = self.max_health
        self.visual_x = 0
        self.visual_y = 0
        self.target_x = 0
        self.target_y = 0
        
        self.has_moved = False
        self.can_act = True
        self.animation_time = 0
        self.is_moving = False
        self.bounce_offset = 0
        self.footstep_timer = 0
        
        self.attack_cooldown = 0
        self.attack_speed = 0.4
        
        # Renderer geométrico detallado
        self._geo_renderer = GeometricUnit(unit_type, owner)
    
    def set_position(self, x, y):
        self.visual_x = x
        self.visual_y = y
        self.target_x = x
        self.target_y = y
    
    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y
        self.has_moved = True
        self.is_moving = True
        self.animation_time = 0
    
    def update(self, dt, grass_system=None):
        if self.is_moving:
            dx = self.target_x - self.visual_x
            dy = self.target_y - self.visual_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 2:
                self.visual_x = self.target_x
                self.visual_y = self.target_y
                self.is_moving = False
                self.bounce_offset = 0
            else:
                speed = 250 * dt
                self.visual_x += (dx / distance) * min(speed, distance)
                self.visual_y += (dy / distance) * min(speed, distance)
                
                self.animation_time += dt * 12
                self.bounce_offset = abs(math.sin(self.animation_time)) * -8
                
                self.footstep_timer += dt
                if self.footstep_timer > 0.3 and grass_system:
                    grass_system.add_footstep_wave(self.visual_x, self.visual_y + 10)
                    self.footstep_timer = 0
        else:
            self.animation_time += dt * 2
            self.bounce_offset = math.sin(self.animation_time) * 1.5
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
    
    def can_attack(self):
        if self.health <= 0 or self.is_moving:
            return False
        return self.attack_cooldown <= 0
    
    def attack_target(self, target):
        if self.can_attack():
            target.take_damage(self.attack)
            self.attack_cooldown = self.attack_speed
            return True
        return False
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def is_alive(self):
        return self.health > 0
    
    def get_attack_range_pixels(self):
        from config.constants import HEX_WIDTH
        return self.range * HEX_WIDTH * 0.9
    
    def draw(self, screen, x, y):
        # Usar siempre las coordenadas pasadas, actualizando la posición visual
        if self.visual_x == 0:
            self.set_position(x, y)
        else:
            # Si ya se movió pero se llama con nuevas coordenadas, actualizar target
            if not self.is_moving:
                self.visual_x = x
                self.visual_y = y
        
        base_x = int(self.visual_x)
        base_y = int(self.visual_y + self.bounce_offset)
        
        # Usar el renderer geométrico detallado con escala 0.55 para que quepa en el hex
        self._geo_renderer.draw(screen, base_x, base_y, scale=0.55, anim_time=self.animation_time)
        
        # Barra de vida
        self._draw_health_bar_ultra(screen, base_x, base_y - 30)
        
        # Indicador de unidad disponible
        if self.can_act and not self.has_moved and self.owner == "player":
            pygame.draw.circle(screen, (255, 255, 0), (base_x, base_y - 38), 6)
            pygame.draw.circle(screen, (255, 140, 0), (base_x, base_y - 38), 6, 2)
    
    def _draw_health_bar_ultra(self, screen, x, y):
        bar_width = 30
        bar_height = 4
        health_ratio = self.health / self.max_health
        
        # Fondo
        pygame.draw.rect(screen, (50, 0, 0), (x - bar_width//2, y, bar_width, bar_height))
        # Salud
        pygame.draw.rect(screen, (0, 255, 0), (x - bar_width//2, y, bar_width * health_ratio, bar_height))
        # Borde
        pygame.draw.rect(screen, (0, 0, 0), (x - bar_width//2, y, bar_width, bar_height), 1)
