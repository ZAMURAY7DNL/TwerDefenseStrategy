"""
Renderizado geométrico detallado para unidades, torres y efectos
"""
import pygame
import math
import random

# ============================================================
# COLORES BASE PARA FIGURAS GEOMÉTRICAS
# ============================================================
PALETTE = {
    # Metales
    'steel_light': (200, 200, 210),
    'steel_mid': (140, 140, 150),
    'steel_dark': (80, 80, 90),
    'gold': (255, 215, 0),
    'bronze': (205, 127, 50),
    'copper': (184, 115, 51),
    
    # Pieles
    'skin_pale': (255, 220, 200),
    'skin_tan': (210, 180, 140),
    'skin_dark': (120, 80, 60),
    
    # Telas
    'cloth_red': (180, 40, 40),
    'cloth_blue': (40, 60, 120),
    'cloth_green': (40, 100, 40),
    'cloth_brown': (101, 67, 33),
    'cloth_black': (30, 30, 30),
    
    # Efectos
    'glow_red': (255, 100, 100, 150),
    'glow_blue': (100, 150, 255, 150),
    'glow_green': (100, 255, 150, 150),
    'shadow': (0, 0, 0, 80),
}


# ============================================================
# DIBUJADOR GEOMÉTRICO UNIVERSAL
# ============================================================
class GeometryRenderer:
    @staticmethod
    def draw_circle(screen, x, y, radius, color, width=0):
        pygame.draw.circle(screen, color, (int(x), int(y)), int(radius), width)
    
    @staticmethod
    def draw_ellipse(screen, x, y, width, height, color, line_width=0):
        rect = pygame.Rect(int(x - width/2), int(y - height/2), int(width), int(height))
        pygame.draw.ellipse(screen, color, rect, line_width)
    
    @staticmethod
    def draw_rect(screen, x, y, width, height, color, line_width=0, centered=True):
        if centered:
            rect = pygame.Rect(int(x - width/2), int(y - height/2), int(width), int(height))
        else:
            rect = pygame.Rect(int(x), int(y), int(width), int(height))
        pygame.draw.rect(screen, color, rect, border_radius=2)
        if line_width > 0:
            pygame.draw.rect(screen, (0,0,0), rect, line_width, border_radius=2)
    
    @staticmethod
    def draw_polygon(screen, points, color, line_width=0):
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points, line_width)
    
    @staticmethod
    def draw_line(screen, x1, y1, x2, y2, color, width=1):
        pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), width)
    
    @staticmethod
    def draw_arc(screen, x, y, radius, start_angle, end_angle, color, width=1):
        rect = pygame.Rect(int(x-radius), int(y-radius), int(radius*2), int(radius*2))
        pygame.draw.arc(screen, color, rect, start_angle, end_angle, width)
    
    @staticmethod
    def draw_star(screen, x, y, outer_r, inner_r, points, color, rotation=0):
        vertices = []
        for i in range(points * 2):
            angle = rotation + (i * math.pi / points)
            radius = outer_r if i % 2 == 0 else inner_r
            vx = x + math.cos(angle) * radius
            vy = y + math.sin(angle) * radius
            vertices.append((vx, vy))
        GeometryRenderer.draw_polygon(screen, vertices, color)
    
    @staticmethod
    def draw_bolt(screen, x1, y1, x2, y2, color, width=2, segments=4):
        """Rayo eléctrico con zigzag"""
        points = [(x1, y1)]
        for i in range(1, segments):
            t = i / segments
            bx = x1 + (x2 - x1) * t + random.uniform(-10, 10)
            by = y1 + (y2 - y1) * t + random.uniform(-10, 10)
            points.append((bx, by))
        points.append((x2, y2))
        
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, width)
            pygame.draw.lines(screen, (255,255,255), False, points, max(1, width-2))

    @staticmethod
    def draw_glow(screen, x, y, radius, color, intensity=3):
        """Efecto de brillo radial"""
        for i in range(intensity, 0, -1):
            alpha = int(100 / i)
            glow_surf = pygame.Surface((radius*2*i, radius*2*i), pygame.SRCALPHA)
            glow_color = (*color[:3], alpha)
            pygame.draw.circle(glow_surf, glow_color, (radius*i, radius*i), radius*i)
            screen.blit(glow_surf, (int(x - radius*i), int(y - radius*i)))
    
    @staticmethod
    def draw_health_bar(screen, x, y, width, height, current, maximum, 
                       color_full=(100,255,100), color_empty=(255,100,100)):
        # Fondo
        GeometryRenderer.draw_rect(screen, x, y, width, height, (40,40,40))
        # Barra de vida
        pct = max(0, min(1, current/maximum))
        bar_width = width * pct
        color = (
            int(color_empty[0] + (color_full[0]-color_empty[0])*pct),
            int(color_empty[1] + (color_full[1]-color_empty[1])*pct),
            int(color_empty[2] + (color_full[2]-color_empty[2])*pct)
        )
        if bar_width > 0:
            GeometryRenderer.draw_rect(screen, x - width/2 + bar_width/2, y, 
                                     bar_width, height, color)
        # Borde
        GeometryRenderer.draw_rect(screen, x, y, width, height, (200,200,200), 2)


