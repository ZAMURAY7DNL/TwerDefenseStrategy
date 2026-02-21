"""
Enemy AI System - Inteligencia Artificial Enemiga
=================================================
Maneja toda la lógica de decisión y comportamiento de unidades enemigas.
"""
import random
from config.constants import ZONE_PLAYER_Y


class EnemyAI:
    """Sistema de IA para unidades enemigas."""
    
    def __init__(self, grid_manager, unit_manager, particle_system):
        self.grid = grid_manager
        self.units = unit_manager
        self.particles = particle_system
        self.projectiles = []
    
    def select_target(self, enemy, targets):
        """Selecciona el mejor objetivo para el enemigo."""
        ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
        
        candidates = []
        for target in targets:
            if not target.is_alive():
                continue
            
            tx, ty = getattr(target, 'visual_x', 0), getattr(target, 'visual_y', 0)
            dist = ((ex - tx)**2 + (ey - ty)**2)**0.5
            
            # Puntuación basada en múltiples factores
            score = 0
            
            # Preferir objetivos más débiles (menos HP)
            hp_ratio = getattr(target, 'health', 100) / getattr(target, 'max_health', 100)
            score += (1 - hp_ratio) * 50
            
            # Preferir objetivos más cercanos
            score -= dist * 0.5
            
            # Preferir el héroe (alta prioridad)
            if getattr(target, 'is_hero', False):
                score += 30
            
            # Penalizar unidades que se defienden
            if getattr(target, 'is_defending', False):
                score -= 20
            
            candidates.append((target, dist, score))
        
        if not candidates:
            return None
        
        # Ordenar por score descendente
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[0][0]
    
    def find_alternative_target(self, enemy, targets, excluded_target):
        """Encuentra un objetivo alternativo si el principal está bloqueado."""
        ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
        
        best = None
        best_dist = float('inf')
        
        for target in targets:
            if target == excluded_target:
                continue
            if not target.is_alive():
                continue
            
            tx, ty = getattr(target, 'visual_x', 0), getattr(target, 'visual_y', 0)
            dist = ((ex - tx)**2 + (ey - ty)**2)**0.5
            
            if dist < best_dist:
                best_dist = dist
                best = target
        
        return best
    
    def move_towards_target(self, enemy, target):
        """
        Mueve enemigo hacia objetivo.
        Returns: True si se movió, False si no pudo.
        """
        if getattr(enemy, 'has_moved', False):
            return False
        
        # Encontrar tiles
        enemy_tile = self.grid.get_unit_tile(enemy)
        target_tile = self.grid.get_unit_tile(target)
        
        if not enemy_tile or not target_tile:
            return False
        
        # Buscar casillas adyacentes válidas
        neighbors = enemy_tile.get_neighbors(self.grid.grid)
        valid = [n for n in neighbors if n.owner == "enemy" and n.is_empty()]
        
        if not valid:
            return False
        
        # Calcular distancia de cada vecino al objetivo
        scored = []
        for n in valid:
            dist = ((n.x - target_tile.x)**2 + (n.y - target_tile.y)**2)**0.5
            scored.append((n, dist))
        
        # Ordenar por distancia
        scored.sort(key=lambda x: x[1])
        
        # 70% probabilidad de elegir el mejor, 30% el segundo
        if len(scored) >= 2 and random.random() < 0.3:
            best = scored[1][0]
        else:
            best = scored[0][0]
        
        # Ejecutar movimiento
        enemy_tile.unit = None
        best.unit = enemy
        enemy.move_to(best.x, best.y)
        enemy.has_moved = True
        
        return True
    
    def execute_attack(self, enemy, target):
        """Ejecuta ataque enemigo."""
        from entities import TracerProjectile
        from config.constants import COLOR_PROJECTILE_ENEMY
        
        damage = getattr(enemy, 'attack', 10)
        
        # Si es héroe enemigo con AP, usar ataque potenciado
        is_hero_enemy = getattr(enemy, 'is_hero', False) and hasattr(enemy, 'action_points')
        if is_hero_enemy and enemy.action_points.current >= 2:
            enemy.action_points.spend(2)
            damage = int(damage * 1.5)
            print(f"[ENEMY HERO] {enemy.name} usa ataque potenciado! (AP restantes: {enemy.action_points.current})")
        
        # Si el objetivo se defiende, reducir daño
        if getattr(target, 'is_defending', False):
            damage = int(damage * 0.5)
        
        actual = target.take_damage(damage)
        
        target_name = getattr(target, 'name', getattr(target, 'unit_type', 'Unidad'))
        enemy_name = getattr(enemy, 'name', enemy.unit_type)
        print(f"[ENEMY] {enemy_name} ataca a {target_name} por {actual} daño!")
        
        # Efectos visuales
        tx = getattr(target, 'visual_x', 0)
        ty = getattr(target, 'visual_y', 0)
        self.particles.spawn_attack(tx, ty, "enemy")
        
        # Proyectil enemigo
        ex = getattr(enemy, 'visual_x', 0)
        ey = getattr(enemy, 'visual_y', 0)
        proj = TracerProjectile(ex, ey, target, actual,
                               COLOR_PROJECTILE_ENEMY, "enemy", self.particles)
        self.projectiles.append(proj)
        
        return actual
    
    def is_in_attack_range(self, enemy, target):
        """Verifica si el objetivo está en rango de ataque."""
        ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
        tx, ty = getattr(target, 'visual_x', 0), getattr(target, 'visual_y', 0)
        dist = ((ex - tx)**2 + (ey - ty)**2)**0.5
        attack_range = getattr(enemy, 'range', 1) * 100
        return dist <= attack_range, dist, attack_range
    
    def process_turn(self, enemy):
        """
        Procesa el turno completo de un enemigo.
        Returns: True si realizó alguna acción, False si no.
        """
        if not enemy or not hasattr(enemy, 'is_alive') or not enemy.is_alive():
            return False
        
        enemy_name = getattr(enemy, 'name', enemy.unit_type)
        print(f"\n[ENEMY TURN] === {enemy_name} ===")
        
        # Encontrar objetivos
        targets = self.units.get_alive_player_units()
        print(f"[ENEMY] Objetivos vivos: {len(targets)}")
        
        if not targets:
            print("[ENEMY] No hay objetivos!")
            return False
        
        # Seleccionar objetivo
        target = self.select_target(enemy, targets)
        if not target:
            print("[ENEMY] No encontró objetivo!")
            return False
        
        target_name = getattr(target, 'name', target.unit_type)
        print(f"[ENEMY] Objetivo seleccionado: {target_name}")
        
        # Verificar rango
        in_range, dist, attack_range = self.is_in_attack_range(enemy, target)
        print(f"[ENEMY] Pos enemigo: ({getattr(enemy, 'visual_x', 0):.0f}, {getattr(enemy, 'visual_y', 0):.0f})")
        print(f"[ENEMY] Pos objetivo: ({getattr(target, 'visual_x', 0):.0f}, {getattr(target, 'visual_y', 0):.0f})")
        print(f"[ENEMY] Distancia: {dist:.1f}px | Rango: {attack_range}px")
        
        ataco = False
        
        # Si está a rango, ATACAR
        if in_range:
            print(f"[ENEMY] >>> ATACANDO <<<")
            self.execute_attack(enemy, target)
            ataco = True
        else:
            print(f"[ENEMY] Fuera de rango ({dist:.0f} > {attack_range})")
        
        # MOVERSE si no se ha movido
        if not getattr(enemy, 'has_moved', False):
            print(f"[ENEMY] Intentando moverse...")
            moved = self.move_towards_target(enemy, target)
            print(f"[ENEMY] ¿Se movió? {moved}")
            
            # Verificar si tras moverse quedó a rango
            if moved and not ataco:
                in_range_new, dist_new, _ = self.is_in_attack_range(enemy, target)
                print(f"[ENEMY] Nueva distancia: {dist_new:.1f}")
                
                if in_range_new:
                    print(f"[ENEMY] >>> ATACANDO TRAS MOVERSE <<<")
                    self.execute_attack(enemy, target)
                else:
                    print(f"[ENEMY] Aún fuera de rango")
        else:
            print(f"[ENEMY] Ya se había movido")
        
        print(f"[ENEMY] === Fin turno {enemy_name} ===\n")
        return True
    
    def execute_simple_ai(self, dt):
        """Ejecuta IA simple para todos los enemigos (modo antiguo)."""
        from config.constants import AI_MOVE_DELAY
        
        self.ai_timer = getattr(self, 'ai_timer', 0) + dt
        if self.ai_timer < AI_MOVE_DELAY:
            return False
        
        for unit in self.units.enemy_units:
            if not unit.is_alive() or unit.has_moved:
                continue
            
            neighbors = self.grid.get_empty_tiles_in_zone("enemy")
            if neighbors:
                best = max(neighbors, key=lambda m: -abs(m.y - ZONE_PLAYER_Y))
                unit_tile = self.grid.get_unit_tile(unit)
                if unit_tile:
                    unit_tile.unit = None
                best.unit = unit
                unit.move_to(best.x, best.y)
                unit.has_moved = True
        
        return all(u.has_moved or not u.is_alive() for u in self.units.enemy_units)
    
    def reset_projectiles(self):
        """Limpia la lista de proyectiles."""
        self.projectiles.clear()
    
    def update_projectiles(self, dt):
        """Actualiza los proyectiles en vuelo."""
        all_done = True
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.active:
                self.projectiles.remove(proj)
            else:
                all_done = False
        return all_done
