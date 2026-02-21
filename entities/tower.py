"""
Torres del juego
"""
import pygame
import math
from systems.geometry import GeometricTower


class UltraTower:
    """Torre defensiva"""
    
    def __init__(self, owner):
        self.owner = owner
        self.max_health = 600
        self.health = 600
        self.attack = 35
        self.range = 3
        self.attack_speed = 0.3
        self.attack_cooldown = 0
        
        self.x = 0
        self.y = 0
        self.visual_x = 0
        self.visual_y = 0
        
        self._anim_time = 0
        
        # Renderer geométrico detallado
        self._geo_renderer = GeometricTower(owner)
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.visual_x = x
        self.visual_y = y
    
    def update(self, dt):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        self._anim_time += dt
    
    def can_attack(self):
        return self.attack_cooldown <= 0 and self.health > 0
    
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
        self.set_position(x, y)
        
        # Usar el renderer geométrico detallado con escala 0.5 para que quepa en el hex
        self._geo_renderer.draw(screen, x, y, scale=0.5, anim_time=self._anim_time)