# ============================================================
# UNIDADES GEOMÉTRICAS DETALLADAS
# ============================================================
class GeometricUnit:
    def __init__(self, unit_type, owner):
        self.unit_type = unit_type
        self.owner = owner  # "player" o "enemy"
        self.anim_frame = 0
        
        # Paleta según facción
        if owner == "player":
            self.primary = (80, 150, 220)
            self.secondary = (60, 110, 180)
            self.accent = (100, 200, 255)
        else:
            self.primary = (200, 80, 80)
            self.secondary = (160, 60, 60)
            self.accent = (255, 150, 100)
    
    def draw(self, screen, x, y, scale=1.0, anim_time=0):
        self.anim_frame = anim_time
        
        if self.unit_type == "berserker":
            self._draw_berserker(screen, x, y, scale)
        elif self.unit_type == "assault":
            self._draw_assault(screen, x, y, scale)
        elif self.unit_type == "ranger":
            self._draw_ranger(screen, x, y, scale)
        elif self.unit_type == "sniper":
            self._draw_sniper(screen, x, y, scale)
        elif self.unit_type == "tank":
            self._draw_tank(screen, x, y, scale)
        elif self.unit_type == "mage":
            self._draw_mage(screen, x, y, scale)
    
    def _draw_berserker(self, screen, x, y, s):
        """Guerrero pesado con hacha doble - 20+ figuras"""
        GR = GeometryRenderer
        
        # Sombra
        GR.draw_ellipse(screen, x, y+25*s, 30*s, 10*s, (0,0,0,60))
        
        # Capa (triángulos y polígonos)
        cape_points = [
            (x-15*s, y-5*s), (x-25*s, y+15*s), (x-10*s, y+20*s),
            (x, y+18*s), (x+10*s, y+20*s), (x+25*s, y+15*s), (x+15*s, y-5*s)
        ]
        GR.draw_polygon(screen, cape_points, (60, 40, 40))
        GR.draw_polygon(screen, cape_points, (40, 30, 30), 2)
        
        # Piernas (rectángulos)
        GR.draw_rect(screen, x-10*s, y+10*s, 8*s, 15*s, self.secondary)
        GR.draw_rect(screen, x+10*s, y+10*s, 8*s, 15*s, self.secondary)
        
        # Botas (elipses)
        GR.draw_ellipse(screen, x-10*s, y+22*s, 12*s, 8*s, (50, 40, 40))
        GR.draw_ellipse(screen, x+10*s, y+22*s, 12*s, 8*s, (50, 40, 40))
        
        # Cinturón
        GR.draw_rect(screen, x, y+2*s, 28*s, 6*s, (139, 90, 43))
        GR.draw_rect(screen, x, y+2*s, 8*s, 8*s, self.accent)  # Hebilla
        
        # Torso (rombo/pecho)
        body_points = [
            (x, y-20*s), (x+15*s, y-5*s), (x+10*s, y+8*s),
            (x, y+5*s), (x-10*s, y+8*s), (x-15*s, y-5*s)
        ]
        GR.draw_polygon(screen, body_points, self.primary)
        GR.draw_polygon(screen, body_points, self.secondary, 2)
        
        # Músculos (líneas)
        GR.draw_line(screen, x, y-15*s, x, y+2*s, self.secondary, 2)
        GR.draw_line(screen, x-8*s, y-8*s, x-5*s, y-3*s, (40,40,40), 1)
        GR.draw_line(screen, x+8*s, y-8*s, x+5*s, y-3*s, (40,40,40), 1)
        
        # Cabeza (círculo)
        GR.draw_circle(screen, x, y-25*s, 10*s, (210, 180, 140))
        GR.draw_circle(screen, x, y-25*s, 10*s, (60, 40, 40), 2)
        
        # Casco/cuernos (triángulos)
        GR.draw_polygon(screen, [
            (x-8*s, y-30*s), (x-12*s, y-42*s), (x-4*s, y-35*s)
        ], (180, 180, 190))
        GR.draw_polygon(screen, [
            (x+8*s, y-30*s), (x+12*s, y-42*s), (x+4*s, y-35*s)
        ], (180, 180, 190))
        
        # Ojos (círculos pequeños)
        GR.draw_circle(screen, x-3*s, y-25*s, 2*s, (255, 50, 50))
        GR.draw_circle(screen, x+3*s, y-25*s, 2*s, (255, 50, 50))
        
        # Hacha izquierda (rectángulos + triángulos)
        GR.draw_rect(screen, x-25*s, y-10*s, 5*s, 30*s, (101, 67, 33))  # Mango
        GR.draw_polygon(screen, [  # Hoja
            (x-28*s, y-15*s), (x-35*s, y+5*s), (x-25*s, y+5*s), (x-25*s, y-10*s)
        ], (180, 180, 190))
        
        # Espada derecha
        GR.draw_rect(screen, x+22*s, y-5*s, 6*s, 10*s, (80, 60, 50))  # Empuñadura
        GR.draw_rect(screen, x+20*s, y-8*s, 10*s, 4*s, (180, 180, 190))  # Guarda
        GR.draw_polygon(screen, [  # Hoja
            (x+25*s, y-8*s), (x+22*s, y-35*s), (x+28*s, y-35*s), (x+25*s, y-8*s)
        ], (220, 220, 230))
        
        # Detalles: brazaletes
        GR.draw_rect(screen, x-20*s, y-10*s, 6*s, 4*s, (180, 180, 190))
        GR.draw_rect(screen, x+18*s, y-10*s, 6*s, 4*s, (180, 180, 190))
        
        # Cicatriz/pecho
        GR.draw_line(screen, x-5*s, y-12*s, x+5*s, y-8*s, (150, 100, 100), 2)
    
    def _draw_assault(self, screen, x, y, s):
        """Soldado de asalto con rifle - 18+ figuras"""
        GR = GeometryRenderer
        
        # Propulsores/jetpack (elipses)
        GR.draw_ellipse(screen, x-15*s, y+20*s, 20*s, 12*s, (50, 50, 60))
        
        # Piernas mecánicas
        GR.draw_rect(screen, x-12*s, y+5*s, 10*s, 12*s, self.secondary)
        GR.draw_rect(screen, x-12*s, y+5*s, 10*s, 4*s, (140, 140, 150))  # Rodilla
        GR.draw_rect(screen, x-11*s, y+15*s, 8*s, 10*s, self.primary)
        GR.draw_rect(screen, x-12*s, y+22*s, 10*s, 5*s, (40, 40, 50))  # Pie
        
        GR.draw_rect(screen, x+12*s, y+5*s, 10*s, 12*s, self.secondary)
        GR.draw_rect(screen, x+12*s, y+5*s, 10*s, 4*s, (140, 140, 150))
        GR.draw_rect(screen, x+11*s, y+15*s, 8*s, 10*s, self.primary)
        GR.draw_rect(screen, x+12*s, y+22*s, 10*s, 5*s, (40, 40, 50))
        
        # Cadera
        GR.draw_rect(screen, x, y-2*s, 24*s, 8*s, (40, 40, 50))
        
        # Torso (rectángulos con detalles)
        GR.draw_rect(screen, x, y-18*s, 26*s, 20*s, self.primary)
        GR.draw_rect(screen, x, y-20*s, 22*s, 4*s, (140, 140, 150))  # Cuello armadura
        GR.draw_rect(screen, x, y-16*s, 16*s, 2*s, self.accent)  # Línea luminosa
        GR.draw_rect(screen, x, y-12*s, 20*s, 8*s, self.secondary)
        
        # Reactor pecho (círculos concéntricos)
        GR.draw_circle(screen, x, y-14*s, 5*s, self.accent)
        GR.draw_circle(screen, x, y-14*s, 3*s, (255, 255, 255))
        GR.draw_circle(screen, x, y-14*s, 1*s, (200, 255, 255))
        
        # Hombros (círculos)
        GR.draw_circle(screen, x-16*s, y-18*s, 7*s, (140, 140, 150))
        GR.draw_circle(screen, x+16*s, y-18*s, 7*s, (140, 140, 150))
        
        # Cabeza (elipse + rectángulos)
        GR.draw_ellipse(screen, x, y-30*s, 18*s, 14*s, (140, 140, 150))
        GR.draw_rect(screen, x, y-28*s, 14*s, 6*s, self.accent)  # Visor
        GR.draw_rect(screen, x, y-27*s, 10*s, 2*s, (255, 255, 255))  # Brillo visor
        
        # Antena
        GR.draw_line(screen, x+8*s, y-32*s, x+12*s, y-42*s, (140, 140, 150), 2)
        GR.draw_circle(screen, x+12*s, y-44*s, 3*s, (255, 50, 50))
        
        # Brazo izquierdo
        GR.draw_rect(screen, x-22*s, y-15*s, 8*s, 12*s, self.secondary)
        GR.draw_ellipse(screen, x-24*s, y-8*s, 8*s, 6*s, (100, 100, 110))
        
        # Rifle (rectángulos complejos)
        GR.draw_rect(screen, x+18*s, y-15*s, 8*s, 10*s, self.secondary)  # Hombro
        GR.draw_rect(screen, x+32*s, y-12*s, 25*s, 6*s, (60, 60, 70))  # Cañón
        GR.draw_rect(screen, x+42*s, y-16*s, 8*s, 4*s, (40, 40, 50))  # Mira
        GR.draw_rect(screen, x+34*s, y-6*s, 6*s, 8*s, (101, 67, 33))  # Cargador
        GR.draw_circle(screen, x+52*s, y-9*s, 3*s, (255, 100, 0))  # Punta caliente
        
        # Brazo derecho sosteniendo rifle
        GR.draw_rect(screen, x+12*s, y-12*s, 8*s, 10*s, self.secondary)
        GR.draw_ellipse(screen, x+16*s, y-8*s, 6*s, 6*s, (100, 100, 110))
        
        # Mochila propulsores
        GR.draw_rect(screen, x, y-26*s, 16*s, 8*s, (40, 40, 50))
        GR.draw_rect(screen, x-6*s, y-24*s, 4*s, 4*s, self.accent)
        GR.draw_rect(screen, x+6*s, y-24*s, 4*s, 4*s, self.accent)
    
    def _draw_ranger(self, screen, x, y, s):
        """Arquero con capa - 16+ figuras"""
        GR = GeometryRenderer
        
        # Sombra
        GR.draw_ellipse(screen, x, y+25*s, 28*s, 8*s, (0,0,0,60))
        
        # Capa con animación de viento
        wind = math.sin(pygame.time.get_ticks() * 0.003) * 5 * s
        cape_points = [
            (x-5*s, y-20*s), (x-22*s+wind, y-8*s), (x-28*s+wind, y+12*s),
            (x-18*s+wind*0.5, y+22*s), (x-5*s, y+18*s), (x+5*s, y+18*s),
            (x+18*s+wind*0.5, y+22*s), (x+28*s+wind, y+12*s), (x+22*s+wind, y-8*s), (x+5*s, y-20*s)
        ]
        GR.draw_polygon(screen, cape_points, (60, 50, 40))
        GR.draw_polygon(screen, cape_points, (40, 30, 20), 2)
        
        # Piernas (elipses + rectángulos)
        GR.draw_ellipse(screen, x-8*s, y+15*s, 10*s, 20*s, (80, 70, 60))
        GR.draw_ellipse(screen, x+8*s, y+15*s, 10*s, 20*s, (80, 70, 60))
        
        # Botas
        GR.draw_ellipse(screen, x-8*s, y+24*s, 8*s, 10*s, (50, 40, 35))
        GR.draw_ellipse(screen, x+8*s, y+24*s, 8*s, 10*s, (50, 40, 35))
        
        # Cuerpo (elipse)
        GR.draw_ellipse(screen, x, y-5*s, 20*s, 30*s, self.primary)
        GR.draw_ellipse(screen, x, y-5*s, 18*s, 28*s, self.secondary, 2)
        
        # Cinturón
        GR.draw_rect(screen, x, y+2*s, 22*s, 5*s, (101, 67, 33))
        GR.draw_rect(screen, x, y+2*s, 6*s, 7*s, self.accent)
        
        # Arco (curva compuesta por líneas)
        bow_points = []
        for i in range(11):
            angle = -math.pi/2 + (i-5) * 0.2
            bx = x + 20*s + math.cos(angle) * 18*s
            by = y - 5*s + math.sin(angle) * 35*s
            bow_points.append((bx, by))
        if len(bow_points) > 1:
            pygame.draw.lines(screen, (139, 90, 43), False, bow_points, int(4*s))
        
        # Cuerda del arco
        GR.draw_line(screen, x+20*s, y-40*s, x+20*s, y+30*s, (220, 220, 200), 1)
        
        # Flecha
        GR.draw_line(screen, x+15*s, y-25*s, x+15*s, y+20*s, (160, 130, 100), 2)
        GR.draw_polygon(screen, [  # Punta
            (x+15*s, y-25*s), (x+12*s, y-20*s), (x+18*s, y-20*s)
        ], (180, 180, 190))
        GR.draw_polygon(screen, [  # Plumas
            (x+15*s, y+20*s), (x+11*s, y+15*s), (x+19*s, y+15*s)
        ], (240, 240, 255))
        
        # Brazos
        GR.draw_rect(screen, x-16*s, y-12*s, 7*s, 14*s, self.primary)
        GR.draw_ellipse(screen, x-18*s, y-8*s, 6*s, 6*s, (210, 180, 140))
        
        GR.draw_rect(screen, x+12*s, y-10*s, 7*s, 12*s, self.primary)
        GR.draw_ellipse(screen, x+16*s, y-6*s, 6*s, 6*s, (210, 180, 140))
        
        # Cabeza
        GR.draw_circle(screen, x, y-28*s, 9*s, (210, 180, 140))
        
        # Cabello (líneas)
        for i in range(4):
            hair_x = x - 6*s + i * 4*s
            GR.draw_line(screen, hair_x, y-32*s, hair_x + wind*0.3, y-25*s, (80, 60, 40), 2)
        
        # Ojos
        GR.draw_circle(screen, x-3*s, y-28*s, 2*s, self.accent)
        GR.draw_circle(screen, x+3*s, y-28*s, 2*s, self.accent)
        
        # Hood/capucha
        GR.draw_arc(screen, x, y-30*s, 11*s, 0, math.pi, (60, 50, 40), int(3*s))
    
    def _draw_sniper(self, screen, x, y, s):
        """Francotirador con rifle largo - 15+ figuras"""
        GR = GeometryRenderer
        
        # Base
        GR.draw_ellipse(screen, x, y+20*s, 26*s, 10*s, (40, 50, 40))
        
        # Piernas (postura de rodillas)
        GR.draw_ellipse(screen, x-12*s, y+10*s, 8*s, 12*s, self.secondary)
        GR.draw_rect(screen, x-14*s, y+2*s, 7*s, 10*s, self.primary)
        GR.draw_rect(screen, x-13*s, y+12*s, 6*s, 10*s, (50, 50, 60))
        GR.draw_ellipse(screen, x-14*s, y+20*s, 9*s, 6*s, (60, 50, 50))
        
        GR.draw_ellipse(screen, x+12*s, y+10*s, 8*s, 12*s, self.secondary)
        GR.draw_rect(screen, x+7*s, y+2*s, 7*s, 10*s, self.primary)
        GR.draw_rect(screen, x+8*s, y+12*s, 6*s, 10*s, (50, 50, 60))
        GR.draw_ellipse(screen, x+7*s, y+20*s, 9*s, 6*s, (60, 50, 50))
        
        # Muslos
        GR.draw_ellipse(screen, x-12*s, y-2*s, 11*s, 12*s, self.primary)
        GR.draw_ellipse(screen, x+12*s, y-2*s, 11*s, 12*s, self.primary)
        
        # Torso
        GR.draw_rect(screen, x, y-18*s, 18*s, 20*s, self.primary)
        GR.draw_rect(screen, x, y-16*s, 16*s, 14*s, (40, 40, 50))
        
        # Chaleco táctico (detalles rectangulares)
        GR.draw_rect(screen, x-7*s, y-14*s, 6*s, 8*s, (60, 60, 70))
        GR.draw_rect(screen, x+7*s, y-14*s, 6*s, 8*s, (60, 60, 70))
        
        # Cuello
        GR.draw_rect(screen, x, y-24*s, 12*s, 6*s, (40, 40, 50))
        
        # Cabeza
        GR.draw_ellipse(screen, x, y-32*s, 16*s, 12*s, self.secondary)
        GR.draw_arc(screen, x, y-34*s, 9*s, 0, math.pi, (40, 40, 50), int(4*s))  # Gorro
        
        # Goggles
        GR.draw_rect(screen, x, y-30*s, 14*s, 5*s, (50, 50, 60))
        GR.draw_rect(screen, x-5*s, y-29*s, 5*s, 3*s, self.accent)
        GR.draw_rect(screen, x+5*s, y-29*s, 5*s, 3*s, self.accent)
        
        # Rifle de francotirador (muy largo)
        GR.draw_rect(screen, x+8*s, y-18*s, 40*s, 6*s, (50, 55, 60))  # Cañón principal
        GR.draw_rect(screen, x+20*s, y-22*s, 35*s, 3*s, (40, 45, 50))  # Mira larga
        GR.draw_rect(screen, x+25*s, y-26*s, 15*s, 4*s, (30, 35, 40))  # Scope
        GR.draw_circle(screen, x+45*s, y-24*s, 1*s, (255, 0, 0))  # Punto rojo
        
        # Bípode
        GR.draw_line(screen, x+35*s, y-12*s, x+32*s, y+8*s, (140, 140, 150), 2)
        GR.draw_line(screen, x+40*s, y-12*s, x+43*s, y+8*s, (140, 140, 150), 2)
        
        # Brazos
        GR.draw_rect(screen, x-14*s, y-15*s, 7*s, 12*s, self.primary)
        GR.draw_ellipse(screen, x-16*s, y-12*s, 6*s, 6*s, (210, 200, 190))
        
        GR.draw_rect(screen, x+10*s, y-12*s, 7*s, 10*s, self.primary)
        GR.draw_ellipse(screen, x+14*s, y-8*s, 6*s, 6*s, (210, 200, 190))
        
        # Detalles: munición
        for dx, dy in [(-6*s, -10*s), (4*s, -6*s), (-4*s, 4*s), (8*s, 0)]:
            GR.draw_circle(screen, x+dx, y+dy, 2*s, (60, 70, 60))
    
    def _draw_tank(self, screen, x, y, s):
        """Unidad tanque pesada - 14+ figuras"""
        GR = GeometryRenderer
        
        # Orugas (elipses grandes)
        GR.draw_ellipse(screen, x-20*s, y+20*s, 25*s, 15*s, (50, 50, 60))
        GR.draw_ellipse(screen, x+20*s, y+20*s, 25*s, 15*s, (50, 50, 60))
        
        # Cadenas detalle
        for i in range(5):
            GR.draw_circle(screen, x-30*s+i*12*s, y+20*s, 3*s, (80, 80, 90))
        
        # Cuerpo principal (rectángulo redondeado)
        GR.draw_rect(screen, x, y+5*s, 50*s, 25*s, self.secondary)
        GR.draw_rect(screen, x, y+5*s, 46*s, 21*s, self.primary, 2)
        
        # Torreta (círculo)
        GR.draw_circle(screen, x, y-10*s, 18*s, self.secondary)
        GR.draw_circle(screen, x, y-10*s, 14*s, self.primary)
        GR.draw_circle(screen, x, y-10*s, 6*s, (80, 80, 90))  # Escotilla
        
        # Cañón principal (rectángulo largo)
        GR.draw_rect(screen, x+35*s, y-10*s, 50*s, 8*s, (60, 60, 70))
        GR.draw_rect(screen, x+55*s, y-12*s, 15*s, 4*s, (40, 40, 50))  # Freno de boca
        
        # Cañón secundario
        GR.draw_rect(screen, x-25*s, y-5*s, 20*s, 5*s, (70, 70, 80))
        
        # Antenas
        GR.draw_line(screen, x-10*s, y-28*s, x-10*s, y-45*s, (140, 140, 150), 2)
        GR.draw_circle(screen, x-10*s, y-47*s, 3*s, (255, 50, 50))
        
        GR.draw_line(screen, x+10*s, y-28*s, x+10*s, y-40*s, (140, 140, 150), 2)
        GR.draw_circle(screen, x+10*s, y-42*s, 2*s, (50, 255, 50))
        
        # Luces
        GR.draw_circle(screen, x-20*s, y+15*s, 4*s, (255, 255, 200))
        GR.draw_circle(screen, x+20*s, y+15*s, 4*s, (255, 100, 100))
    
    def _draw_mage(self, screen, x, y, s):
        """Mago con efectos mágicos - 18+ figuras"""
        GR = GeometryRenderer
        
        # Aura mágica (círculos concéntricos transparentes)
        GR.draw_glow(screen, x, y-10*s, 25*s, self.accent, 4)
        
        # Túnica (triángulo invertido)
        robe_points = [
            (x, y-35*s), (x-18*s, y+20*s), (x-10*s, y+25*s),
            (x, y+22*s), (x+10*s, y+25*s), (x+18*s, y+20*s)
        ]
        GR.draw_polygon(screen, robe_points, (80, 40, 120))
        GR.draw_polygon(screen, robe_points, (120, 60, 180), 2)
        
        # Mangas amplias
        GR.draw_ellipse(screen, x-20*s, y-5*s, 15*s, 20*s, (100, 50, 150))
        GR.draw_ellipse(screen, x+20*s, y-5*s, 15*s, 20*s, (100, 50, 150))
        
        # Cinturón
        GR.draw_rect(screen, x, y+5*s, 20*s, 5*s, (139, 90, 43))
        GR.draw_rect(screen, x, y+5*s, 6*s, 7*s, self.accent)  # Gema
        
        # Pecho ornamentado
        GR.draw_star(screen, x, y-15*s, 8*s, 4*s, 5, (255, 215, 0))
        
        # Cabeza con capucha
        GR.draw_circle(screen, x, y-30*s, 10*s, (210, 180, 200))
        GR.draw_arc(screen, x, y-32*s, 12*s, math.pi, 2*math.pi, (80, 40, 120), int(4*s))
        
        # Ojos brillantes
        GR.draw_circle(screen, x-3*s, y-30*s, 2*s, self.accent)
        GR.draw_circle(screen, x+3*s, y-30*s, 2*s, self.accent)
        GR.draw_glow(screen, x-3*s, y-30*s, 4*s, self.accent, 2)
        GR.draw_glow(screen, x+3*s, y-30*s, 4*s, self.accent, 2)
        
        # Barba
        GR.draw_polygon(screen, [
            (x, y-25*s), (x-5*s, y-15*s), (x, y-12*s), (x+5*s, y-15*s)
        ], (220, 220, 240))
        
        # Bastón mágico
        GR.draw_line(screen, x+25*s, y+20*s, x+25*s, y-40*s, (101, 67, 33), 3)
        GR.draw_star(screen, x+25*s, y-42*s, 8*s, 4*s, 6, self.accent)
        GR.draw_glow(screen, x+25*s, y-42*s, 10*s, self.accent, 3)
        
        # Orbes flotantes
        orbit_time = pygame.time.get_ticks() * 0.002
        for i in range(3):
            angle = orbit_time + i * (2*math.pi/3)
            ox = x + math.cos(angle) * 25*s
            oy = y - 10*s + math.sin(angle) * 10*s
            GR.draw_circle(screen, ox, oy, 4*s, self.accent)
            GR.draw_glow(screen, ox, oy, 6*s, self.accent, 2)


