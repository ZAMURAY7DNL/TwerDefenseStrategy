"""
Combat Handler - Manejador de Combate
======================================
Gestiona ataques, proyectiles y lógica de combate.
"""
from entities import TracerProjectile
from config.constants import *


class CombatHandler:
    """Maneja todas las operaciones de combate."""
    
    def __init__(self, grid_manager, unit_manager, particle_system):
        self.grid = grid_manager
        self.units = unit_manager
        self.particles = particle_system
        self.projectiles = []
        self.combat_attacks_done = False
    
    def execute_move_free(self, from_tile, to_tile, active_unit_checker):
        """
        Ejecuta movimiento gratuito (1 vez por turno).
        Returns: True si el movimiento fue exitoso.
        """
        unit = from_tile.unit
        if not unit:
            return False
        
        # Verificar que sea la unidad activa
        if not active_unit_checker(unit):
            return False
        
        # Verificar que no se haya movido ya
        if getattr(unit, 'has_moved', False):
            print("[AVISO] Ya te moviste este turno")
            return False
        
        # Ejecutar movimiento
        self.particles.spawn_dust(from_tile.x, from_tile.y)
        from_tile.unit = None
        to_tile.unit = unit
        self.particles.spawn_dust(to_tile.x, to_tile.y)
        unit.move_to(to_tile.x, to_tile.y)
        unit.has_moved = True
        
        return True
    
    def execute_hero_attack(self, hero, target):
        """Héroe ataca usando AP."""
        if not hasattr(hero, 'use_power'):
            return None
        
        result = hero.use_power('slash', target)
        
        if result['success']:
            # Efectos visuales
            tx = getattr(target, 'visual_x', 0)
            ty = getattr(target, 'visual_y', 0)
            self.particles.spawn_attack(tx, ty, "player")
            
            # Proyectil
            ax = getattr(hero, 'visual_x', 0)
            ay = getattr(hero, 'visual_y', 0)
            proj = TracerProjectile(ax, ay, target, result.get('damage', 0),
                                   COLOR_PROJECTILE_PLAYER, "player", self.particles)
            self.projectiles.append(proj)
        else:
            print(f"[ERROR] {result['message']}")
        
        return result
    
    def execute_troop_attack(self, troop, target):
        """Tropa ataca (sin AP)."""
        damage = getattr(troop, 'attack', 10)
        actual = target.take_damage(damage)
        
        print(f"[ATAQUE] {troop.unit_type} ataca por {actual}")
        
        # Efectos visuales
        tx = getattr(target, 'visual_x', 0)
        ty = getattr(target, 'visual_y', 0)
        self.particles.spawn_attack(tx, ty, "player")
        
        # Proyectil
        ax = getattr(troop, 'visual_x', 0)
        ay = getattr(troop, 'visual_y', 0)
        proj = TracerProjectile(ax, ay, target, actual,
                               COLOR_PROJECTILE_PLAYER, "player", self.particles)
        self.projectiles.append(proj)
        
        # Marcar que la tropa actuó
        troop.has_moved = True
        
        return actual
    
    def execute_hero_power(self, hero, target, power_id):
        """Ejecuta un poder del héroe."""
        if not hasattr(hero, 'use_power'):
            return None
        
        result = hero.use_power(power_id, target)
        
        if result['success']:
            print(f"[HEROE] Usa {power_id} causando {result.get('damage', 0)} daño")
            
            # Efectos visuales
            tx = getattr(target, 'visual_x', 0)
            ty = getattr(target, 'visual_y', 0)
            self.particles.spawn_attack(tx, ty, "player")
            
            # Proyectil especial según poder
            hx = getattr(hero, 'visual_x', 0)
            hy = getattr(hero, 'visual_y', 0)
            
            color = (255, 200, 100) if power_id == 'slash' else \
                    (255, 100, 50) if power_id == 'power_strike' else \
                    (100, 255, 100) if power_id == 'heal' else (200, 200, 255)
            
            proj = TracerProjectile(hx, hy, target, result.get('damage', 0), 
                                   color, "player", self.particles)
            self.projectiles.append(proj)
        
        return result
    
    def execute_special_attack(self, unit, target, attack_name):
        """Ejecuta un ataque especial."""
        damage_mult = {
            "Carga": 1.5,
            "Furia": 2.0,
            "Suprimir": 0.8,
            "Refuerzo": 0.5,
            "Disparo Área": 1.2,
            "Trampa": 1.0,
            "Disparo Largo": 2.5,
            "Marca": 0.3,
        }.get(attack_name, 1.0)
        
        damage = int(unit.attack * damage_mult)
        target.take_damage(damage)
        
        # Efectos visuales
        tx = getattr(target, 'visual_x', 0)
        ty = getattr(target, 'visual_y', 0)
        self.particles.spawn_attack(tx, ty, unit.owner)
        
        # Crear proyectil visual
        ux = getattr(unit, 'visual_x', 0)
        uy = getattr(unit, 'visual_y', 0)
        proj = TracerProjectile(ux, uy, target, damage, (255, 200, 100), unit.owner, self.particles)
        self.projectiles.append(proj)
        
        return damage
    
    def execute_basic_attack(self, attacker, target):
        """Ejecuta ataque básico."""
        damage = getattr(attacker, 'attack', 10)
        actual = target.take_damage(damage)
        
        # Efectos visuales
        tx = getattr(target, 'visual_x', 0)
        ty = getattr(target, 'visual_y', 0)
        self.particles.spawn_attack(tx, ty, attacker.owner if hasattr(attacker, 'owner') else "player")
        
        # Proyectil
        from entities import TracerProjectile
        ax = getattr(attacker, 'visual_x', 0)
        ay = getattr(attacker, 'visual_y', 0)
        color = COLOR_PROJECTILE_PLAYER if getattr(attacker, 'owner', 'player') == 'player' else COLOR_PROJECTILE_ENEMY
        proj = TracerProjectile(ax, ay, target, actual, color, 
                               getattr(attacker, 'owner', 'player'), self.particles)
        self.projectiles.append(proj)
        
        return actual
    
    def process_all_attacks_once(self):
        """Cada unidad/torre lanza exactamente un ataque si hay objetivo en rango."""
        self.combat_attacks_done = False
        
        # Ataques del jugador
        for attacker in self.units.player_units + self.units.player_towers:
            if not attacker.is_alive():
                continue
            if getattr(attacker, 'has_attacked', False):
                continue
            
            target = self._find_target(attacker, self.units.enemy_units + self.units.enemy_towers)
            if target and self._in_range(attacker, target):
                ax = getattr(attacker, 'visual_x', getattr(attacker, 'x', 0))
                ay = getattr(attacker, 'visual_y', getattr(attacker, 'y', 0))
                
                proj = TracerProjectile(ax, ay, target, attacker.attack,
                                       COLOR_PROJECTILE_PLAYER, "player", self.particles)
                self.projectiles.append(proj)
                attacker.has_attacked = True
        
        # Ataques enemigos
        for attacker in self.units.enemy_units + self.units.enemy_towers:
            if not attacker.is_alive():
                continue
            if getattr(attacker, 'has_attacked', False):
                continue
            
            target = self._find_target(attacker, self.units.player_units + self.units.player_towers)
            if target and self._in_range(attacker, target):
                ax = getattr(attacker, 'visual_x', getattr(attacker, 'x', 0))
                ay = getattr(attacker, 'visual_y', getattr(attacker, 'y', 0))
                
                proj = TracerProjectile(ax, ay, target, attacker.attack,
                                       COLOR_PROJECTILE_ENEMY, "enemy", self.particles)
                self.projectiles.append(proj)
                attacker.has_attacked = True
        
        self.combat_attacks_done = True
    
    def _find_target(self, attacker, targets):
        """Encuentra el objetivo más cercano."""
        best = None
        best_dist = float('inf')
        ax = getattr(attacker, 'visual_x', None) if hasattr(attacker, 'visual_x') else getattr(attacker, 'x', 0)
        ay = getattr(attacker, 'visual_y', None) if hasattr(attacker, 'visual_y') else getattr(attacker, 'y', 0)
        
        for target in targets:
            if not target.is_alive():
                continue
            tx = getattr(target, 'visual_x', None) if hasattr(target, 'visual_x') else getattr(target, 'x', 0)
            ty = getattr(target, 'visual_y', None) if hasattr(target, 'visual_y') else getattr(target, 'y', 0)
            dist = ((ax-tx)**2 + (ay-ty)**2)**0.5
            if dist < best_dist:
                best_dist = dist
                best = target
        return best
    
    def _in_range(self, attacker, target):
        """Verifica si el objetivo está en rango."""
        ax = getattr(attacker, 'visual_x', None) if hasattr(attacker, 'visual_x') else getattr(attacker, 'x', 0)
        ay = getattr(attacker, 'visual_y', None) if hasattr(attacker, 'visual_y') else getattr(attacker, 'y', 0)
        tx = getattr(target, 'visual_x', None) if hasattr(target, 'visual_x') else getattr(target, 'x', 0)
        ty = getattr(target, 'visual_y', None) if hasattr(target, 'visual_y') else getattr(target, 'y', 0)
        return ((ax-tx)**2 + (ay-ty)**2)**0.5 <= attacker.get_attack_range_pixels()
    
    def reset_attack_flags(self):
        """Resetea flags de ataque de todas las unidades."""
        for unit in self.units.player_units + self.units.enemy_units:
            unit.has_attacked = False
            unit.attack_cooldown = 0
        
        for tower in self.units.player_towers + self.units.enemy_towers:
            tower.has_attacked = False
    
    def update_projectiles(self, dt):
        """Actualiza proyectiles en vuelo."""
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.active:
                self.projectiles.remove(proj)
    
    def clear_projectiles(self):
        """Limpia todos los proyectiles."""
        self.projectiles.clear()
    
    def are_all_projectiles_done(self):
        """Verifica si todos los proyectiles han terminado."""
        return self.combat_attacks_done and not self.projectiles
    
    def draw_projectiles(self, screen):
        """Dibuja todos los proyectiles."""
        for proj in self.projectiles:
            proj.draw(screen)
