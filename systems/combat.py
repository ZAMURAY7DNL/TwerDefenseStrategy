"""
Sistema de Combate
"""
from config.constants import COMBAT_DURATION, COLOR_PROJECTILE_PLAYER, COLOR_PROJECTILE_ENEMY


class CombatSystem:
    """Sistema de combate del juego"""
    
    def __init__(self):
        self.combat_timer = 0
        self.duration = COMBAT_DURATION
    
    def start_combat(self, game):
        """Inicia la fase de combate"""
        game.phase = "combat"
        self.combat_timer = self.duration
        
        # Resetear estados de unidades
        for unit in game.player_units + game.enemy_units:
            unit.has_moved = False
            unit.attack_cooldown = 0
    
    def update(self, game, dt):
        """Actualiza el combate"""
        self.combat_timer -= dt
        
        # Actualizar partículas
        game.particles.update(dt)
        
        # Actualizar unidades
        for unit in game.player_units + game.enemy_units:
            unit.update(dt, game.grass)
        
        # Actualizar torres
        for tower in game.player_towers + game.enemy_towers:
            tower.update(dt)
        
        # Procesar ataques
        self._process_attacks(game)
        
        # Actualizar proyectiles
        self._update_projectiles(game)
        
        # Verificar fin del combate
        if self.combat_timer <= 0:
            return True  # Fin del combate
        
        return False
    
    def _process_attacks(self, game):
        """Procesa los ataques de todas las unidades"""
        # Ataques del jugador
        for attacker in game.player_units + game.player_towers:
            if not attacker.is_alive() or attacker.attack_cooldown > 0:
                continue
            
            target = self._find_target(attacker, game.enemy_units + game.enemy_towers)
            if target and self._in_range(attacker, target):
                self._create_projectile(attacker, target, game, COLOR_PROJECTILE_PLAYER, "player")
                attacker.attack_cooldown = attacker.attack_speed
        
        # Ataques del enemigo
        for attacker in game.enemy_units + game.enemy_towers:
            if not attacker.is_alive() or attacker.attack_cooldown > 0:
                continue
            
            target = self._find_target(attacker, game.player_units + game.player_towers)
            if target and self._in_range(attacker, target):
                self._create_projectile(attacker, target, game, COLOR_PROJECTILE_ENEMY, "enemy")
                attacker.attack_cooldown = attacker.attack_speed
    
    def _find_target(self, attacker, targets):
        """Encuentra el objetivo más cercano"""
        best = None
        best_dist = float('inf')
        
        ax = getattr(attacker, 'visual_x', None) if hasattr(attacker, 'visual_x') else getattr(attacker, 'x', 0)
        ay = getattr(attacker, 'visual_y', None) if hasattr(attacker, 'visual_y') else getattr(attacker, 'y', 0)
        
        for target in targets:
            if not target.is_alive():
                continue
            
            tx = getattr(target, 'visual_x', None) if hasattr(target, 'visual_x') else getattr(target, 'x', 0)
            ty = getattr(target, 'visual_y', None) if hasattr(target, 'visual_y') else getattr(target, 'y', 0)
            
            dist = ((ax - tx)**2 + (ay - ty)**2)**0.5
            if dist < best_dist:
                best_dist = dist
                best = target
        
        return best
    
    def _in_range(self, attacker, target):
        """Verifica si el objetivo está en rango"""
        ax = getattr(attacker, 'visual_x', None) if hasattr(attacker, 'visual_x') else getattr(attacker, 'x', 0)
        ay = getattr(attacker, 'visual_y', None) if hasattr(attacker, 'visual_y') else getattr(attacker, 'y', 0)
        tx = getattr(target, 'visual_x', None) if hasattr(target, 'visual_x') else getattr(target, 'x', 0)
        ty = getattr(target, 'visual_y', None) if hasattr(target, 'visual_y') else getattr(target, 'y', 0)
        
        dist = ((ax - tx)**2 + (ay - ty)**2)**0.5
        return dist <= attacker.get_attack_range_pixels()
    
    def _create_projectile(self, attacker, target, game, color, owner):
        """Crea un proyectil"""
        from entities.projectile import TracerProjectile
        
        ax = getattr(attacker, 'visual_x', None) if hasattr(attacker, 'visual_x') else getattr(attacker, 'x', 0)
        ay = getattr(attacker, 'visual_y', None) if hasattr(attacker, 'visual_y') else getattr(attacker, 'y', 0)
        
        proj = TracerProjectile(ax, ay, target, attacker.attack, color, owner, game.particles)
        game.projectiles.append(proj)
    
    def _update_projectiles(self, game):
        """Actualiza los proyectiles"""
        for proj in game.projectiles[:]:
            proj.update(0.016)  # dt = 60fps
            if not proj.active:
                game.projectiles.remove(proj)
    
    def end_combat(self, game):
        """Termina el combate y limpia"""
        game.projectiles.clear()
        game.particles.particles.clear()
        
        # Limpiar unidades y torres muertas
        for tile in game.grid.values():
            if getattr(tile, 'unit', None) and not tile.unit.is_alive():
                tile.unit = None
            if getattr(tile, 'tower', None) and not tile.tower.is_alive():
                tile.tower = None
        
        # Actualizar listas
        game.player_units = [u for u in game.player_units if u.is_alive()]
        game.enemy_units = [u for u in game.enemy_units if u.is_alive()]
        game.player_towers = [t for t in game.player_towers if t.is_alive()]
        game.enemy_towers = [t for t in game.enemy_towers if t.is_alive()]
        
        game.turn_number += 1
        game.phase = "player_turn"
    
    def get_time_remaining(self):
        """Retorna el tiempo restante"""
        return self.combat_timer
