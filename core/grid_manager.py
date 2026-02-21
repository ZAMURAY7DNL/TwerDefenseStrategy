"""
Grid Manager - Gestión del Grid Hexagonal
=========================================
Maneja la creación, consulta y operaciones sobre el grid de hexágonos.
"""
import math
from config.constants import *
from systems.grid import HoneycombTile


class GridManager:
    """Gestiona el grid hexagonal del juego."""
    
    def __init__(self):
        self.grid = {}
        self.neutral_zone_y = 0
        self._create_grid()
    
    def _create_grid(self):
        """Crea el grid hexagonal con zonas de jugador y enemigo."""
        total_width = GRID_COLS * HEX_WIDTH * 0.75
        start_x = (SCREEN_WIDTH - total_width) // 2 + HEX_RADIUS
        
        # Zona del jugador (filas positivas)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = start_x + col * HEX_WIDTH * 0.75
                y = ZONE_PLAYER_Y + row * HEX_HEIGHT
                if col % 2 == 1:
                    y += HEX_HEIGHT // 2
                
                tile = HoneycombTile(col, row, int(x), int(y), "player", False)
                self.grid[(col, row)] = tile
        
        # Zona enemiga (filas negativas)
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = start_x + col * HEX_WIDTH * 0.75
                y = ZONE_ENEMY_Y + (GRID_ROWS - 1 - row) * HEX_HEIGHT
                if col % 2 == 1:
                    y += HEX_HEIGHT // 2
                
                tile = HoneycombTile(col, -(row + 1), int(x), int(y), "enemy", False)
                self.grid[(col, -(row + 1))] = tile
        
        self.neutral_zone_y = (ZONE_ENEMY_Y + ZONE_PLAYER_Y) // 2
    
    def find_tile(self, pos):
        """Encuentra el tile en la posición dada (mouse)."""
        for tile in self.grid.values():
            dx = pos[0] - tile.x
            dy = pos[1] - tile.y
            if (dx**2 + dy**2)**0.5 <= HEX_RADIUS * 0.9:
                return tile
        return None
    
    def get_unit_tile(self, unit):
        """Obtiene el tile donde está ubicada una unidad."""
        for tile in self.grid.values():
            if getattr(tile, 'unit', None) == unit:
                return tile
        return None
    
    def get_tower_tile(self, tower):
        """Obtiene el tile donde está ubicada una torre."""
        for tile in self.grid.values():
            if getattr(tile, 'tower', None) == tower:
                return tile
        return None
    
    def get_tile(self, col, row):
        """Obtiene un tile por coordenadas."""
        return self.grid.get((col, row))
    
    def update_valid_moves(self, selected_tile):
        """Actualiza los tiles válidos para movimiento."""
        # Limpiar movimientos válidos previos
        for tile in self.grid.values():
            tile.valid_move = False
        
        if not selected_tile:
            return
        
        unit = selected_tile.unit
        if not unit or unit.has_moved:
            return
        
        # Marcar vecinos vacíos como válidos
        neighbors = selected_tile.get_neighbors(self.grid)
        for neighbor in neighbors:
            if neighbor.is_empty():
                neighbor.valid_move = True
    
    def move_unit(self, from_tile, to_tile):
        """Mueve una unidad de un tile a otro."""
        unit = from_tile.unit
        to_tile.unit = unit
        from_tile.unit = None
        unit.move_to(to_tile.x, to_tile.y)
    
    def clear_dead_units(self):
        """Limpia unidades muertas del grid."""
        for tile in self.grid.values():
            if getattr(tile, 'unit', None) and not tile.unit.is_alive():
                tile.unit = None
            if getattr(tile, 'tower', None) and not tile.tower.is_alive():
                tile.tower = None
    
    def clear_selections(self):
        """Limpia todas las selecciones del grid."""
        for tile in self.grid.values():
            tile.selected = False
            tile.valid_move = False
    
    def get_empty_tiles_in_zone(self, zone="enemy"):
        """Obtiene tiles vacíos en una zona específica."""
        return [t for t in self.grid.values() 
                if t.owner == zone and t.is_empty()]
    
    def get_tiles_sorted_by_y(self):
        """Retorna tiles ordenados por coordenada Y (para dibujado)."""
        return sorted(self.grid.values(), key=lambda t: t.y)
    
    def get_all_units_and_towers(self, sorted_by_y=True):
        """Obtiene todas las unidades y torres con sus posiciones."""
        items = []
        for tile in self.grid.values():
            if tile.unit:
                visual_y = tile.unit.visual_y if tile.unit.is_moving else tile.y
                items.append((visual_y, tile.unit, tile))
            if tile.tower:
                items.append((tile.y, tile.tower, tile))
        
        if sorted_by_y:
            items.sort(key=lambda x: x[0])
        return items
    
    def update(self, mouse_pos):
        """Actualiza el estado de hover de los tiles."""
        for tile in self.grid.values():
            tile.update(mouse_pos)
