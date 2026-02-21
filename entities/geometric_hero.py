"""
GeometricHero - Héroe detallado con +20 figuras geométricas
============================================================
El héroe está compuesto por múltiples figuras geométricas superpuestas
para crear un personaje detallado y visualmente interesante.
"""
import pygame
import math


class GeometricHero:
    """
    Héroe del jugador renderizado con +20 figuras geométricas superpuestas.
    Cada figura contribuye a un aspecto único y detallado del personaje.
    """
    
    def __init__(self, hero_type="commander"):
        self.hero_type = hero_type
        self.anim_time = 0.0
        
        # Paleta de colores del héroe
        self.colors = {
            # Armadura principal
            'armor_light': (180, 180, 190),
            'armor_mid': (130, 130, 140),
            'armor_dark': (80, 80, 90),
            'armor_gold': (255, 200, 50),
            
            # Tela/capa
            'cloth_main': (40, 60, 120),
            'cloth_dark': (20, 30, 60),
            'cloth_accent': (180, 40, 40),
            
            # Piel
            'skin': (255, 220, 180),
            'skin_shadow': (200, 170, 140),
            
            # Metallics
            'metal_silver': (200, 200, 210),
            'metal_gold': (255, 215, 0),
            'metal_copper': (184, 115, 51),
            
            # Glows
            'glow_cyan': (0, 200, 255, 100),
            'glow_gold': (255, 200, 50, 80),
            
            # Ojos
            'eye_white': (255, 255, 255),
            'eye_pupil': (50, 50, 50),
        }
    
    def draw(self, screen, x, y, scale=1.0, anim_time=0.0):
        """
        Dibuja el héroe con +20 figuras geométricas.
        
        Args:
            screen: superficie pygame
            x, y: posición central del héroe
            scale: factor de escala
            anim_time: tiempo de animación para efectos
        """
        self.anim_time = anim_time
        s = scale
        
        # === FIGURAS DEL CUERPO (Capas de atrás hacia adelante) ===
        
        # 1. Capa base - sombras
        self._draw_ellipse(screen, x, y + 5*s, 25*s, 8*s, (20, 20, 30, 150), True)
        
        # 2. Capa - sombra del personaje
        self._draw_ellipse(screen, x, y + 35*s, 20*s, 6*s, (0, 0, 0, 100), True)
        
        # 3. Pierna izquierda
        self._draw_rect(screen, x - 8*s, y + 20*s, 6*s, 18*s, self.colors['armor_dark'])
        self._draw_rect(screen, x - 8*s, y + 20*s, 6*s, 18*s, (0, 0, 0), 1)
        
        # 4. Pierna derecha
        self._draw_rect(screen, x + 2*s, y + 20*s, 6*s, 18*s, self.colors['armor_dark'])
        self._draw_rect(screen, x + 2*s, y + 20*s, 6*s, 18*s, (0, 0, 0), 1)
        
        # 5. Bota izquierda
        self._draw_rect(screen, x - 10*s, y + 34*s, 10*s, 6*s, self.colors['metal_copper'])
        self._draw_rect(screen, x - 10*s, y + 34*s, 10*s, 6*s, (0, 0, 0), 1)
        
        # 6. Bota derecha
        self._draw_rect(screen, x + 1*s, y + 34*s, 10*s, 6*s, self.colors['metal_copper'])
        self._draw_rect(screen, x + 1*s, y + 34*s, 10*s, 6*s, (0, 0, 0), 1)
        
        # 7. Torso - armor principal
        self._draw_ellipse(screen, x, y + 10*s, 18*s, 20*s, self.colors['armor_mid'])
        self._draw_ellipse(screen, x, y + 10*s, 18*s, 20*s, (0, 0, 0), 1)
        
        # 8. Torso - detalle central
        self._draw_rect(screen, x, y + 5*s, 8*s, 16*s, self.colors['armor_gold'])
        
        # 9. Capa - atrás
        self._draw_triangle(screen, x, y - 5*s, 25*s, 30*s, self.colors['cloth_dark'])
        
        # 10. Cinturón
        self._draw_rect(screen, x, y + 18*s, 20*s, 3*s, self.colors['metal_gold'])
        
        # 11. Hebilla del cinturón
        self._draw_rect(screen, x, y + 18*s, 5*s, 5*s, self.colors['metal_silver'])
        
        # 12. Brazo izquierdo
        self._draw_rect(screen, x - 15*s, y + 8*s, 6*s, 16*s, self.colors['armor_light'])
        self._draw_rect(screen, x - 15*s, y + 8*s, 6*s, 16*s, (0, 0, 0), 1)
        
        # 13. Brazo derecho (levantado para comando)
        self._draw_rect(screen, x + 10*s, y - 2*s, 6*s, 14*s, self.colors['armor_light'])
        self._draw_rect(screen, x + 10*s, y - 2*s, 6*s, 14*s, (0, 0, 0), 1)
        
        # 14. Guante izquierdo
        self._draw_circle(screen, x - 15*s, y + 22*s, 5*s, self.colors['cloth_main'])
        
        # 15. Guante derecho (con guantelete)
        self._draw_circle(screen, x + 10*s, y + 10*s, 6*s, self.colors['armor_gold'])
        
        # 16. Cuello - armadura
        self._draw_rect(screen, x, y - 8*s, 8*s, 5*s, self.colors['armor_dark'])
        
        # 17. Cabeza - casco principal
        self._draw_circle(screen, x, y - 18*s, 14*s, self.colors['armor_light'])
        self._draw_circle(screen, x, y - 18*s, 14*s, (0, 0, 0), 2)
        
        # 18. Visor del casco
        self._draw_ellipse(screen, x, y - 16*s, 20*s, 8*s, self.colors['glow_cyan'][:3] + (150,))
        self._draw_ellipse(screen, x, y - 16*s, 20*s, 8*s, (0, 200, 255), 2)
        
        # 19. Pluma del casco
        self._draw_triangle(screen, x - 3*s, y - 30*s, 6*s, 15*s, self.colors['cloth_accent'])
        
        # 20. Cresta del casco
        self._draw_triangle(screen, x + 3*s, y - 32*s, 4*s, 12*s, self.colors['metal_gold'])
        
        # 21. Ojo (a través del visor)
        self._draw_circle(screen, x + 4*s, y - 17*s, 2*s, self.colors['eye_white'])
        self._draw_circle(screen, x + 4*s, y - 17*s, 1*s, self.colors['eye_pupil'])
        
        # 22. Hombro izquierdo - hombrera
        self._draw_ellipse(screen, x - 14*s, y - 2*s, 8*s, 6*s, self.colors['armor_gold'])
        self._draw_ellipse(screen, x - 14*s, y - 2*s, 8*s, 6*s, (0, 0, 0), 1)
        
        # 23. Hombro derecho - hombrera
        self._draw_ellipse(screen, x + 14*s, y - 2*s, 8*s, 6*s, self.colors['armor_gold'])
        self._draw_ellipse(screen, x + 14*s, y - 2*s, 8*s, 6*s, (0, 0, 0), 1)
        
        # 24. Espada/Báculo en la mano derecha
        self._draw_line(screen, x + 16*s, y + 5*s, x + 16*s, y - 20*s, self.colors['metal_silver'], 2)
        
        # 25. Punta de la espada
        self._draw_triangle(screen, x + 16*s, y - 25*s, 4*s, 8*s, self.colors['glow_cyan'][:3])
        
        # 26. Emblema en el pecho
        self._draw_star(screen, x, y + 8*s, 5*s, 2*s, 5, self.colors['metal_gold'])
        
        # 27. Efecto de glow animado (aura)
        pulse = abs(math.sin(anim_time * 2)) * 0.3 + 0.7
        glow_size = 30 * pulse
        self._draw_circle(screen, x, y, glow_size * s, self.colors['glow_cyan'], True)
        
        # 28. Corona/diadema
        self._draw_rect(screen, x, y - 30*s, 14*s, 3*s, self.colors['metal_gold'])
        for i in range(3):
            self._draw_triangle(screen, x - 4*s + i*4*s, y - 33*s, 3*s, 5*s, self.colors['metal_gold'])
    
    # === Métodos helpers de dibujo ===
    
    def _draw_circle(self, screen, x, y, radius, color, filled=False):
        if filled and len(color) == 4:
            surf = pygame.Surface((int(radius*2), int(radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(radius), int(radius)), int(radius))
            screen.blit(surf, (int(x - radius), int(y - radius)))
        else:
            width = 0 if filled else 2
            pygame.draw.circle(screen, color, (int(x), int(y)), int(radius), width)
    
    def _draw_ellipse(self, screen, x, y, w, h, color, filled=False):
        rect = pygame.Rect(int(x - w/2), int(y - h/2), int(w), int(h))
        if filled and len(color) == 4:
            surf = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, color, (0, 0, int(w), int(h)))
            screen.blit(surf, (int(x - w/2), int(y - h/2)))
        else:
            width = 0 if filled else 2
            pygame.draw.ellipse(screen, color, rect, width)
    
    def _draw_rect(self, screen, x, y, w, h, color, width=0):
        rect = pygame.Rect(int(x - w/2), int(y - h/2), int(w), int(h))
        pygame.draw.rect(screen, color, rect, width)
    
    def _draw_triangle(self, screen, x, y, w, h, color):
        points = [
            (x, y - h/2),
            (x - w/2, y + h/2),
            (x + w/2, y + h/2)
        ]
        pygame.draw.polygon(screen, color, points)
    
    def _draw_line(self, screen, x1, y1, x2, y2, color, width=1):
        pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), width)
    
    def _draw_star(self, screen, x, y, outer_r, inner_r, points, color):
        import math
        vertices = []
        for i in range(points * 2):
            angle = math.pi / points * i - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            vertices.append((
                x + r * math.cos(angle),
                y + r * math.sin(angle)
            ))
        pygame.draw.polygon(screen, color, vertices)


# Alias para importación
GeometricHeroRenderer = GeometricHero
