"""
Juego principal - Core (Limpiado)
"""
import pygame
import math
from config.constants import *
from config.settings import *
from systems import GrassSystem, HoneycombTile, Particle, ParticleSystem
from systems.alternating_turn_system import AlternatingTurnSystem, AlternatingPhase
from entities import Hero, HeroPowers
from entities import UltraUnit, UltraTower, TracerProjectile
from ui import OracleOfKimi, PersistentMenu


class TacticalDefenseGame:
    """Juego principal"""
    
    def __init__(self):
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Táctico - Day R Combat")
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.SysFont("arial", 52, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 28)
        self.font_small = pygame.font.SysFont("arial", 22)
        
        self.grass = GrassSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = ParticleSystem()
        self.oracle = OracleOfKimi()
        
        # Sistema de turnos alternados
        self.alt_turn_system = AlternatingTurnSystem()
        self.alt_turn_system.on_unit_activate = self._on_alt_unit_activate
        self.alt_turn_system.on_phase_change = self._on_alt_phase_change
        
        # Menú persistente estilizado
        self.persistent_menu = PersistentMenu(x=20, y=110, width=150)
        
        # Héroe del jugador (único con AP)
        self.hero = None
        
        # Animación de ataque activa
        self.attack_animation = None
        
        # Botón reiniciar
        self.btn_restart = None
        
        self.reset_game()
    

    
    def reset_game(self):
        self.turn_number = 1
        self.phase = PHASE_PLAYER_TURN
        self.combat_timer = 0
        self.selected_tile = None
        
        self.player_units = []
        self.enemy_units = []
        self.player_towers = []
        self.enemy_towers = []
        self.projectiles = []
        
        self.grid = {}
        self._create_grid()
        self._setup_units()
        
        self.oracle.clear_recommendation(self.grid)
        self._update_buttons()
        
        # NUEVO: Iniciar sistema de turnos alternados
        # Separar héroe de tropas
        troops = [u for u in self.player_units if not getattr(u, 'is_hero', False)]
        self.alt_turn_system.setup(self.hero, troops, self.enemy_units)
    
    def _create_grid(self):
        total_width = GRID_COLS * HEX_WIDTH * 0.75
        start_x = (SCREEN_WIDTH - total_width) // 2 + HEX_RADIUS
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = start_x + col * HEX_WIDTH * 0.75
                y = ZONE_PLAYER_Y + row * HEX_HEIGHT
                if col % 2 == 1:
                    y += HEX_HEIGHT // 2
                
                tile = HoneycombTile(col, row, int(x), int(y), "player", False)
                self.grid[(col, row)] = tile
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = start_x + col * HEX_WIDTH * 0.75
                y = ZONE_ENEMY_Y + (GRID_ROWS - 1 - row) * HEX_HEIGHT
                if col % 2 == 1:
                    y += HEX_HEIGHT // 2
                
                tile = HoneycombTile(col, -(row + 1), int(x), int(y), "enemy", False)
                self.grid[(col, -(row + 1))] = tile
        
        self.neutral_zone_y = (ZONE_ENEMY_Y + ZONE_PLAYER_Y) // 2
    
    def _setup_units(self):
        # NUEVO: Crear HÉROE principal (con AP) en posición central
        self.hero = Hero(name="Comandante")
        hero_tile = self.grid.get((4, 3))
        if hero_tile:
            hero_tile.unit = self.hero
            self.hero.set_position(hero_tile.x, hero_tile.y)
            self.player_units.append(self.hero)
        
        # TROPAS normales (sin AP)
        configs = [("berserker", 1, 2), ("assault", 3, 3), ("ranger", 5, 2), 
                  ("sniper", 6, 4), ("assault", 2, 4)]
        
        for unit_type, col, row in configs:
            # No colocar tropa donde está el héroe
            if (col, row) == (4, 3):
                continue
            unit = UltraUnit(unit_type, "player")
            tile = self.grid.get((col, row))
            if tile:
                tile.unit = unit
                unit.set_position(tile.x, tile.y)
                self.player_units.append(unit)
        
        for col, row in [(2, 0), (5, 0)]:
            tile = self.grid.get((col, row))
            if tile:
                tower = UltraTower("player")
                tower.set_position(tile.x, tile.y)
                tile.tower = tower
                self.player_towers.append(tower)
        
        # Crear HÉROE ENEMIGO (con AP)
        from systems.combat_dayr import ActionPointsSystem
        self.enemy_hero = UltraUnit("berserker", "enemy")  # Placeholder, idealmente sería clase Hero
        self.enemy_hero.name = "Señor Oscuro"
        self.enemy_hero.max_health = 120
        self.enemy_hero.health = 120
        self.enemy_hero.attack = 35
        self.enemy_hero.is_hero = True
        # Darle sistema de AP con solo 2 puntos
        self.enemy_hero.action_points = ActionPointsSystem(max_ap=2, recovery_per_turn=2)
        self.enemy_hero.action_points.reset()
        
        enemy_hero_tile = self.grid.get((4, -3))
        if enemy_hero_tile:
            enemy_hero_tile.unit = self.enemy_hero
            self.enemy_hero.set_position(enemy_hero_tile.x, enemy_hero_tile.y)
            self.enemy_units.append(self.enemy_hero)
        
        # Tropas enemigas normales
        enemy_configs = [("berserker", 2, -3), ("assault", 3, -3), ("ranger", 5, -3),
                        ("sniper", 3, -4), ("assault", 5, -4)]
        
        for unit_type, col, row in enemy_configs:
            if (col, row) == (4, -3):  # Skip donde está el héroe
                continue
            unit = UltraUnit(unit_type, "enemy")
            tile = self.grid.get((col, row))
            if tile:
                tile.unit = unit
                unit.set_position(tile.x, tile.y)
                self.enemy_units.append(unit)
        
        for col, row in [(3, -1), (4, -1)]:
            tile = self.grid.get((col, row))
            if tile:
                tower = UltraTower("enemy")
                tower.set_position(tile.x, tile.y)
                tile.tower = tower
                self.enemy_towers.append(tower)
    
    def find_tile(self, pos):
        for tile in self.grid.values():
            dx = pos[0] - tile.x
            dy = pos[1] - tile.y
            if (dx**2 + dy**2)**0.5 <= HEX_RADIUS * 0.9:
                return tile
        return None
    
    def get_unit_tile(self, unit):
        for tile in self.grid.values():
            if getattr(tile, 'unit', None) == unit:
                return tile
        return None
    
    def get_tower_tile(self, tower):
        for tile in self.grid.values():
            if getattr(tile, 'tower', None) == tower:
                return tile
        return None
    
    def update_valid_moves(self):
        for tile in self.grid.values():
            tile.valid_move = False
        
        if not self.selected_tile:
            return
        
        unit = self.selected_tile.unit
        if not unit or unit.has_moved:
            return
        
        neighbors = self.selected_tile.get_neighbors(self.grid)
        for neighbor in neighbors:
            if neighbor.is_empty():
                neighbor.valid_move = True
    
    def _update_buttons(self):
        pass
    
    def handle_input(self):
        import pygame
        mouse_pos = pygame.mouse.get_pos()
        dt = self.clock.tick(FPS) / 1000.0
        
        # Actualizar menú persistente
        self.persistent_menu.update(mouse_pos, dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.selected_tile:
                    self.selected_tile.selected = False
                    self.selected_tile = None
                    self.update_valid_moves()
                if event.key == pygame.K_SPACE and self.phase == PHASE_PLAYER_TURN:
                    self._end_player_turn()
                if event.key == pygame.K_r and self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
                    self.reset_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Presionar botones del menú (visual)
                self.persistent_menu.handle_click(mouse_pos, pressed=True)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Soltar botón - ejecutar acción si se hizo click en un botón
                action = self.persistent_menu.handle_click(mouse_pos, pressed=False)
                if not action:
                    self._handle_click(mouse_pos)
        
        return True
    
    def _handle_click(self, mouse_pos):
        import pygame
        
        # NUEVO: Usar sistema de turnos alternados
        alt = self.alt_turn_system
        
        # Solo procesar clicks en turno del jugador
        if not alt.is_player_turn():
            return
        
        tile = self.find_tile(mouse_pos)
        if not tile:
            return
        
        # Obtener unidad activa del sistema alternado
        active_unit = alt.active_unit
        
        if not self.selected_tile:
            # Seleccionar solo si es la unidad activa
            if tile.unit and tile.unit == active_unit:
                self.selected_tile = tile
                tile.selected = True
                self.update_valid_moves()
                
                # Mostrar menú según tipo
                if alt.is_hero_turn():
                    self._show_hero_menu(tile.unit)
                else:
                    self._show_action_menu(tile.unit)
                
                self.oracle.analyze_battlefield(
                    tile.unit, tile, self.grid,
                    self.player_units, self.enemy_units
                )
            return
        
        current = self.selected_tile
        
        # Mover (gratis para héroe y tropas)
        if tile.valid_move and tile.is_empty():
            self._execute_move_free(current, tile)
            return
        
        # Atacar enemigo
        if tile.unit and tile.unit.owner == "enemy":
            if alt.is_hero_turn():
                self._execute_hero_attack(current.unit, tile.unit)
            else:
                self._execute_troop_attack(current.unit, tile.unit)
            return
        
        if current == tile:
            current.selected = False
            self.selected_tile = None
            self.persistent_menu.clear()
            self.oracle.clear_recommendation(self.grid)
            self.update_valid_moves()
            return
        
        # Cambiar selección si es la unidad activa
        if tile.unit and tile.unit == active_unit:
            current.selected = False
            self.selected_tile = tile
            tile.selected = True
            self.update_valid_moves()
            if alt.is_hero_turn():
                self._show_hero_menu(tile.unit)
            else:
                self._show_action_menu(tile.unit)
            return
        
        current.selected = False
        self.selected_tile = None
        self.persistent_menu.clear()
        self.oracle.clear_recommendation(self.grid)
        self.update_valid_moves()
    
    def _execute_move_action(self, from_tile, to_tile):
        """NUEVO: Ejecuta acción de movimiento usando sistema Day R."""
        unit = from_tile.unit
        if not unit:
            return
        
        # Ejecutar movimiento directamente (simplificado)
        self.particles.spawn_dust(from_tile.x, from_tile.y)
        from_tile.unit = None
        to_tile.unit = unit
        self.particles.spawn_dust(to_tile.x, to_tile.y)
        unit.move_to(to_tile.x, to_tile.y)
    
    def _execute_attack_action(self, attacker, target):
        """Ejecuta ataque básico (simplificado)."""
        damage = getattr(attacker, 'attack', 10)
        actual = target.take_damage(damage)
        
        # Efectos visuales
        tx = getattr(target, 'visual_x', 0)
        ty = getattr(target, 'visual_y', 0)
        self.particles.spawn_attack(tx, ty, "player")
        
        # Proyectil
        from entities import TracerProjectile
        ax = getattr(attacker, 'visual_x', 0)
        ay = getattr(attacker, 'visual_y', 0)
        proj = TracerProjectile(ax, ay, target, actual, 
                               COLOR_PROJECTILE_PLAYER, "player", self.particles)
        self.projectiles.append(proj)
    
    def _show_action_menu(self, unit):
        """Muestra menú persistente para tropas normales."""
        self.persistent_menu.clear()
        self.persistent_menu.title = "TROPA"
        
        # Verificar si hay enemigos a rango
        can_attack = self._can_unit_attack_anyone(unit)
        has_moved = getattr(unit, 'has_moved', False)
        
        if has_moved:
            # Ya se movió, solo puede atacar si hay objetivos o pasar
            if can_attack:
                self.persistent_menu.add_button("Atacar", None)
                self.persistent_menu.add_button("Terminar", lambda: self._end_player_turn())
            else:
                # No puede hacer nada más
                self.persistent_menu.add_button("Pasar Turno", lambda: self._end_player_turn())
        else:
            # Puede moverse y/o atacar
            self.persistent_menu.add_button("Mover", None)
            if can_attack:
                self.persistent_menu.add_button("Atacar", None)
            self.persistent_menu.add_button("Terminar", lambda: self._end_player_turn())
    
    def _can_unit_attack_anyone(self, unit):
        """Verifica si la unidad tiene algún enemigo a rango."""
        attack_range = getattr(unit, 'range', 1) * 100  # Mismo rango que enemigos
        ux, uy = getattr(unit, 'visual_x', 0), getattr(unit, 'visual_y', 0)
        
        enemies = [u for u in self.enemy_units if u.is_alive()]
        for enemy in enemies:
            ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
            dist = ((ux - ex)**2 + (uy - ey)**2)**0.5
            if dist <= attack_range:
                return True
        return False
    
    def _execute_action(self, action_name):
        """Ejecuta la acción seleccionada INMEDIATAMENTE."""
        if not self.selected_tile:
            return
        
        unit = self.selected_tile.unit
        if not unit:
            return
        
        if action_name == "Mover":
            # El movimiento ya funciona con los tiles válidos
            return
        
        # Buscar objetivo para los ataques
        target = self._find_nearest_enemy(unit)
        if not target:
            return
        
        # Ejecutar ataque basado en la acción
        if action_name in ["Carga", "Furia", "Suprimir", "Refuerzo", "Disparo Área", "Trampa", "Disparo Largo", "Marca"]:
            # Ejecutar ataque especial inmediatamente
            self._execute_special_attack(unit, target, action_name)
            unit.has_moved = True  # Usar su acción del turno
            self.selected_tile.selected = False
            self.selected_tile = None
            self.action_menu_visible = False
            self.oracle.clear_recommendation(self.grid)
            self.update_valid_moves()
    
    def _find_nearest_enemy(self, unit):
        """Encuentra el enemigo más cercano a la unidad."""
        best = None
        best_dist = float('inf')
        
        unit_x = getattr(unit, 'visual_x', 0)
        unit_y = getattr(unit, 'visual_y', 0)
        
        for enemy in self.enemy_units:
            if not enemy.is_alive():
                continue
            ex = getattr(enemy, 'visual_x', 0)
            ey = getattr(enemy, 'visual_y', 0)
            dist = ((unit_x - ex)**2 + (unit_y - ey)**2)**0.5
            if dist < best_dist:
                best_dist = dist
                best = enemy
        return best
    
    def _execute_special_attack(self, unit, target, attack_name):
        """Ejecuta un ataque especial inmediatamente."""
        import random
        
        # Calcular daño según el ataque
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
        from entities import TracerProjectile
        proj = TracerProjectile(ux, uy, target, damage, (255, 200, 100), unit.owner, self.particles)
        self.projectiles.append(proj)
    
    def _move_unit(self, from_tile, to_tile):
        unit = from_tile.unit
        to_tile.unit = unit
        from_tile.unit = None
        unit.move_to(to_tile.x, to_tile.y)
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        
        for tile in self.grid.values():
            tile.update(mouse_pos)
        
        # Actualizar sistema de turnos alternados
        self._update_alt_turn_system(dt)
        self.alt_turn_system.update(dt)
        
        # Actualizar animación de ataque
        self._update_attack_animation(dt)
        
        self.grass.update(dt)
    
    # NUEVO: Callbacks del sistema de combate
    def _on_turn_start(self, unit, faction):
        """Callback cuando inicia un turno."""
        unit_name = getattr(unit, 'name', getattr(unit, 'unit_type', 'Unidad'))
        print(f"[COMBATE] Turno de {unit_name} ({faction})")
        
        # Resetear selección
        if self.selected_tile:
            self.selected_tile.selected = False
            self.selected_tile = None
        self.update_valid_moves()
        
        # Si es unidad del jugador, seleccionarla automáticamente
        if faction == "player":
            tile = self.get_unit_tile(unit)
            if tile:
                self.selected_tile = tile
                tile.selected = True
                self._show_action_menu(unit)
    
    def _on_action_executed(self, action, result):
        """Callback cuando se ejecuta una acción."""
        if result.message:
            print(f"[COMBATE] {result.message}")
        
        # Efectos visuales
        if hasattr(action, 'target') and action.target:
            tx = getattr(action.target, 'visual_x', 0)
            ty = getattr(action.target, 'visual_y', 0)
            self.particles.spawn_attack(tx, ty, "player" if action.performer in self.player_units else "enemy")
    
    def _on_combat_end(self, winner):
        """Callback cuando termina el combate."""
        print(f"[COMBATE] Fin del combate. Ganador: {winner}")
        if winner == "player":
            self.phase = PHASE_VICTORY
        else:
            self.phase = PHASE_DEFEAT
        self._update_buttons()
    
    def _on_unit_died(self, unit):
        """Callback cuando una unidad muere."""
        unit_name = getattr(unit, 'name', getattr(unit, 'unit_type', 'Unidad'))
        print(f"[COMBATE] {unit_name} ha caído")
        
        # Limpiar del grid
        for tile in self.grid.values():
            if getattr(tile, 'unit', None) == unit:
                tile.unit = None
            if getattr(tile, 'tower', None) == unit:
                tile.tower = None
    
    # === NUEVO: Sistema de Turnos Alternados ===
    
    def _update_alt_turn_system(self, dt):
        """Actualiza el sistema de turnos alternados."""
        alt = self.alt_turn_system
        
        # Actualizar fase visual
        if alt.phase == AlternatingPhase.PLAYER_HERO:
            self.phase = PHASE_PLAYER_TURN
        elif alt.phase == AlternatingPhase.PLAYER_TROOP:
            self.phase = PHASE_PLAYER_TURN
        elif alt.phase == AlternatingPhase.ENEMY:
            self.phase = PHASE_ENEMY_TURN
        elif alt.phase == AlternatingPhase.ENDED:
            pass
        
        # Actualizar unidad activa
        active = alt.active_unit
        if active and hasattr(active, 'update'):
            import inspect
            try:
                sig = inspect.signature(active.update)
                params = list(sig.parameters.keys())
                if len(params) >= 3:
                    active.update(dt, self.grass)
                else:
                    active.update(dt)
            except Exception:
                pass
        
        # Procesar turno enemigo
        if alt.is_enemy_turn() and active:
            self._process_enemy_turn_alt(dt)
    
    def _on_alt_unit_activate(self, unit, unit_type):
        """Callback cuando se activa una unidad en el sistema alternado."""
        unit_name = getattr(unit, 'name', getattr(unit, 'unit_type', 'Unidad'))
        print(f"[ALT-TURN] Activado: {unit_name} ({unit_type})")
        
        # Limpiar selección anterior
        if self.selected_tile:
            self.selected_tile.selected = False
            self.selected_tile = None
        
        # Seleccionar automáticamente la unidad activa
        tile = self.get_unit_tile(unit)
        if tile and unit_type in ['hero', 'player_troop']:
            self.selected_tile = tile
            tile.selected = True
            if unit_type == 'hero':
                self._show_hero_menu(unit)
            else:
                self._show_action_menu(unit)
        
        self.update_valid_moves()
    
    def _on_alt_phase_change(self, phase, winner):
        """Callback cuando cambia la fase del combate."""
        if phase == AlternatingPhase.ENDED:
            if winner == "player":
                self.phase = PHASE_VICTORY
            else:
                self.phase = PHASE_DEFEAT
            self._update_buttons()
    
    def _process_enemy_turn_alt(self, dt):
        """Procesa turno enemigo - puede moverse Y atacar si queda a rango."""
        if self.alt_turn_system.enemy_action_taken:
            return
        
        enemy = self.alt_turn_system.active_unit
        if not enemy or not hasattr(enemy, 'is_alive') or not enemy.is_alive():
            print(f"[ENEMY ERROR] Enemigo inválido o muerto")
            self.alt_turn_system.enemy_finished_action()
            return
        
        enemy_name = getattr(enemy, 'name', enemy.unit_type)
        print(f"\n[ENEMY TURN] === {enemy_name} ===")
        
        # Encontrar objetivos
        targets = [u for u in self.player_units if u.is_alive()]
        print(f"[ENEMY] Objetivos vivos: {len(targets)}")
        if not targets:
            print("[ENEMY] No hay objetivos!")
            self.alt_turn_system.enemy_finished_action()
            return
        
        # Seleccionar objetivo
        target = self._select_enemy_target(enemy, targets)
        if not target:
            print("[ENEMY] No encontró objetivo!")
            self.alt_turn_system.enemy_finished_action()
            return
        
        target_name = getattr(target, 'name', target.unit_type)
        print(f"[ENEMY] Objetivo seleccionado: {target_name}")
        
        # Calcular distancia
        ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
        tx, ty = getattr(target, 'visual_x', 0), getattr(target, 'visual_y', 0)
        dist = ((ex - tx)**2 + (ey - ty)**2)**0.5
        attack_range = getattr(enemy, 'range', 1) * 100  # Aumentado a 100 por rango
        
        print(f"[ENEMY] Pos enemigo: ({ex:.0f}, {ey:.0f})")
        print(f"[ENEMY] Pos objetivo: ({tx:.0f}, {ty:.0f})")
        print(f"[ENEMY] Distancia: {dist:.1f}px | Rango: {attack_range}px")
        
        ataco = False
        
        # Si está a rango, ATACAR
        if dist <= attack_range:
            print(f"[ENEMY] >>> ATACANDO <<<")
            self._execute_enemy_attack(enemy, target)
            ataco = True
        else:
            print(f"[ENEMY] Fuera de rango ({dist:.0f} > {attack_range})")
        
        # MOVERSE si no se ha movido
        if not getattr(enemy, 'has_moved', False):
            print(f"[ENEMY] Intentando moverse...")
            moved = self._move_enemy_towards(enemy, target)
            print(f"[ENEMY] ¿Se movió? {moved}")
            
            # Verificar si tras moverse quedó a rango
            if moved and not ataco:
                ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
                dist_nueva = ((ex - tx)**2 + (ey - ty)**2)**0.5
                print(f"[ENEMY] Nueva distancia: {dist_nueva:.1f}")
                
                if dist_nueva <= attack_range:
                    print(f"[ENEMY] >>> ATACANDO TRAS MOVERSE <<<")
                    self._execute_enemy_attack(enemy, target)
                else:
                    print(f"[ENEMY] Aún fuera de rango")
        else:
            print(f"[ENEMY] Ya se había movido")
        
        print(f"[ENEMY] === Fin turno {enemy_name} ===\n")
        self.alt_turn_system.enemy_finished_action()
    
    def _select_enemy_target(self, enemy, targets):
        """IA: Selecciona el mejor objetivo para el enemigo."""
        ex, ey = getattr(enemy, 'visual_x', 0), getattr(enemy, 'visual_y', 0)
        
        candidates = []
        for target in targets:
            tx, ty = getattr(target, 'visual_x', 0), getattr(target, 'visual_y', 0)
            dist = ((ex - tx)**2 + (ey - ty)**2)**0.5
            
            # Puntuación basada en múltiples factores
            score = 0
            
            # Preferir objetivos más débiles (menos HP)
            hp_ratio = getattr(target, 'health', 100) / getattr(target, 'max_health', 100)
            score += (1 - hp_ratio) * 50  # Hasta 50 puntos por estar débil
            
            # Preferir objetivos más cercanos
            score -= dist * 0.5  # Penalizar distancia
            
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
    
    def _execute_enemy_attack(self, enemy, target):
        """Ejecuta ataque enemigo (con posible uso de AP para héroes)."""
        damage = getattr(enemy, 'attack', 10)
        
        # Si es héroe enemigo con AP, usar AP para ataque potenciado
        is_hero_enemy = getattr(enemy, 'is_hero', False) and hasattr(enemy, 'action_points')
        if is_hero_enemy and enemy.action_points.current >= 2:
            # Usar 2 AP para ataque potenciado x1.5
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
        from entities import TracerProjectile
        ex = getattr(enemy, 'visual_x', 0)
        ey = getattr(enemy, 'visual_y', 0)
        proj = TracerProjectile(ex, ey, target, actual,
                               COLOR_PROJECTILE_ENEMY, "enemy", self.particles)
        self.projectiles.append(proj)
    
    def _find_alternative_target(self, enemy, targets, excluded_target):
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
    
    def _move_enemy_towards(self, enemy, target):
        """
        Mueve enemigo hacia objetivo.
        Returns: True si se movió, False si no pudo.
        """
        # Verificar que no se haya movido ya
        if getattr(enemy, 'has_moved', False):
            return False
        
        # Encontrar tiles
        enemy_tile = None
        target_tile = None
        
        for tile in self.grid.values():
            if getattr(tile, 'unit', None) == enemy:
                enemy_tile = tile
            if getattr(tile, 'unit', None) == target:
                target_tile = tile
        
        if not enemy_tile or not target_tile:
            return False
        
        # Buscar casillas adyacentes válidas
        neighbors = enemy_tile.get_neighbors(self.grid)
        valid = [n for n in neighbors if n.owner == "enemy" and n.is_empty()]
        
        if not valid:
            return False
        
        # Estrategia: moverse hacia el objetivo
        # Pero también considerar aleatoriedad para no predecir
        import random
        
        # Calcular distancia de cada vecino al objetivo
        scored = []
        for n in valid:
            dist = ((n.x - target_tile.x)**2 + (n.y - target_tile.y)**2)**0.5
            scored.append((n, dist))
        
        # Ordenar por distancia
        scored.sort(key=lambda x: x[1])
        
        # 70% de probabilidad de elegir el mejor movimiento
        # 30% de elegir el segundo mejor (para variabilidad)
        if len(scored) >= 2 and random.random() < 0.3:
            best = scored[1][0]  # Segundo mejor
        else:
            best = scored[0][0]  # Mejor
        
        # Ejecutar movimiento
        enemy_tile.unit = None
        best.unit = enemy
        enemy.move_to(best.x, best.y)
        enemy.has_moved = True  # Marcar como movido
        
        return True
    
    def _execute_ai(self, dt):
        import pygame
        self.ai_timer = getattr(self, 'ai_timer', 0) + dt
        
        if self.ai_timer < AI_MOVE_DELAY:
            return
        
        for unit in self.enemy_units:
            if not unit.is_alive() or unit.has_moved:
                continue
            
            neighbors = []
            for tile in self.grid.values():
                if tile.owner == "enemy" and tile.is_empty():
                    neighbors.append(tile)
            
            if neighbors:
                best = max(neighbors, key=lambda m: -abs(m.y - ZONE_PLAYER_Y))
                unit_tile = self.get_unit_tile(unit)
                if unit_tile:
                    unit_tile.unit = None
                best.unit = unit
                unit.move_to(best.x, best.y)
                unit.has_moved = True
        
        if all(u.has_moved or not u.is_alive() for u in self.enemy_units):
            self._start_combat()
    
    def _start_combat(self):
        self.phase = PHASE_COMBAT
        self.combat_attacks_done = False  # Bandera: ¿ya se lanzaron todos los ataques?
        
        for unit in self.player_units + self.enemy_units:
            unit.has_moved = False
            unit.attack_cooldown = 0
            unit.has_attacked = False  # Cada unidad solo ataca una vez
        
        for tower in self.player_towers + self.enemy_towers:
            tower.has_attacked = False
        
        # Lanzar todos los ataques de una sola vez
        self._process_attacks_once()
        self.combat_attacks_done = True
    
    def _update_combat(self, dt):
        import pygame
        
        self.grass.update(dt)
        self.particles.update(dt)
        
        for unit in self.player_units + self.enemy_units:
            unit.update(dt, self.grass)
        
        for tower in self.player_towers + self.enemy_towers:
            tower.update(dt)
        
        # Actualizar proyectiles en vuelo
        all_done = True
        for proj in self.projectiles[:]:
            proj.update(dt)
            if not proj.active:
                self.projectiles.remove(proj)
            else:
                all_done = False
        
        # Cuando todos los proyectiles llegaron, terminar combate
        if self.combat_attacks_done and not self.projectiles:
            self._end_combat()
        
        self._check_victory()
    
    def _process_attacks_once(self):
        """Cada unidad/torre lanza exactamente un ataque si hay objetivo en rango."""
        for attacker in self.player_units + self.player_towers:
            if not attacker.is_alive():
                continue
            if getattr(attacker, 'has_attacked', False):
                continue
            
            target = self._find_target(attacker, self.enemy_units + self.enemy_towers)
            if target and self._in_range(attacker, target):
                ax = getattr(attacker, 'visual_x', getattr(attacker, 'x', 0))
                ay = getattr(attacker, 'visual_y', getattr(attacker, 'y', 0))
                
                proj = TracerProjectile(ax, ay, target, attacker.attack,
                                       COLOR_PROJECTILE_PLAYER, "player", self.particles)
                self.projectiles.append(proj)
                attacker.has_attacked = True
        
        for attacker in self.enemy_units + self.enemy_towers:
            if not attacker.is_alive():
                continue
            if getattr(attacker, 'has_attacked', False):
                continue
            
            target = self._find_target(attacker, self.player_units + self.player_towers)
            if target and self._in_range(attacker, target):
                ax = getattr(attacker, 'visual_x', getattr(attacker, 'x', 0))
                ay = getattr(attacker, 'visual_y', getattr(attacker, 'y', 0))
                
                proj = TracerProjectile(ax, ay, target, attacker.attack,
                                       COLOR_PROJECTILE_ENEMY, "enemy", self.particles)
                self.projectiles.append(proj)
                attacker.has_attacked = True
    
    def _find_target(self, attacker, targets):
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
        ax = getattr(attacker, 'visual_x', None) if hasattr(attacker, 'visual_x') else getattr(attacker, 'x', 0)
        ay = getattr(attacker, 'visual_y', None) if hasattr(attacker, 'visual_y') else getattr(attacker, 'y', 0)
        tx = getattr(target, 'visual_x', None) if hasattr(target, 'visual_x') else getattr(target, 'x', 0)
        ty = getattr(target, 'visual_y', None) if hasattr(target, 'visual_y') else getattr(target, 'y', 0)
        return ((ax-tx)**2 + (ay-ty)**2)**0.5 <= attacker.get_attack_range_pixels()
    
    def _end_combat(self):
        self.turn_number += 1
        self.phase = PHASE_PLAYER_TURN
        self.projectiles.clear()
        self.particles.particles.clear()
        
        for tile in self.grid.values():
            if getattr(tile, 'unit', None) and not tile.unit.is_alive():
                tile.unit = None
            if getattr(tile, 'tower', None) and not tile.tower.is_alive():
                tile.tower = None
        
        self.player_units = [u for u in self.player_units if u.is_alive()]
        self.enemy_units = [u for u in self.enemy_units if u.is_alive()]
        self.player_towers = [t for t in self.player_towers if t.is_alive()]
        self.enemy_towers = [t for t in self.enemy_towers if t.is_alive()]
        
        self._update_buttons()
    
    # NUEVO: Métodos para sistema de combate Day R
    def _execute_action_from_menu(self, action_id):
        """Ejecuta acción desde el menú."""
        if action_id == "move":
            pass
        elif action_id == "end_turn":
            self._end_player_turn()
        elif action_id.startswith("power_"):
            # Poder del héroe
            power_id = action_id.replace("power_", "")
            self._execute_hero_power(power_id)
        elif action_id == "defend":
            # Defender (solo héroe)
            if self.selected_tile and self.alt_turn_system.is_hero_turn():
                hero = self.selected_tile.unit
                if hasattr(hero, 'set_defending'):
                    hero.set_defending(True)
                    print(f"[HEROE] {hero.name} se defiende")
                    # Terminar turno
                    self.selected_tile.selected = False
                    self.selected_tile = None
                    self.persistent_menu.clear()
                    self.alt_turn_system.end_hero_turn()
    
    def _execute_defend_action(self):
        """Ejecuta acción de defender (simplificado)."""
        if not self.selected_tile or not self.selected_tile.unit:
            return
        
        unit = self.selected_tile.unit
        if hasattr(unit, 'set_defending'):
            unit.set_defending(True)
            print(f"[DEFENSA] {getattr(unit, 'name', unit.unit_type)} se defiende")
    
    def _end_player_turn(self):
        """NUEVO: Termina el turno del jugador."""
        if self.selected_tile:
            self.selected_tile.selected = False
            self.selected_tile = None
        self.persistent_menu.clear()
        self.oracle.clear_recommendation(self.grid)
        self.update_valid_moves()
        
        # Usar sistema alternado
        if self.alt_turn_system.is_hero_turn():
            self.alt_turn_system.end_hero_turn()
        elif self.alt_turn_system.is_troop_turn():
            self.alt_turn_system.end_troop_turn()
    
    # === NUEVO: Métodos para sistema de turnos alternados ===
    
    def _execute_move_free(self, from_tile, to_tile):
        """Movimiento gratuito (1 vez por turno)."""
        unit = from_tile.unit
        if not unit:
            return
        
        # Verificar que sea la unidad activa
        if unit != self.alt_turn_system.active_unit:
            return
        
        # Verificar que no se haya movido ya este turno
        if getattr(unit, 'has_moved', False):
            print("[AVISO] Ya te moviste este turno")
            return
        
        # Ejecutar movimiento
        self.particles.spawn_dust(from_tile.x, from_tile.y)
        from_tile.unit = None
        to_tile.unit = unit
        self.particles.spawn_dust(to_tile.x, to_tile.y)
        unit.move_to(to_tile.x, to_tile.y)
        
        # Marcar como movido
        unit.has_moved = True
        
        # Limpiar selección
        from_tile.selected = False
        self.selected_tile = None
        self.persistent_menu.clear()
        self.oracle.clear_recommendation(self.grid)
        self.update_valid_moves()
    
    def _execute_hero_attack(self, hero, target):
        """Héroe ataca usando AP."""
        if not hasattr(hero, 'use_power'):
            return
        
        # Usar poder básico de ataque
        result = hero.use_power('slash', target)
        
        if result['success']:
            # Efectos visuales
            tx = getattr(target, 'visual_x', 0)
            ty = getattr(target, 'visual_y', 0)
            self.particles.spawn_attack(tx, ty, "player")
            
            # Proyectil
            from entities import TracerProjectile
            ax = getattr(hero, 'visual_x', 0)
            ay = getattr(hero, 'visual_y', 0)
            proj = TracerProjectile(ax, ay, target, result.get('damage', 0),
                                   COLOR_PROJECTILE_PLAYER, "player", self.particles)
            self.projectiles.append(proj)
            
            # Si se quedó sin AP, terminar turno automáticamente
            if hero.action_points.is_depleted:
                self.selected_tile.selected = False
                self.selected_tile = None
                self.persistent_menu.clear()
                self.alt_turn_system.end_hero_turn()
        else:
            print(f"[ERROR] {result['message']}")
    
    def _execute_troop_attack(self, troop, target):
        """Tropa ataca (sin AP)."""
        damage = getattr(troop, 'attack', 10)
        actual = target.take_damage(damage)
        
        print(f"[ATAQUE] {troop.unit_type} ataca por {actual}")
        
        # Efectos visuales
        tx = getattr(target, 'visual_x', 0)
        ty = getattr(target, 'visual_y', 0)
        self.particles.spawn_attack(tx, ty, "player")
        
        # Proyectil
        from entities import TracerProjectile
        ax = getattr(troop, 'visual_x', 0)
        ay = getattr(troop, 'visual_y', 0)
        proj = TracerProjectile(ax, ay, target, actual,
                               COLOR_PROJECTILE_PLAYER, "player", self.particles)
        self.projectiles.append(proj)
        
        # Marcar que la tropa actuó (ya no puede hacer más este turno)
        troop.has_moved = True
        
        # Después de atacar, la tropa termina su turno
        self.selected_tile.selected = False
        self.selected_tile = None
        self.persistent_menu.clear()
        self.alt_turn_system.end_troop_turn()
    
    def _show_hero_menu(self, hero):
        """Muestra menú persistente para el héroe con sus poderes."""
        self.persistent_menu.clear()
        self.persistent_menu.title = "HEROE"
        
        # Mover (gratis)
        can_move = not getattr(hero, 'has_moved', False)
        self.persistent_menu.add_button("Mover" if can_move else "Mover ✓", None, enabled=can_move)
        
        # Ataque básico (2 AP)
        can_slash = hero.can_use_power('slash')
        self.persistent_menu.add_button(f"Ataque ({2} AP)", 
                                       lambda: self._execute_hero_power('slash'), 
                                       enabled=can_slash)
        
        # Golpe poderoso (4 AP)
        can_power = hero.can_use_power('power_strike')
        self.persistent_menu.add_button(f"Golpe Fuerte ({4} AP)",
                                       lambda: self._execute_hero_power('power_strike'),
                                       enabled=can_power)
        
        # Curación (3 AP)
        can_heal = hero.can_use_power('heal')
        self.persistent_menu.add_button(f"Curar ({3} AP)",
                                       lambda: self._execute_hero_power('heal'),
                                       enabled=can_heal)
        
        # Terminar
        self.persistent_menu.add_button("Terminar Turno", lambda: self._end_player_turn())
    
    def _execute_hero_power(self, power_id):
        """Ejecuta poder del héroe con animación."""
        if not self.selected_tile or not self.alt_turn_system.is_hero_turn():
            return
        
        hero = self.selected_tile.unit
        if not hero or not hasattr(hero, 'use_power'):
            return
        
        # Encontrar objetivo (más cercano)
        target = self._find_nearest_enemy(hero)
        if not target:
            print("[ERROR] No hay objetivo")
            return
        
        # Iniciar animación de ataque
        self._start_attack_animation(hero, target, power_id)
        
        # Ejecutar daño
        result = hero.use_power(power_id, target)
        
        if result['success']:
            print(f"[HEROE] Usa {power_id} causando {result.get('damage', 0)} daño")
            
            # Si se quedó sin AP, terminar turno después de la animación
            if hero.action_points.is_depleted:
                self.selected_tile.selected = False
                self.selected_tile = None
                self.persistent_menu.clear()
                self.alt_turn_system.end_hero_turn()
        else:
            print(f"[ERROR] {result['message']}")
    
    def _start_attack_animation(self, hero, target, power_id):
        """Inicia animación de ataque del héroe."""
        # Guardar animación activa
        self.attack_animation = {
            'hero': hero,
            'target': target,
            'power': power_id,
            'phase': 'windup',  # windup, strike, recovery
            'timer': 0.0,
            'duration': 0.8,  # Duración total lenta y dramática
        }
    
    def _update_attack_animation(self, dt):
        """Actualiza animación de ataque."""
        if not self.attack_animation:
            return
        
        anim = self.attack_animation
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
                from entities import TracerProjectile
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
                self.attack_animation = None  # Terminar animación
    
    def _check_victory(self):
        if not self.enemy_units and not self.enemy_towers:
            self.phase = PHASE_VICTORY
        elif not self.player_units and not self.player_towers:
            self.phase = PHASE_DEFEAT
        
        if self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
            self._update_buttons()
    
    def draw(self):
        import pygame
        self.screen.fill(COLOR_BG)
        
        self.grass.draw(self.screen)
        
        pygame.draw.rect(self.screen, (30, 40, 35), 
                        (0, ZONE_ENEMY_Y - 30, SCREEN_WIDTH, 
                         ZONE_PLAYER_Y - ZONE_ENEMY_Y + GRID_ROWS * HEX_HEIGHT + 100))
        
        pygame.draw.line(self.screen, COLOR_HONEY_BORDER, 
                        (50, self.neutral_zone_y), (SCREEN_WIDTH-50, self.neutral_zone_y), 4)
        
        self.screen.blit(self.font_medium.render("ZONA ENEMIGA", True, (255, 150, 150)), 
                        (SCREEN_WIDTH//2 - 100, ZONE_ENEMY_Y - 45))
        self.screen.blit(self.font_medium.render("TU ZONA", True, (150, 255, 150)), 
                        (SCREEN_WIDTH//2 - 60, ZONE_PLAYER_Y + GRID_ROWS * HEX_HEIGHT + 25))
        
        tiles = sorted(self.grid.values(), key=lambda t: t.y)
        for tile in tiles:
            tile.draw(self.screen)
        
        
        # Dibujar todas las unidades y torres después de las tiles
        all_units_and_towers = []
        for tile in tiles:
            if tile.unit:
                visual_y = tile.unit.visual_y if tile.unit.is_moving else tile.y
                all_units_and_towers.append((visual_y, tile.unit, tile))
            if tile.tower:
                all_units_and_towers.append((tile.y, tile.tower, tile))
        
        for y_pos, obj, tile in sorted(all_units_and_towers, key=lambda x: x[0]):
            if hasattr(obj, 'is_moving'):
                if obj.is_moving:
                    obj.draw(self.screen, obj.visual_x, obj.visual_y + tile.wall_height//2)
                else:
                    obj.draw(self.screen, tile.x, tile.y + tile.wall_height//2)
            else:
                obj.draw(self.screen, tile.x, tile.y + tile.wall_height//2)
        
        for proj in self.projectiles:
            proj.draw(self.screen)
        self.particles.draw(self.screen)
        
        self._draw_ui()
        
        if self.phase == PHASE_VICTORY:
            self._draw_victory()
        elif self.phase == PHASE_DEFEAT:
            self._draw_defeat()
        
        pygame.display.flip()
    
    def _draw_ui(self):
        import pygame
        
        # === PANEL SUPERIOR (info principal) ===
        panel_top = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        pygame.draw.rect(panel_top, (20, 25, 35, 240), (0, 0, SCREEN_WIDTH, 60))
        self.screen.blit(panel_top, (0, 0))
        
        # Usar sistema alternado para info
        alt = self.alt_turn_system
        phase_name = alt.get_phase_name()
        phase_color = alt.get_phase_color()
        
        # Ronda y estado
        self.screen.blit(self.font_medium.render(f"Ronda {alt.turn_number} - {phase_name}", True, phase_color), (20, 8))
        
        # Info de unidad activa
        active = alt.active_unit
        if active:
            is_hero = getattr(active, 'is_hero', False)
            name = getattr(active, 'name', getattr(active, 'unit_type', 'Unidad'))
            name_color = (255, 215, 0) if is_hero else (100, 255, 100) if alt.is_troop_turn() else (255, 100, 100)
            
            name_text = f"Activa: {name}"
            self.screen.blit(self.font_small.render(name_text, True, name_color), (20, 38))
            
            # AP solo para héroe
            if is_hero and hasattr(active, 'action_points'):
                ap = active.action_points
                ap_color = (100, 255, 100) if ap.current >= 4 else (255, 255, 100) if ap.current >= 2 else (255, 100, 100)
                ap_text = f"AP: {ap.current}/{ap.maximum}"
                self.screen.blit(self.font_medium.render(ap_text, True, ap_color), (300, 8))
        
        # === PANEL DERECHO (stats) ===
        px = SCREEN_WIDTH - 180
        pygame.draw.rect(self.screen, (30, 35, 45), (px, 5, 170, 50))
        alive_p = len([u for u in self.player_units if u.is_alive()])
        alive_e = len([u for u in self.enemy_units if u.is_alive()])
        self.screen.blit(self.font_small.render(f"Aliados: {alive_p}", True, (100, 255, 100)), (px+10, 10))
        self.screen.blit(self.font_small.render(f"Enemigos: {alive_e}", True, (255, 100, 100)), (px+10, 30))
        
        # === MENSAJE DE AYUDA ===
        help_y = 65
        if alt.is_hero_turn():
            msg = "HÉROE: Click=Mover(gratis) | Click enemigo=Ataque básico | Menú=Poderes especiales"
        elif alt.is_troop_turn():
            msg = "TROPA: Click=Mover | Click enemigo=Atacar | ESPACIO=Terminar"
        elif alt.is_enemy_turn():
            msg = "El enemigo está actuando..."
        else:
            msg = ""
        if msg:
            self.screen.blit(self.font_small.render(msg, True, (200, 220, 255)), (20, help_y))
        
        # Oracle y menú (menú se dibuja a la izquierda)
        self.oracle.draw(self.screen, self.font_small)
        # Menú persistente estilizado
        self.persistent_menu.draw(self.screen, self.font_small)
        
        # Info de unidad seleccionada (esquina inferior)
        if self.selected_tile and self.selected_tile.unit:
            self._draw_unit_info(self.selected_tile.unit)
    
    def _draw_unit_info(self, unit):
        import pygame
        x = 20
        y = SCREEN_HEIGHT - 140
        
        # Panel de fondo para la info
        is_hero = getattr(unit, 'is_hero', False)
        panel_h = 140 if is_hero else 110
        pygame.draw.rect(self.screen, (20, 25, 35, 200), (x-10, y-5, 180, panel_h))
        
        # Título con color según tipo
        title_color = (255, 215, 0) if is_hero else (100, 255, 100) if unit.owner == "player" else (255, 100, 100)
        title = f"{'★ ' if is_hero else ''}{unit.unit_type.upper()}"
        self.screen.blit(self.font_small.render(title, True, title_color), (x, y))
        
        # Info básica
        info_lines = [
            f"Salud: {unit.health}/{unit.max_health}",
            f"Ataque: {unit.attack}",
            f"Rango: {unit.range}",
            f"Velocidad: {unit.speed}",
        ]
        
        # Solo mostrar AP si es el héroe
        if is_hero and hasattr(unit, 'action_points'):
            ap = unit.action_points
            info_lines.append(f"AP: {ap.current}/{ap.maximum}")
            # Barra de AP visual
            bar_w = 100
            bar_ratio = ap.current / ap.maximum
            bar_color = (100, 255, 100) if bar_ratio > 0.4 else (255, 255, 100) if bar_ratio > 0.2 else (255, 100, 100)
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y + 110, bar_w, 8))
            pygame.draw.rect(self.screen, bar_color, (x, y + 110, bar_w * bar_ratio, 8))
            pygame.draw.rect(self.screen, (200, 200, 200), (x, y + 110, bar_w, 8), 1)
        
        for i, text in enumerate(info_lines):
            self.screen.blit(self.font_small.render(text, True, (220, 220, 220)), (x, y + 22 + i*20))
    
    def _draw_victory(self):
        import pygame
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 100, 0, 150), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        self.screen.blit(self.font_large.render("¡VICTORIA!", True, (255, 215, 0)), 
                        (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
        
        self.screen.blit(self.font_medium.render("Has derrotado a todos los enemigos", True, (255, 255, 200)), 
                        (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 + 10))
        
        self.btn_restart.draw(self.screen, self.font_small)
    
    def _draw_defeat(self):
        import pygame
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (100, 0, 0, 150), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        
        self.screen.blit(self.font_large.render("DERROTA", True, (255, 100, 100)), 
                        (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
        
        self.screen.blit(self.font_medium.render("Tus fuerzas han caído", True, (255, 200, 200)), 
                        (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 + 30))
        
        self.btn_restart.draw(self.screen, self.font_small)
    
    def run(self):
        import pygame
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_input()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    game = TacticalDefenseGame()
    game.run()
