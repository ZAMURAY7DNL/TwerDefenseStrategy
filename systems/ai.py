"""
Sistema de Inteligencia Artificial
"""
from config.constants import ZONE_ENEMY_Y, ZONE_PLAYER_Y, AI_MOVE_DELAY


class AISystem:
    """Sistema de IA para el enemigo"""
    
    def __init__(self):
        self.ai_timer = 0
        self.move_delay = AI_MOVE_DELAY
    
    def update(self, game, dt):
        """Actualiza la IA - llama a la IA para mover unidades"""
        self.ai_timer += dt
        
        if self.ai_timer < self.move_delay:
            return
        
        self.ai_timer = 0
        self._execute_ai_moves(game)
    
    def _execute_ai_moves(self, game):
        """Ejecuta los movimientos de la IA"""
        for unit in game.enemy_units:
            if not unit.is_alive() or unit.has_moved:
                continue
            
            # Encontrar mejores movimientos
            neighbors = []
            for tile in game.grid.values():
                if tile.owner == "enemy" and tile.is_empty():
                    neighbors.append(tile)
            
            if neighbors:
                # IA mejorada: buscar la mejor posición
                best = self._find_best_position(neighbors, game)
                
                unit_tile = game.get_unit_tile(unit)
                if unit_tile:
                    unit_tile.unit = None
                best.unit = unit
                unit.move_to(best.x, best.y)
                unit.has_moved = True
    
    def _find_best_position(self, available_tiles, game):
        """Encuentra la mejor posición para las unidades enemigas"""
        best = None
        best_score = float('-inf')
        
        for tile in available_tiles:
            score = self._evaluate_position(tile, game)
            if score > best_score:
                best_score = score
                best = tile
        
        return best if best else available_tiles[0]
    
    def _evaluate_position(self, tile, game):
        """Evalúa qué tan buena es una posición"""
        score = 0
        
        # Preferir posiciones más cerca de la zona del jugador
        dist_to_player = abs(tile.y - ZONE_PLAYER_Y)
        score += (500 - dist_to_player) / 10
        
        # Evitar posiciones con muchas unidades aliadas cerca
        for other_tile in game.grid.values():
            if other_tile.unit and other_tile.unit.owner == "enemy":
                dist = ((tile.x - other_tile.x)**2 + (tile.y - other_tile.y)**2)**0.5
                if dist < 50:
                    score -= 20
        
        # Preferir posiciones con espacio para moverse
        empty_neighbors = sum(1 for n in tile.get_neighbors(game.grid) if n.is_empty())
        score += empty_neighbors * 10
        
        return score
    
    def reset(self):
        """Resetea el timer de IA"""
        self.ai_timer = 0


class CombatAI:
    """IA para decisiones de combate"""
    
    def __init__(self):
        self.difficulty = "normal"  # easy, normal, hard
    
    def should_attack(self, attacker, target, game):
        """Determina si debe atacar"""
        from config.constants import HEX_WIDTH
        
        dist = ((attacker.visual_x - target.visual_x)**2 + 
                (attacker.visual_y - target.visual_y)**2)**0.5
        attack_range = attacker.range * HEX_WIDTH * 0.9
        
        if dist > attack_range:
            return False
        
        # Según dificultad
        if self.difficulty == "easy":
            return random.random() < 0.5
        elif self.difficulty == "normal":
            return random.random() < 0.8
        else:  # hard
            return True
    
    def choose_target(self, attacker, potential_targets):
        """Elige el mejor objetivo para atacar"""
        if not potential_targets:
            return None
        
        # Priorizar unidades con menos salud
        if self.difficulty == "hard":
            return min(potential_targets, key=lambda t: t.health)
        
        # Normal: atacar al más cercano
        best = None
        best_dist = float('inf')
        
        for target in potential_targets:
            dist = ((attacker.visual_x - target.visual_x)**2 + 
                    (attacker.visual_y - target.visual_y)**2)**0.5
            if dist < best_dist:
                best_dist = dist
                best = target
        
        return best


import random
