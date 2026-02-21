"""
Tactical Defense - Juego Principal (Modular)
============================================
Punto central del juego. Maneja:
- Inicialización de sistemas
- Loop principal
- Input/Teclado
- Eventos de botones
- Coordinación entre módulos
"""
import pygame
from config.constants import *
from config.settings import *

# Sistemas
from systems import GrassSystem, ParticleSystem
from systems.alternating_turn_system import AlternatingTurnSystem, AlternatingPhase
from systems.enemy_ai import EnemyAI
from systems.sound_generator import SoundGenerator
from systems.music_external import start_music as start_epic_music, stop_music

# Core modular
from core.grid_manager import GridManager
from core.unit_manager import UnitManager
from core.combat_handler import CombatHandler
from core.animation_manager import AnimationManager
from core.renderer import GameRenderer

# UI y Entidades
from ui import OracleOfKimi, PersistentMenu
from ui.buttons import StyledButton
from entities import Hero


class TacticalDefenseGame:
    """Juego principal - Coordinador de sistemas."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Táctico - Day R Combat")
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.font_large = pygame.font.SysFont("arial", 52, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 28)
        self.font_small = pygame.font.SysFont("arial", 22)
        
        # Sistemas visuales
        self.grass = GrassSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = ParticleSystem()
        self.oracle = OracleOfKimi()
        
        # Sistema de audio
        self.sounds = SoundGenerator()
        
        # Módulos core
        self.grid = GridManager()
        self.units = UnitManager(self.grid)
        self.combat = CombatHandler(self.grid, self.units, self.particles)
        self.animations = AnimationManager(self.particles)
        self.enemy_ai = EnemyAI(self.grid, self.units, self.particles)
        self.renderer = GameRenderer(self.screen, self.font_large, self.font_medium, self.font_small)
        
        # Sistema de turnos
        self.alt_turn_system = AlternatingTurnSystem()
        self.alt_turn_system.on_unit_activate = self._on_unit_activate
        self.alt_turn_system.on_phase_change = self._on_phase_change
        
        # UI
        self.persistent_menu = PersistentMenu(x=20, y=110, width=150)
        
        # Estado del juego
        self.turn_number = 1
        self.phase = PHASE_PLAYER_TURN
        self.selected_tile = None
        
        # Botón de reinicio (para pantalla de victoria/derrota)
        self.btn_restart = StyledButton(
            x=SCREEN_WIDTH//2 - 75,
            y=SCREEN_HEIGHT//2 + 80,
            width=150,
            height=50,
            text="Reiniciar",
            action=lambda: self.reset_game()
        )
        
        self.reset_game()
    
    # ============================================================
    # INICIALIZACIÓN Y RESET
    # ============================================================
    
    def reset_game(self):
        """Reinicia el estado del juego."""
        self.turn_number = 1
        self.phase = PHASE_PLAYER_TURN
        self.selected_tile = None
        
        # Resetear módulos
        self.grid = GridManager()
        self.units = UnitManager(self.grid)
        self.units.setup_initial_units()
        
        # Reconectar grid a módulos que lo necesitan
        self.combat = CombatHandler(self.grid, self.units, self.particles)
        self.enemy_ai = EnemyAI(self.grid, self.units, self.particles)
        
        # Setup sistema de turnos
        troops = self.units.get_troops_only()
        self.alt_turn_system.setup(self.units.hero, troops, self.units.enemy_units)
        
        # Limpiar UI
        self.oracle.clear_recommendation(self.grid.grid)
        self.persistent_menu.clear()
        self.animations.clear()
        self.combat.clear_projectiles()
        
        # Iniciar música épica con nuevo sistema robusto
        start_epic_music()
    
    # ============================================================
    # CALLBACKS DEL SISTEMA DE TURNOS
    # ============================================================
    
    def _on_unit_activate(self, unit, unit_type):
        """Callback cuando se activa una unidad."""
        name = getattr(unit, 'name', getattr(unit, 'unit_type', 'Unidad'))
        print(f"[TURN] Activado: {name} ({unit_type})")
        
        # Limpiar selección anterior
        if self.selected_tile:
            self.selected_tile.selected = False
            self.selected_tile = None
        
        # Auto-seleccionar unidad del jugador
        if unit_type in ['hero', 'player_troop']:
            tile = self.grid.get_unit_tile(unit)
            if tile:
                self.selected_tile = tile
                tile.selected = True
                if unit_type == 'hero':
                    self._show_hero_menu(unit)
                else:
                    self._show_troop_menu(unit)
        
        self.grid.update_valid_moves(self.selected_tile)
    
    def _on_phase_change(self, phase, winner):
        """Callback cuando cambia la fase del combate."""
        if phase == AlternatingPhase.ENDED:
            if winner == "player":
                self.phase = PHASE_VICTORY
                self.sounds.victory_jingle().play()
            else:
                self.phase = PHASE_DEFEAT
                self.sounds.defeat_sound().play()
    
    # ============================================================
    # INPUT Y EVENTOS
    # ============================================================
    
    def handle_input(self):
        """Maneja todo el input del usuario."""
        mouse_pos = pygame.mouse.get_pos()
        dt = self.clock.tick(FPS) / 1000.0
        
        # Actualizar menú
        self.persistent_menu.update(mouse_pos, dt)
        
        # Actualizar botón de reinicio si estamos en victoria/derrota
        if self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
            self.btn_restart.update(mouse_pos, dt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Sonido de click al presionar
                self.sounds.button_click().play()
                self.persistent_menu.handle_click(mouse_pos, pressed=True)
                
                # Manejar click en botón de reinicio
                if self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
                    self.btn_restart.handle_click(mouse_pos, pressed=True)
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                action = self.persistent_menu.handle_click(mouse_pos, pressed=False)
                if not action:
                    self._handle_click(mouse_pos)
                
                # Manejar release en botón de reinicio
                if self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
                    self.btn_restart.handle_click(mouse_pos, pressed=False)
        
        return True
    
    def _handle_keydown(self, key):
        """Maneja teclas presionadas."""
        if key == pygame.K_ESCAPE and self.selected_tile:
            self._clear_selection()
        
        if key == pygame.K_SPACE and self.phase == PHASE_PLAYER_TURN:
            self._end_player_turn()
        
        if key == pygame.K_r and self.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
            self.reset_game()
    
    def _handle_click(self, mouse_pos):
        """Maneja clicks en el grid."""
        # Solo procesar clicks en turno del jugador
        if not self.alt_turn_system.is_player_turn():
            return
        
        tile = self.grid.find_tile(mouse_pos)
        if not tile:
            return
        
        active_unit = self.alt_turn_system.active_unit
        
        # Seleccionar unidad
        if not self.selected_tile:
            if tile.unit and tile.unit == active_unit:
                self._select_unit(tile)
            return
        
        current = self.selected_tile
        
        # Mover unidad
        if tile.valid_move and tile.is_empty():
            self._execute_move(current, tile)
            return
        
        # Atacar enemigo
        if tile.unit and tile.unit.owner == "enemy":
            self._execute_attack(current.unit, tile.unit)
            return
        
        # Deseleccionar
        if current == tile:
            self._clear_selection()
            return
        
        # Cambiar selección
        if tile.unit and tile.unit == active_unit:
            self._switch_selection(current, tile)
            return
        
        self._clear_selection()
    
    def _select_unit(self, tile):
        """Selecciona una unidad."""
        self.selected_tile = tile
        tile.selected = True
        self.grid.update_valid_moves(tile)
        
        if self.alt_turn_system.is_hero_turn():
            self._show_hero_menu(tile.unit)
        else:
            self._show_troop_menu(tile.unit)
        
        self.oracle.analyze_battlefield(
            tile.unit, tile, self.grid.grid,
            self.units.player_units, self.units.enemy_units
        )
    
    def _clear_selection(self):
        """Limpia la selección actual."""
        if self.selected_tile:
            self.selected_tile.selected = False
            self.selected_tile = None
        self.persistent_menu.clear()
        self.oracle.clear_recommendation(self.grid.grid)
        self.grid.update_valid_moves(None)
    
    def _switch_selection(self, current_tile, new_tile):
        """Cambia la selección a otra unidad."""
        current_tile.selected = False
        self.selected_tile = new_tile
        new_tile.selected = True
        self.grid.update_valid_moves(new_tile)
        
        if self.alt_turn_system.is_hero_turn():
            self._show_hero_menu(new_tile.unit)
        else:
            self._show_troop_menu(new_tile.unit)
    
    def _execute_move(self, from_tile, to_tile):
        """Ejecuta un movimiento."""
        def is_active_unit(unit):
            return unit == self.alt_turn_system.active_unit
        
        if self.combat.execute_move_free(from_tile, to_tile, is_active_unit):
            # Sonido de paso al moverse
            self.sounds.footstep('grass', 'normal').play()
            
            from_tile.selected = False
            self.selected_tile = None
            self.persistent_menu.clear()
            self.oracle.clear_recommendation(self.grid.grid)
            self.grid.update_valid_moves(None)
    
    def _execute_attack(self, attacker, target):
        """Ejecuta un ataque."""
        if self.alt_turn_system.is_hero_turn():
            result = self.combat.execute_hero_attack(attacker, target)
            if result and result.get('success'):
                if attacker.action_points.is_depleted:
                    self._clear_selection()
                    self.alt_turn_system.end_hero_turn()
        else:
            self.combat.execute_troop_attack(attacker, target)
            self._clear_selection()
            self.alt_turn_system.end_troop_turn()
    
    # ============================================================
    # MENÚS DE ACCIÓN
    # ============================================================
    
    def _show_hero_menu(self, hero):
        """Muestra menú para el héroe."""
        self.persistent_menu.clear()
        self.persistent_menu.title = "HEROE"
        
        # Mover
        can_move = not getattr(hero, 'has_moved', False)
        self.persistent_menu.add_button("Mover" if can_move else "Mover ✓", None, enabled=can_move)
        
        # Ataque básico
        can_slash = hero.can_use_power('slash')
        self.persistent_menu.add_button(f"Ataque (2 AP)", 
                                       lambda: self._execute_hero_power('slash'), 
                                       enabled=can_slash)
        
        # Golpe poderoso
        can_power = hero.can_use_power('power_strike')
        self.persistent_menu.add_button(f"Golpe Fuerte (4 AP)",
                                       lambda: self._execute_hero_power('power_strike'),
                                       enabled=can_power)
        
        # Curación
        can_heal = hero.can_use_power('heal')
        self.persistent_menu.add_button(f"Curar (3 AP)",
                                       lambda: self._execute_hero_power('heal'),
                                       enabled=can_heal)
        
        # Terminar
        self.persistent_menu.add_button("Terminar Turno", lambda: self._end_player_turn())
    
    def _show_troop_menu(self, unit):
        """Muestra menú para tropas normales."""
        self.persistent_menu.clear()
        self.persistent_menu.title = "TROPA"
        
        can_attack = self.units.can_unit_attack_anyone(unit, self.units.enemy_units)
        has_moved = getattr(unit, 'has_moved', False)
        
        if has_moved:
            if can_attack:
                self.persistent_menu.add_button("Atacar", None)
                self.persistent_menu.add_button("Terminar", lambda: self._end_player_turn())
            else:
                self.persistent_menu.add_button("Pasar Turno", lambda: self._end_player_turn())
        else:
            self.persistent_menu.add_button("Mover", None)
            if can_attack:
                self.persistent_menu.add_button("Atacar", None)
            self.persistent_menu.add_button("Terminar", lambda: self._end_player_turn())
    
    def _execute_hero_power(self, power_id):
        """Ejecuta un poder del héroe."""
        if not self.selected_tile or not self.alt_turn_system.is_hero_turn():
            return
        
        hero = self.selected_tile.unit
        target = self.units.find_nearest_enemy(hero, self.units.enemy_units)
        
        if not target:
            print("[ERROR] No hay objetivo")
            return
        
        # Iniciar animación
        self.animations.start_attack_animation(hero, target, power_id)
        
        # Sonido de poder
        self.sounds.hero_power_use(power_id).play()
        
        # Ejecutar daño
        result = self.combat.execute_hero_power(hero, target, power_id)
        
        if result and result.get('success') and hero.action_points.is_depleted:
            self._clear_selection()
            self.alt_turn_system.end_hero_turn()
    
    def _end_player_turn(self):
        """Termina el turno del jugador."""
        self._clear_selection()
        
        if self.alt_turn_system.is_hero_turn():
            self.alt_turn_system.end_hero_turn()
        elif self.alt_turn_system.is_troop_turn():
            self.alt_turn_system.end_troop_turn()
    
    # ============================================================
    # UPDATE
    # ============================================================
    
    def update(self, dt):
        """Actualiza el estado del juego."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Actualizar grid
        self.grid.update(mouse_pos)
        
        # Actualizar sistema de turnos
        self._update_turn_system(dt)
        
        # Actualizar animaciones
        self.animations.update(dt)
        self.animations.update_projectiles(dt)
        
        # Actualizar grass
        self.grass.update(dt)
        
        # Actualizar partículas
        self.particles.update(dt)
    
    def _update_turn_system(self, dt):
        """Actualiza el sistema de turnos."""
        alt = self.alt_turn_system
        
        # Actualizar fase visual
        if alt.phase == AlternatingPhase.PLAYER_HERO:
            self.phase = PHASE_PLAYER_TURN
        elif alt.phase == AlternatingPhase.PLAYER_TROOP:
            self.phase = PHASE_PLAYER_TURN
        elif alt.phase == AlternatingPhase.ENEMY:
            self.phase = PHASE_ENEMY_TURN
        
        # Actualizar unidad activa
        active = alt.active_unit
        if active:
            self.units.update(dt, self.grass)
        
        # Procesar turno enemigo
        if alt.is_enemy_turn() and active:
            self._process_enemy_turn(dt)
        
        # Actualizar sistema alternado
        alt.update(dt)
    
    def _process_enemy_turn(self, dt):
        """Procesa el turno de un enemigo."""
        if self.alt_turn_system.enemy_action_taken:
            return
        
        enemy = self.alt_turn_system.active_unit
        if not enemy or not enemy.is_alive():
            self.alt_turn_system.enemy_finished_action()
            return
        
        # Usar el sistema de IA
        self.enemy_ai.process_turn(enemy)
        self.alt_turn_system.enemy_finished_action()
    
    # ============================================================
    # DRAW
    # ============================================================
    
    def draw(self):
        """Dibuja el juego."""
        self.renderer.clear_screen()
        self.renderer.draw_background(self.grass, self.grid.neutral_zone_y)
        self.renderer.draw_grid(self.grid)
        self.renderer.draw_units_and_towers(self.grid)
        
        # Proyectiles
        all_projectiles = self.combat.projectiles + self.enemy_ai.projectiles + self.animations.projectiles
        self.renderer.draw_projectiles(all_projectiles)
        
        # Partículas
        self.renderer.draw_particles(self.particles)
        
        # UI
        self.renderer.draw_ui(self.alt_turn_system, self.units, 
                             self.selected_tile, self.oracle, self.persistent_menu)
        
        # Pantallas de victoria/derrota
        if self.phase == PHASE_VICTORY:
            self.renderer.draw_victory_screen(self.btn_restart)
        elif self.phase == PHASE_DEFEAT:
            self.renderer.draw_defeat_screen(self.btn_restart)
        
        self.renderer.flip_display()
    
    # ============================================================
    # MAIN LOOP
    # ============================================================
    
    def run(self):
        """Loop principal del juego."""
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
