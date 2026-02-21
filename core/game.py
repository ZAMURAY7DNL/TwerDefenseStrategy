"""
Juego principal - Core
"""
import pygame
# Importar todo lo necesario
from config.constants import *
from config.settings import *
from systems import GrassSystem, HoneycombTile, Particle, ParticleSystem, ActionMenuSystem
from entities import UltraUnit, UltraTower, TracerProjectile, GeometricHero
from ui import OracleOfKimi, StyledButton


class TacticalDefenseGame:
    """Juego principal"""
    
    def __init__(self):
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Táctico - Powered by Kimi")
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.SysFont("arial", 52, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 28)
        self.font_small = pygame.font.SysFont("arial", 22)
        
        self.grass = GrassSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = ParticleSystem()
        self.oracle = OracleOfKimi()
        
        # Sistema de acciones (modular)
        self.action_menu = ActionMenuSystem()
        
        # Héroe del jugador
        self.hero = None
        
        self._create_buttons()
        self.reset_game()
    
    def _create_buttons(self):
        self.buttons = []
        
        self.btn_restart = StyledButton(
            SCREEN_WIDTH - 100, 10, 90, 40, "Reiniciar",
            (100, 50, 50), (150, 80, 80),
            self.reset_game
        )
        self.buttons.append(self.btn_restart)
        
        btn_width = 140
        btn_height = 45
        start_x = 20
        
        self.btn_berserker = StyledButton(
            start_x, SCREEN_HEIGHT - 60, btn_width, btn_height, "Berserker",
            (180, 50, 50), (220, 80, 80)
        )
        self.btn_assault = StyledButton(
            start_x + btn_width + 10, SCREEN_HEIGHT - 60, btn_width, btn_height, "Assault",
            (50, 150, 50), (80, 200, 80)
        )
        self.btn_ranger = StyledButton(
            start_x + (btn_width + 10) * 2, SCREEN_HEIGHT - 60, btn_width, btn_height, "Ranger",
            (50, 120, 180), (80, 160, 220)
        )
        self.btn_sniper = StyledButton(
            start_x + (btn_width + 10) * 3, SCREEN_HEIGHT - 60, btn_width, btn_height, "Sniper",
            (140, 50, 180), (180, 80, 220)
        )
        
        self.buttons.extend([
            self.btn_berserker, self.btn_assault,
            self.btn_ranger, self.btn_sniper
        ])
    
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
        configs = [("berserker", 1, 2), ("assault", 3, 3), ("ranger", 5, 2), 
                  ("sniper", 6, 4), ("assault", 2, 4)]
        
        for unit_type, col, row in configs:
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
        
        enemy_configs = [("berserker", 2, -3), ("assault", 3, -3), ("ranger", 4, -3),
                        ("sniper", 3, -4), ("assault", 4, -4)]
        
        for unit_type, col, row in enemy_configs:
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
        
        for btn in self.buttons:
            btn.update(mouse_pos)
        
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
                clicked_btn = False
                for btn in self.buttons:
                    if btn.handle_click(mouse_pos):
                        clicked_btn = True
                        break
                
                if not clicked_btn:
                    self._handle_click(mouse_pos)
        
        return True
    
    def _handle_click(self, mouse_pos):
        import pygame
        if self.phase != PHASE_PLAYER_TURN:
            return
        
        # Verificar clic en menú de acciones
        action_id = self.action_menu.handle_click(mouse_pos)
        if action_id:
            self._execute_action_from_menu(action_id)
            return
        
        tile = self.find_tile(mouse_pos)
        if not tile:
            return
        
        if not self.selected_tile:
            if tile.unit and tile.unit.owner == "player" and not tile.unit.has_moved:
                self.selected_tile = tile
                tile.selected = True
                self.update_valid_moves()
                # Mostrar menú de acciones
                self._show_action_menu(tile.unit)
                self.oracle.analyze_battlefield(
                    tile.unit, tile, self.grid,
                    self.player_units, self.enemy_units
                )
            return
        
        current = self.selected_tile
        
        if tile.valid_move and tile.is_empty():
            self.particles.spawn_dust(current.x, current.y)
            self._move_unit(current, tile)
            self.particles.spawn_dust(tile.x, tile.y)
            current.selected = False
            self.selected_tile = None
            self.action_menu_visible = False
            self.oracle.clear_recommendation(self.grid)
            self.update_valid_moves()
            return
        
        if current == tile:
            current.selected = False
            self.selected_tile = None
            self.action_menu_visible = False
            self.oracle.clear_recommendation(self.grid)
            self.update_valid_moves()
            return
        
        if tile.unit and tile.unit.owner == "player" and not tile.unit.has_moved:
            current.selected = False
            self.selected_tile = tile
            tile.selected = True
            self.update_valid_moves()
            self._show_action_menu(tile.unit)
            self.oracle.analyze_battlefield(
                tile.unit, tile, self.grid,
                self.player_units, self.enemy_units
            )
            return
        
        current.selected = False
        self.selected_tile = None
        self.action_menu_visible = False
        self.oracle.clear_recommendation(self.grid)
        self.update_valid_moves()
    
    def _show_action_menu(self, unit):
        """Muestra el menú de acciones para la unidad seleccionada."""
        self.action_menu_visible = True
        # Opciones basadas en el tipo de unidad
        if unit.unit_type == "berserker":
            self.action_menu_options = ["Mover", "Carga", "Furia"]
        elif unit.unit_type == "assault":
            self.action_menu_options = ["Mover", "Suprimir", "Refuerzo"]
        elif unit.unit_type == "ranger":
            self.action_menu_options = ["Mover", "Disparo Área", "Trampa"]
        elif unit.unit_type == "sniper":
            self.action_menu_options = ["Mover", "Disparo Largo", "Marca"]
        else:
            self.action_menu_options = ["Mover", "Ataque 1", "Ataque 2"]
    
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
    
    def _end_player_turn(self):
        self.phase = PHASE_ENEMY_TURN
        self.ai_timer = 0
        self.oracle.clear_recommendation(self.grid)
        
        
        for tile in self.grid.values():
            tile.selected = False
            tile.valid_move = False
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        
        for tile in self.grid.values():
            tile.update(mouse_pos)
        
        
        if self.phase == PHASE_PLAYER_TURN:
            pass
        elif self.phase == PHASE_ENEMY_TURN:
            self._execute_ai(dt)
        elif self.phase == PHASE_COMBAT:
            self._update_combat(dt)
        
        self.grass.update(dt)
    
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
        panel = pygame.Surface((SCREEN_WIDTH, 105), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 25, 35, 230), (0, 0, SCREEN_WIDTH, 105))
        self.screen.blit(panel, (0, 0))
        
        phases = {
            PHASE_PLAYER_TURN: ("TU TURNO", (100, 255, 100)),
            PHASE_ENEMY_TURN: ("TURNO ENEMIGO", (255, 100, 100)),
            PHASE_COMBAT: ("COMBATE", (255, 255, 100))
        }
        text, color = phases.get(self.phase, ("", (255, 255, 255)))
        self.screen.blit(self.font_medium.render(f"Turno {self.turn_number} | {text}", True, color), (20, 12))
        
        if self.phase == PHASE_PLAYER_TURN:
            if self.selected_tile:
                msgs = ["VERDE = Mover | DORADO = Mejor opción", "ESC: Cancelar | ESPACIO: Terminar"]
            else:
                msgs = ["Selecciona una unidad (círculo amarillo)", "Mueve 1 casilla | Ataca en combate"]
            for i, msg in enumerate(msgs):
                self.screen.blit(self.font_small.render(msg, True, (200, 200, 200)), (20, 48 + i*24))
        
        self.oracle.draw(self.screen, self.font_small)
        
        # Dibujar menú de acciones usando el sistema modular
        self.action_menu.draw(self.screen, self.font_small)
        
        for btn in self.buttons:
            if btn != self.btn_restart or self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
                btn.draw(self.screen, self.font_small)
        
        px = SCREEN_WIDTH - 300
        pygame.draw.rect(self.screen, (40, 70, 40), (px, 10, 130, 75))
        self.screen.blit(self.font_small.render(f"Unidades: {len(self.player_units)}", True, (100, 255, 100)), (px+10, 15))
        self.screen.blit(self.font_small.render(f"Torres: {len(self.player_towers)}", True, (100, 200, 255)), (px+10, 45))
        
        pygame.draw.rect(self.screen, (70, 40, 40), (px+140, 10, 130, 75))
        self.screen.blit(self.font_small.render(f"Enemigos: {len(self.enemy_units)}", True, (255, 100, 100)), (px+150, 15))
        self.screen.blit(self.font_small.render(f"Torres: {len(self.enemy_towers)}", True, (255, 150, 100)), (px+150, 45))
        
        if self.selected_tile and self.selected_tile.unit:
            self._draw_unit_info(self.selected_tile.unit)
    
    def _draw_unit_info(self, unit):
        import pygame
        x = 20
        y = SCREEN_HEIGHT - 110
        
        info = [
            f"{unit.unit_type.upper()}",
            f"Salud: {unit.health}/{unit.max_health}",
            f"Ataque: {unit.attack}",
            f"Rango: {unit.range}",
            f"Velocidad: {unit.speed}"
        ]
        
        for i, text in enumerate(info):
            color = (255, 255, 200) if i == 0 else (200, 200, 200)
            self.screen.blit(self.font_small.render(text, True, color), (x, y + i*22))
    
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
