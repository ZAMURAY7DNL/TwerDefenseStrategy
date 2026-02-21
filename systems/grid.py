"""
Sistema de grilla hexagonal - Panal de abeja
"""
import pygame
import math


class HoneycombTile:
    """Tile hexagonal estilo panal de abeja"""
    
    def __init__(self, col, row, x, y, owner, inverted=False):
        from config.constants import HEX_RADIUS
        
        self.col = col
        self.row = row
        self.x = x
        self.y = y
        self.owner = owner
        self.inverted = inverted
        
        self.unit = None
        self.tower = None
        
        self.hovered = False
        self.selected = False
        self.valid_move = False
        self.oracle_recommended = False
        
        self.vertices = self._calculate_vertices()
        self.inner_vertices = self._calculate_inner_vertices(0.85)
        self.wall_height = 8
    
    def _calculate_vertices(self, scale=1.0):
        from config.constants import HEX_RADIUS
        
        vertices = []
        for i in range(6):
            angle = (math.pi / 3) * i  # Hexágono con lado plano hacia arriba
            if self.inverted:
                angle += math.pi
            vx = self.x + HEX_RADIUS * scale * math.cos(angle)
            vy = self.y + HEX_RADIUS * scale * math.sin(angle)
            vertices.append((vx, vy))
        return vertices
    
    def _calculate_inner_vertices(self, scale):
        return self._calculate_vertices(scale)
    
    def update(self, mouse_pos):
        from config.constants import HEX_RADIUS
        
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.hovered = (dx**2 + dy**2)**0.5 <= HEX_RADIUS * 0.9
    
    def draw(self, screen):
        from config.constants import (
            COLOR_HONEY_BORDER, COLOR_SELECTED, COLOR_VALID_MOVE,
            COLOR_HOVER, COLOR_PLAYER_ZONE, COLOR_ENEMY_ZONE,
            COLOR_NEUTRAL_ZONE, COLOR_ORACLE
        )
        
        # Determinar colores según estado
        if self.oracle_recommended:
            base_color = (255, 220, 100)
            wall_color = (200, 170, 50)
            glow = True
        elif self.selected:
            base_color = COLOR_SELECTED
            wall_color = (180, 100, 30)
            glow = True
        elif self.valid_move:
            base_color = COLOR_VALID_MOVE
            wall_color = (60, 180, 60)
            glow = False
        elif self.hovered:
            base_color = COLOR_HOVER
            wall_color = (200, 200, 80)
            glow = False
        elif self.owner == "player":
            base_color = COLOR_PLAYER_ZONE
            wall_color = (30, 60, 90)
            glow = False
        elif self.owner == "enemy":
            base_color = COLOR_ENEMY_ZONE
            wall_color = (80, 30, 30)
            glow = False
        else:
            base_color = COLOR_NEUTRAL_ZONE
            wall_color = (40, 40, 40)
            glow = False
        
        # Dibujar paredes laterales (efecto 3D)
        for i in range(6):
            next_i = (i + 1) % 6
            wall_points = [
                self.vertices[i],
                self.vertices[next_i],
                (self.vertices[next_i][0], self.vertices[next_i][1] + self.wall_height),
                (self.vertices[i][0], self.vertices[i][1] + self.wall_height)
            ]
            pygame.draw.polygon(screen, wall_color, wall_points)
        
        # Cara superior
        pygame.draw.polygon(screen, base_color, self.vertices)
        pygame.draw.polygon(screen, COLOR_HONEY_BORDER, self.vertices, 3)
        
        # Líneas internas del panal
        for i in range(0, 6, 2):
            line_color = (
                min(255, base_color[0] + 20),
                min(255, base_color[1] + 20),
                min(255, base_color[2] + 20)
            )
            pygame.draw.line(screen, line_color, self.inner_vertices[i], 
                           self.inner_vertices[(i+3)%6], 2)
        
        # Glow effect
        if glow:
            from config.constants import HEX_RADIUS
            glow_surf = pygame.Surface((HEX_RADIUS*3, HEX_RADIUS*3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 100, 60), 
                             (HEX_RADIUS*1.5, HEX_RADIUS*1.5), HEX_RADIUS)
            screen.blit(glow_surf, (self.x - HEX_RADIUS*1.5, self.y - HEX_RADIUS*1.5))
        
        # Indicador de oráculo
        if self.oracle_recommended:
            pygame.draw.circle(screen, COLOR_ORACLE, (self.x, self.y), 10)
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 6)
            font = pygame.font.SysFont("arial", 14, bold=True)
            text = font.render("K", True, (0, 0, 0))
            rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, rect)
    
    def get_neighbors(self, all_tiles):
        neighbors = []
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]
        
        if self.col % 2 == 0:
            directions.extend([(-1, -1), (1, -1)])
        else:
            directions.extend([(-1, 1), (1, 1)])
        
        for dc, dr in directions:
            neighbor_key = (self.col + dc, self.row + dr)
            if neighbor_key in all_tiles:
                neighbors.append(all_tiles[neighbor_key])
        
        return neighbors
    
    def is_empty(self):
        return self.unit is None and self.tower is None