# ============================================================
# TORRE GEOMÉTRICA DETALLADA
# ============================================================
class GeometricTower:
    def __init__(self, owner):
        self.owner = owner
        self.anim_time = 0
        
        if owner == "player":
            self.primary = (80, 130, 200)
            self.secondary = (60, 100, 160)
            self.accent = (150, 200, 255)
        else:
            self.primary = (180, 70, 70)
            self.secondary = (140, 50, 50)
            self.accent = (255, 150, 150)
    
    def draw(self, screen, x, y, scale=1.0, anim_time=0):
        self.anim_time = anim_time
        GR = GeometryRenderer
        s = scale
        
        # Sombra base
        GR.draw_ellipse(screen, x, y+30*s, 50*s, 15*s, (0,0,0,60))
        
        # Base escalonada (3 niveles de rectángulos)
        GR.draw_rect(screen, x, y+25*s, 60*s, 12*s, (80, 80, 90))
        GR.draw_rect(screen, x, y+18*s, 50*s, 10*s, (100, 100, 110))
        GR.draw_rect(screen, x, y+10*s, 40*s, 12*s, self.secondary)
        
        # Detalles de ladrillos
        for row in range(3):
            for col in range(4):
                brick_x = x - 18*s + col * 10*s
                brick_y = y + 5*s + row * 8*s
                GR.draw_rect(screen, brick_x, brick_y, 8*s, 6*s, self.primary)
                GR.draw_rect(screen, brick_x, brick_y, 8*s, 6*s, (40,40,50), 1)
        
        # Plataforma superior
        GR.draw_rect(screen, x, y-5*s, 44*s, 8*s, (140, 140, 150))
        GR.draw_rect(screen, x, y-5*s, 44*s, 8*s, (100,100,110), 2)
        
        # Cúpula (semicírculo)
        GR.draw_arc(screen, x, y-15*s, 18*s, 0, math.pi, self.primary, int(6*s))
        GR.draw_line(screen, x, y-15*s, x, y-5*s, self.accent, 2)
        
        # Cañón rotativo
        angle = math.sin(anim_time * 2) * 0.3
        cannon_x = x + math.cos(angle) * 20*s
        cannon_y = y - 15*s + math.sin(angle) * 5*s
        
        GR.draw_rect(screen, x, y-15*s, 12*s, 10*s, (140, 140, 150))
        GR.draw_rect(screen, cannon_x+15*s, cannon_y, 35*s, 8*s, (60, 60, 70))
        GR.draw_rect(screen, cannon_x+35*s, cannon_y-3*s, 12*s, 4*s, (40, 40, 50))
        GR.draw_ellipse(screen, cannon_x+42*s, cannon_y, 6*s, 10*s, (30, 30, 35))
        
        # Ojos de la torre (círculos)
        GR.draw_circle(screen, x-12*s, y-8*s, 5*s, self.accent)
        GR.draw_circle(screen, x-12*s, y-8*s, 3*s, (255, 255, 255))
        GR.draw_circle(screen, x+12*s, y-8*s, 5*s, self.accent)
        GR.draw_circle(screen, x+12*s, y-8*s, 3*s, (255, 255, 255))
        
        # Antena con luz parpadeante
        GR.draw_line(screen, x, y-15*s, x, y-35*s, (140, 140, 150), 3)
        blink = (math.sin(anim_time * 8) > 0)
        light_color = (0, 255, 0) if blink else (255, 50, 50)
        GR.draw_circle(screen, x, y-37*s, 5*s, light_color)
        GR.draw_glow(screen, x, y-37*s, 8*s, light_color, 2)
        
        # Escudo lateral
        shield_points = [
            (x-28*s, y-5*s), (x-38*s, y-15*s), (x-38*s, y+5*s), (x-28*s, y+10*s)
        ]
        GR.draw_polygon(screen, shield_points, self.primary)
        GR.draw_polygon(screen, [
            (x-30*s, y-5*s), (x-35*s, y-10*s), (x-35*s, y)
        ], (255, 255, 255))
        
        # Engranajes decorativos
        GR.draw_circle(screen, x-15*s, y+15*s, 6*s, (140, 140, 150))
        GR.draw_circle(screen, x-15*s, y+15*s, 4*s, (60, 60, 70))
        GR.draw_circle(screen, x+15*s, y+15*s, 6*s, (140, 140, 150))
        GR.draw_circle(screen, x+15*s, y+15*s, 4*s, (60, 60, 70))
        
        # Escalera
        for i in range(5):
            GR.draw_line(screen, x-10*s, y+22*s-i*5*s, x+10*s, y+22*s-i*5*s, (120, 120, 130), 1)
        
        # Barra de vida de torre
        GR.draw_health_bar(screen, x, y-50*s, 50*s, 8*s, 600, 600)


