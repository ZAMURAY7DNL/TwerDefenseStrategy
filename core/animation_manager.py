"""
Animation Manager - Gestor de Animaciones
=========================================
Maneja animaciones de ataque y efectos visuales.
"""
from entities import TracerProjectile


class AnimationManager:
    """Gestiona animaciones del juego."""
    
    def __init__(self, particle_system):
        self.particles = particle_system
        self.active_animation = None
        self.projectiles = []
    
    def start_attack_animation(self, hero, target, power_id):
        """Inicia animación de ataque del héroe."""
        self.active_animation = {
            'hero': hero,
            'target': target,
            'power': power_id,
            'phase': 'windup',
            'timer': 0.0,
            'duration': 0.8,
        }
    
    def update(self, dt):
        """Actualiza la animación activa."""
        if not self.active_animation:
            return False
        
        anim = self.active_animation
        anim['timer'] += dt
        
        # Fase 1: Preparación (windup) - 0.0 a 0.3s
        if anim['phase'] == 'windup':
            if anim['timer'] >= 0.3:
                anim['phase'] = 'strike'
                # Crear efectos visuales al impactar
                tx = getattr(anim['target'], 'visual_x', 0)
                ty = getattr(anim['target'], 'visual_y', 0)
                self.particles.spawn_attack(tx, ty, "player")
                
                # Proyectil especial según poder
                hx = getattr(anim['hero'], 'visual_x', 0)
                hy = getattr(anim['hero'], 'visual_y', 0)
                
                color = (255, 200, 100) if anim['power'] == 'slash' else \
                        (255, 100, 50) if anim['power'] == 'power_strike' else \
                        (100, 255, 100) if anim['power'] == 'heal' else (200, 200, 255)
                
                proj = TracerProjectile(hx, hy, anim['target'], 10, 
                                       color, "player", self.particles)
                self.projectiles.append(proj)
        
        # Fase 2: Impacto (strike) - 0.3 a 0.5s
        elif anim['phase'] == 'strike':
            if anim['timer'] >= 0.5:
                anim['phase'] = 'recovery'
        
        # Fase 3: Recuperación (recovery) - 0.5 a 0.8s
        elif anim['phase'] == 'recovery':
            if anim['timer'] >= anim['duration']:
                self.active_animation = None
                return True  # Animación terminada
        
        return False
    
    def is_animating(self):
        """Verifica si hay una animación activa."""
        return self.active_animation is not None
    
    def cancel_animation(self):
        """Cancela la animación actual."""
        self.active_animation = None
    
    def update_projectiles(self, dt):
        """Actualiza proyectiles de animación."""
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.active:
                self.projectiles.remove(proj)
    
    def draw_projectiles(self, screen):
        """Dibuja proyectiles de animación."""
        for proj in self.projectiles:
            proj.draw(screen)
    
    def clear(self):
        """Limpia todas las animaciones."""
        self.active_animation = None
        self.projectiles.clear()
