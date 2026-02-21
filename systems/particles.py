"""
Sistema de partículas
"""
import pygame
import random
import math


class Particle:
    """Clase base para partículas"""
    
    def __init__(self, x, y, color, velocity, lifetime, size, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.glow = glow
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def is_alive(self):
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.glow:
            glow_surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            pygame.draw.circle(glow_surf, (*self.color, alpha // 2), 
                            (self.size * 2, self.size * 2), self.size * 2)
            screen.blit(glow_surf, (self.x - self.size * 2, self.y - self.size * 2))
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color, alpha)
        
        if len(self.color) == 3:
            color = self.color
            
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class ParticleSystem:
    """Sistema de partículas"""
    
    def __init__(self):
        self.particles = []
    
    def spawn_spark(self, x, y, color, count=5):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, color, (vx, vy), 
                                         random.uniform(0.3, 0.8), 
                                         random.randint(2, 5), glow=True))
    
    def spawn_dust(self, x, y):
        for _ in range(8):
            vx = random.uniform(-40, 40)
            vy = random.uniform(-30, -80)
            color = (139, 125, 107)
            self.particles.append(Particle(x, y, color, (vx, vy), 0.6, random.randint(4, 8)))
    
    def spawn_attack(self, x, y, owner):
        color = (255, 200, 50) if owner == "player" else (255, 100, 50)
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 250)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(Particle(x, y, color, (vx, vy), 0.5, 
                                         random.randint(6, 10), glow=True))
        self.spawn_spark(x, y, (255, 255, 200), 8)
    
    def spawn_footstep(self, x, y):
        for _ in range(3):
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-5, 5)
            self.particles.append(Particle(
                x + offset_x, y + offset_y,
                (100, 140, 100),
                (random.uniform(-20, 20), random.uniform(-10, -30)),
                0.4, random.randint(3, 6)
            ))
    
    def spawn_magic_trail(self, x, y, color):
        self.particles.append(Particle(x, y, color, 
                                     (random.uniform(-10, 10), random.uniform(-10, 10)), 
                                     0.5, random.randint(3, 6), glow=True))
    
    def update(self, dt):
        for p in self.particles[:]:
            p.update(dt)
            if not p.is_alive():
                self.particles.remove(p)
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