# ============================================================
# EFECTOS VISUALES GEOMÉTRICOS
# ============================================================
class GeometricEffects:
    @staticmethod
    def draw_explosion(screen, x, y, progress, max_radius=50, color=(255, 200, 50)):
        """Explosión con ondas concéntricas"""
        GR = GeometryRenderer
        
        # Onda de choque
        current_r = max_radius * progress
        alpha = int(255 * (1 - progress))
        
        surf = pygame.Surface((max_radius*4, max_radius*4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color[:3], alpha//3), (max_radius*2, max_radius*2), int(current_r))
        screen.blit(surf, (int(x-max_radius*2), int(y-max_radius*2)))
        
        # Partículas geométricas
        num_particles = 12
        for i in range(num_particles):
            angle = (2 * math.pi * i) / num_particles
            dist = current_r * (0.5 + 0.5 * math.sin(progress * 10 + i))
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist
            size = 5 * (1 - progress)
            GR.draw_polygon(screen, [
                (px, py-size), (px+size, py), (px, py+size), (px-size, py)
            ], color)
    
    @staticmethod
    def draw_shield_effect(screen, x, y, radius, intensity=1.0):
        """Campo de fuerza hexagonal"""
        GR = GeometryRenderer
        
        hex_points = []
        for i in range(6):
            angle = i * math.pi / 3
            hx = x + math.cos(angle) * radius
            hy = y + math.sin(angle) * radius
            hex_points.append((hx, hy))
        
        # Hexágonos concéntricos rotando
        for j in range(3):
            rotation = pygame.time.get_ticks() * 0.001 * (j + 1) * (1 if j % 2 == 0 else -1)
            scaled_points = []
            scale = 1 - j * 0.2
            for px, py in hex_points:
                dx = px - x
                dy = py - y
                # Rotar
                new_x = x + (dx * math.cos(rotation) - dy * math.sin(rotation)) * scale
                new_y = y + (dx * math.sin(rotation) + dy * math.cos(rotation)) * scale
                scaled_points.append((new_x, new_y))
            
            alpha = int(100 * intensity * (1 - j * 0.3))
            color = (100, 150, 255, alpha) if j % 2 == 0 else (150, 200, 255, alpha)
            GR.draw_polygon(screen, scaled_points, color)
            GR.draw_polygon(screen, scaled_points, (255, 255, 255, alpha), 2)
    
    @staticmethod
    def draw_laser_beam(screen, x1, y1, x2, y2, color=(255, 50, 50), width=4):
        """Rayo láser con núcleo brillante"""
        GR = GeometryRenderer
        
        # Glow exterior
        for i in range(3, 0, -1):
            GR.draw_line(screen, x1, y1, x2, y2, (*color[:3], 50), width + i*3)
        
        # Rayo principal
        GR.draw_line(screen, x1, y1, x2, y2, color, width)
        
        # Núcleo blanco
        GR.draw_line(screen, x1, y1, x2, y2, (255, 255, 255), max(1, width-2))
        
        # Impacto
        GR.draw_glow(screen, x2, y2, 20, color, 3)
        GR.draw_star(screen, x2, y2, 10, 5, 4, (255, 255, 255))
    
    @staticmethod
    def draw_teleport_effect(screen, x, y, progress):
        """Efecto de teleportación con espiral"""
        GR = GeometryRenderer
        
        num_lines = 8
        for i in range(num_lines):
            angle = (2 * math.pi * i) / num_lines + progress * math.pi * 4
            inner_r = 10 + progress * 30
            outer_r = inner_r + 20 * (1 - progress)
            
            x1 = x + math.cos(angle) * inner_r
            y1 = y + math.sin(angle) * inner_r
            x2 = x + math.cos(angle + 0.3) * outer_r
            y2 = y + math.sin(angle + 0.3) * outer_r
            
            alpha = int(255 * (1 - progress))
            color = (100, 200, 255, alpha)
            GR.draw_line(screen, x1, y1, x2, y2, color, 3)


# ============================================================
# HEXÁGONO GEOMÉTRICO MEJORADO
# ============================================================
class GeometricHex:
    @staticmethod
    def draw_hex(screen, x, y, radius, color, border_color=None, border_width=2, height=0):
        """Hexágono 3D con paredes laterales"""
        GR = GeometryRenderer
        
        # Calcular vértices
        vertices = []
        for i in range(6):
            angle = (math.pi / 3) * i
            vx = x + radius * math.cos(angle)
            vy = y + radius * math.sin(angle)
            vertices.append((vx, vy))
        
        # Si tiene altura (3D), dibujar paredes
        if height > 0:
            for i in range(6):
                next_i = (i + 1) % 6
                wall = [
                    vertices[i],
                    vertices[next_i],
                    (vertices[next_i][0], vertices[next_i][1] + height),
                    (vertices[i][0], vertices[i][1] + height)
                ]
                # Color más oscuro para paredes
                dark_color = tuple(max(0, c - 40) for c in color[:3])
                GR.draw_polygon(screen, wall, dark_color)
        
        # Cara superior
        GR.draw_polygon(screen, vertices, color)
        if border_color:
            GR.draw_polygon(screen, vertices, border_color, border_width)
        
        # Líneas internas decorativas
        if border_color:
            for i in range(0, 6, 2):
                inner_start = (
                    x + (vertices[i][0] - x) * 0.7,
                    y + (vertices[i][1] - y) * 0.7
                )
                inner_end = (
                    x + (vertices[(i+3)%6][0] - x) * 0.7,
                    y + (vertices[(i+3)%6][1] - y) * 0.7
                )
                GR.draw_line(screen, inner_start[0], inner_start[1], 
                           inner_end[0], inner_end[1], border_color, 1)
    
    @staticmethod
    def draw_hex_grid(screen, cols, rows, start_x, start_y, radius, gap=0):
        """Grid completo de hexágonos"""
        GR = GeometryRenderer
        hex_height = radius * 1.732
        width_step = radius * 1.5 + gap
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * width_step
                y = start_y + row * hex_height
                if col % 2 == 1:
                    y += hex_height / 2
                
                # Color según posición
                if row < 2:
                    color = (100, 60, 60)  # Enemigo
                    border = (150, 100, 100)
                elif row > rows - 3:
                    color = (60, 80, 120)  # Jugador
                    border = (100, 150, 200)
                else:
                    color = (70, 70, 70)  # Neutral
                    border = (120, 120, 120)
                
                GeometricHex.draw_hex(screen, x, y, radius - gap, color, border, 2, 6)
