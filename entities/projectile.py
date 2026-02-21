"""
Proyectiles del juego
"""
import pygame
import random


class TracerProjectile:
    """Proyectil con estela"""
    
    def __init__(self, x, y, target, damage, color, owner, particles):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.color = color
        self.owner = owner
        self.particles = particles
        
        self.speed = 400
        self.radius = 4
        self.active = True
        self.trail = []
        self.max_trail = 8
        self.vx = 0
        self.vy = 0
        
        self.update_direction()
    
    def update_direction(self):
        if self.target.is_alive():
            tx = getattr(self.target, 'visual_x', None) if hasattr(self.target, 'visual_x') else getattr(self.target, 'x', 0)
            ty = getattr(self.target, 'visual_y', None) if hasattr(self.target, 'visual_y') else getattr(self.target, 'y', 0)
            
            dx = tx - self.x
            dy = ty - self.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 0:
                self.vx = (dx / distance) * self.speed
                self.vy = (dy / distance) * self.speed
    
    def update(self, dt):
        if not self.active:
            return
        
        if not self.target.is_alive():
            self.active = False
            return
        
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        self.update_direction()
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        if random.random() < 0.3:
            self.particles.spawn_magic_trail(self.x, self.y, self.color)
        
        tx = getattr(self.target, 'visual_x', None) if hasattr(self.target, 'visual_x') else getattr(self.target, 'x', 0)
        ty = getattr(self.target, 'visual_y', None) if hasattr(self.target, 'visual_y') else getattr(self.target, 'y', 0)
        
        dist = ((self.x - tx)**2 + (self.y - ty)**2)**0.5
        if dist < 15:
            self.target.take_damage(self.damage)
            self.particles.spawn_attack(tx, ty, self.owner)
            self.active = False
    
    def draw(self, screen):
        if not self.active or len(self.trail) < 2:
            return
        
        for i, (tx, ty) in enumerate(self.trail):
            size = self.radius * (i / len(self.trail))
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(tx), int(ty)), int(size))
        
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)
        
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color[:3], 150), (10, 10), 10)
        screen.blit(glow_surf, (int(self.x) - 10, int(self.y) - 10))
