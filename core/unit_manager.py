"""
Unit Manager - Gestión de Unidades
===================================
Crea, configura y gestiona todas las unidades del juego.
"""
from entities import Hero, UltraUnit, UltraTower
from systems.combat_dayr import ActionPointsSystem


class UnitManager:
    """Gestiona la creación y configuración de unidades."""
    
    def __init__(self, grid_manager):
        self.grid = grid_manager
        self.player_units = []
        self.enemy_units = []
        self.player_towers = []
        self.enemy_towers = []
        self.hero = None
        self.enemy_hero = None
    
    def setup_initial_units(self):
        """Configura las unidades iniciales del juego."""
        self._create_player_hero()
        self._create_player_troops()
        self._create_player_towers()
        self._create_enemy_hero()
        self._create_enemy_troops()
        self._create_enemy_towers()
    
    def _create_player_hero(self):
        """Crea el héroe del jugador."""
        self.hero = Hero(name="Comandante")
        hero_tile = self.grid.get_tile(4, 3)
        if hero_tile:
            hero_tile.unit = self.hero
            self.hero.set_position(hero_tile.x, hero_tile.y)
            self.player_units.append(self.hero)
    
    def _create_player_troops(self):
        """Crea las tropas iniciales del jugador."""
        configs = [
            ("berserker", 1, 2),
            ("assault", 3, 3),
            ("ranger", 5, 2),
            ("sniper", 6, 4),
            ("assault", 2, 4)
        ]
        
        for unit_type, col, row in configs:
            if (col, row) == (4, 3):  # Skip posición del héroe
                continue
            unit = UltraUnit(unit_type, "player")
            tile = self.grid.get_tile(col, row)
            if tile:
                tile.unit = unit
                unit.set_position(tile.x, tile.y)
                self.player_units.append(unit)
    
    def _create_player_towers(self):
        """Crea las torres del jugador."""
        for col, row in [(2, 0), (5, 0)]:
            tile = self.grid.get_tile(col, row)
            if tile:
                tower = UltraTower("player")
                tower.set_position(tile.x, tile.y)
                tile.tower = tower
                self.player_towers.append(tower)
    
    def _create_enemy_hero(self):
        """Crea el héroe enemigo."""
        self.enemy_hero = UltraUnit("berserker", "enemy")
        self.enemy_hero.name = "Señor Oscuro"
        self.enemy_hero.max_health = 120
        self.enemy_hero.health = 120
        self.enemy_hero.attack = 35
        self.enemy_hero.is_hero = True
        
        # Sistema de AP para héroe enemigo
        self.enemy_hero.action_points = ActionPointsSystem(max_ap=2, recovery_per_turn=2)
        self.enemy_hero.action_points.reset()
        
        enemy_hero_tile = self.grid.get_tile(4, -3)
        if enemy_hero_tile:
            enemy_hero_tile.unit = self.enemy_hero
            self.enemy_hero.set_position(enemy_hero_tile.x, enemy_hero_tile.y)
            self.enemy_units.append(self.enemy_hero)
    
    def _create_enemy_troops(self):
        """Crea las tropas enemigas iniciales."""
        enemy_configs = [
            ("berserker", 2, -3),
            ("assault", 3, -3),
            ("ranger", 5, -3),
            ("sniper", 3, -4),
            ("assault", 5, -4)
        ]
        
        for unit_type, col, row in enemy_configs:
            if (col, row) == (4, -3):  # Skip posición del héroe
                continue
            unit = UltraUnit(unit_type, "enemy")
            tile = self.grid.get_tile(col, row)
            if tile:
                tile.unit = unit
                unit.set_position(tile.x, tile.y)
                self.enemy_units.append(unit)
    
    def _create_enemy_towers(self):
        """Crea las torres enemigas."""
        for col, row in [(3, -1), (4, -1)]:
            tile = self.grid.get_tile(col, row)
            if tile:
                tower = UltraTower("enemy")
                tower.set_position(tile.x, tile.y)
                tile.tower = tower
                self.enemy_towers.append(tower)
    
    def get_all_player_units(self):
        """Retorna todas las unidades del jugador."""
        return self.player_units
    
    def get_all_enemy_units(self):
        """Retorna todas las unidades enemigas."""
        return self.enemy_units
    
    def get_all_units(self):
        """Retorna todas las unidades (ambos bandos)."""
        return self.player_units + self.enemy_units
    
    def get_all_towers(self):
        """Retorna todas las torres (ambos bandos)."""
        return self.player_towers + self.enemy_towers
    
    def get_alive_player_units(self):
        """Retorna unidades del jugador vivas."""
        return [u for u in self.player_units if u.is_alive()]
    
    def get_alive_enemy_units(self):
        """Retorna unidades enemigas vivas."""
        return [u for u in self.enemy_units if u.is_alive()]
    
    def get_alive_player_towers(self):
        """Retorna torres del jugador vivas."""
        return [t for t in self.player_towers if t.is_alive()]
    
    def get_alive_enemy_towers(self):
        """Retorna torres enemigas vivas."""
        return [t for t in self.enemy_towers if t.is_alive()]
    
    def cleanup_dead_units(self):
        """Elimina unidades muertas de las listas."""
        self.player_units = [u for u in self.player_units if u.is_alive()]
        self.enemy_units = [u for u in self.enemy_units if u.is_alive()]
        self.player_towers = [t for t in self.player_towers if t.is_alive()]
        self.enemy_towers = [t for t in self.enemy_towers if t.is_alive()]
    
    def reset_units(self):
        """Resetea las listas de unidades."""
        self.player_units.clear()
        self.enemy_units.clear()
        self.player_towers.clear()
        self.enemy_towers.clear()
        self.hero = None
        self.enemy_hero = None
    
    def get_troops_only(self):
        """Retorna solo las tropas (sin el héroe)."""
        return [u for u in self.player_units if not getattr(u, 'is_hero', False)]
    
    def can_unit_attack_anyone(self, unit, enemies):
        """Verifica si una unidad tiene algún enemigo a rango."""
        attack_range = getattr(unit, 'range', 1) * 100
        ux = getattr(unit, 'visual_x', 0)
        uy = getattr(unit, 'visual_y', 0)
        
        alive_enemies = [e for e in enemies if e.is_alive()]
        for enemy in alive_enemies:
            ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
            dist = ((ux - ex)**2 + (uy - ey)**2)**0.5
            if dist <= attack_range:
                return True
        return False
    
    def find_nearest_enemy(self, unit, enemies):
        """Encuentra el enemigo más cercano a la unidad."""
        best = None
        best_dist = float('inf')
        
        unit_x = getattr(unit, 'visual_x', 0)
        unit_y = getattr(unit, 'visual_y', 0)
        
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            ex = getattr(enemy, 'visual_x', 0)
            ey = getattr(enemy, 'visual_y', 0)
            dist = ((unit_x - ex)**2 + (unit_y - ey)**2)**0.5
            if dist < best_dist:
                best_dist = dist
                best = enemy
        return best
    
    def update(self, dt, grass_system):
        """Actualiza todas las unidades."""
        for unit in self.player_units + self.enemy_units:
            if hasattr(unit, 'update'):
                import inspect
                try:
                    sig = inspect.signature(unit.update)
                    params = list(sig.parameters.keys())
                    if len(params) >= 3:
                        unit.update(dt, grass_system)
                    else:
                        unit.update(dt)
                except Exception:
                    pass
        
        for tower in self.player_towers + self.enemy_towers:
            if hasattr(tower, 'update'):
                tower.update(dt)
