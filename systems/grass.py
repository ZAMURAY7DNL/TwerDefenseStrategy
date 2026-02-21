"""
Sistema de pasto animado
"""
import pygame
import math
import random


class GrassSystem:
    """Sistema de pasto con ondas al caminar"""
    
    def __init__(self, width, height):
        from config.constants import GRASS_LIGHT, GRASS_DARK, GRASS_BASE
        
        self.width = width
        self.height = height
        self.blades = []
        self.waves = []
        self.time = 0
        
        for x in range(0, width, 8):
            for y in range(0, height, 8):
                height_var = random.uniform(0.7, 1.3)
                angle_var = random.uniform(-0.2, 0.2)
                self.blades.append({
                    'x': x + random.uniform(-3, 3),
                    'y': y + random.uniform(-3, 3),
                    'height': 12 * height_var,
                    'angle': angle_var,
                    'base_angle': angle_var,
                    'sway_speed': random.uniform(1.5, 2.5),
                    'color': random.choice([GRASS_LIGHT, GRASS_DARK, GRASS_BASE]),
                    'width': random.randint(2, 4)
                })
    
    def add_footstep_wave(self, x, y, radius=60):
        self.waves.append({
            'x': x,
            'y': y,
            'radius': radius,
            'strength': 1.0,
            'decay': 2.0
        })
    
    def update(self, dt):
        self.time += dt
        
        for wave in self.waves[:]:
            wave['strength'] -= wave['decay'] * dt
            if wave['strength'] <= 0:
                self.waves.remove(wave)
        
        for blade in self.blades:
            wind = math.sin(self.time * blade['sway_speed'] + blade['x'] * 0.01) * 0.15
            wave_effect = 0
            
            for wave in self.waves:
                dist = math.sqrt((blade['x'] - wave['x'])**2 + (blade['y'] - wave['y'])**2)
                if dist < wave['radius']:
                    wave_intensity = (1 - dist / wave['radius']) * wave['strength']
                    wave_effect += math.sin(self.time * 10 - dist * 0.2) * wave_intensity * 0.5
            
            blade['angle'] = blade['base_angle'] + wind + wave_effect
    
    def draw(self, screen):
        grass_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for blade in self.blades:
            tip_x = blade['x'] + math.sin(blade['angle']) * blade['height']
            tip_y = blade['y'] - math.cos(blade['angle']) * blade['height'] * 0.7
            ctrl_x = blade['x'] + math.sin(blade['angle']) * blade['height'] * 0.3
            ctrl_y = blade['y'] - math.cos(blade['angle']) * blade['height'] * 0.2
            
            points = [
                (blade['x'] - blade['width']/2, blade['y']),
                (ctrl_x - blade['width']/3, ctrl_y),
                (tip_x, tip_y),
                (ctrl_x + blade['width']/3, ctrl_y),
                (blade['x'] + blade['width']/2, blade['y'])
            ]
            
            pygame.draw.polygon(grass_surface, blade['color'], points)
            
            tip_color = (
                min(255, blade['color'][0] + 30),
                min(255, blade['color'][1] + 30),
                min(255, blade['color'][2] + 30)
            )
            pygame.draw.circle(grass_surface, tip_color, (int(tip_x), int(tip_y)), 1)
        
        screen.blit(grass_surface, (0, 0))
