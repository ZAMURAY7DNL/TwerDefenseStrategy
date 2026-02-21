"""
Sistema de Turnos Alternados Estrictos
======================================
Alternancia: Enemigo -> Jugador (Héroe) -> Enemigo -> Jugador (Tropa) -> ...

Reglas:
1. Cada lado actúa UNA unidad a la vez
2. El jugador primero controla al HÉROE (con AP)
3. Luego controla cada TROPA (sin AP, movimiento libre)
4. El enemigo actúa una unidad por turno
"""

from enum import Enum, auto
from typing import List, Any, Optional


class AlternatingPhase(Enum):
    PLAYER_HERO = auto()      # Turno del héroe (con AP)
    PLAYER_TROOP = auto()     # Turno de una tropa (sin AP)
    ENEMY = auto()            # Turno enemigo
    ENDED = auto()            # Combate terminado


class AlternatingTurnSystem:
    """
    Sistema de turnos estrictamente alternados.
    """
    
    # Tiempo mínimo que dura un turno enemigo (segundos)
    ENEMY_TURN_DELAY = 1.5
    
    def __init__(self):
        self.phase = AlternatingPhase.PLAYER_HERO
        self.turn_number = 1
        
        # Listas de unidades
        self.hero = None           # Unidad héroe (única)
        self.player_troops = []    # Tropas del jugador
        self.enemies = []          # Enemigos
        
        # Índices para seguimiento
        self.current_troop_index = 0
        self.current_enemy_index = 0
        
        # Estado
        self.active_unit = None
        self.waiting_for_input = True
        
        # Control de turno enemigo
        self.enemy_action_taken = False  # Ya actuó este turno
        self.enemy_turn_timer = 0.0      # Temporizador del turno
        
        # Callbacks
        self.on_phase_change = None
        self.on_unit_activate = None
    
    def setup(self, hero: Any, troops: List[Any], enemies: List[Any]):
        """
        Configura el sistema con las unidades.
        """
        self.hero = hero
        self.player_troops = [t for t in troops if t != hero and hasattr(t, 'is_alive')]
        self.enemies = [e for e in enemies if hasattr(e, 'is_alive')]
        
        self.phase = AlternatingPhase.PLAYER_HERO
        self.turn_number = 1
        self.current_troop_index = 0
        self.current_enemy_index = 0
        
        # Resetear flags de movimiento
        self._reset_unit_flags()
        
        self._activate_current_unit()
    
    def _reset_unit_flags(self):
        """Resetea flags de movimiento de todas las unidades."""
        if self.hero and hasattr(self.hero, 'has_moved'):
            self.hero.has_moved = False
        for troop in self.player_troops:
            if hasattr(troop, 'has_moved'):
                troop.has_moved = False
        for enemy in self.enemies:
            if hasattr(enemy, 'has_moved'):
                enemy.has_moved = False
    
    def next_turn(self):
        """
        Avanza al siguiente turno con patrón estricto:
        Héroe → Enemigo → Tropa1 → Enemigo → Tropa2 → Enemigo → ...
        """
        if self.phase == AlternatingPhase.PLAYER_HERO:
            # Héroe terminó → enemigo
            self.phase = AlternatingPhase.ENEMY
            self._activate_enemy()
            
        elif self.phase == AlternatingPhase.ENEMY:
            # Enemigo terminó → siguiente unidad del jugador
            self._activate_next_player_after_enemy()
                
        elif self.phase == AlternatingPhase.PLAYER_TROOP:
            # Tropa terminó → siguiente enemigo
            self.phase = AlternatingPhase.ENEMY
            self._activate_enemy()
        
        # Verificar fin de combate
        self._check_combat_end()
    
    def _activate_next_player_after_enemy(self):
        """Después de un enemigo, activa siguiente unidad del jugador."""
        # Si es el primer enemigo de la ronda (índice 0), va a la primera tropa
        # (el héroe ya actuó al principio)
        # Si hay más tropas, va a la siguiente
        # Si no hay más tropas, nueva ronda
        
        found = False
        while self.current_troop_index < len(self.player_troops):
            troop = self.player_troops[self.current_troop_index]
            if troop.is_alive():
                self.phase = AlternatingPhase.PLAYER_TROOP
                self.active_unit = troop
                found = True
                if self.on_unit_activate:
                    self.on_unit_activate(troop, "player_troop")
                return
            self.current_troop_index += 1
        
        # No hay más tropas vivas
        if not found:
            self._start_new_round()
    
    def end_hero_turn(self):
        """
        El jugador termina el turno del héroe manualmente.
        """
        if self.phase == AlternatingPhase.PLAYER_HERO and self.hero:
            self.hero.end_turn()
            self.next_turn()
    
    def end_troop_turn(self):
        """
        El jugador termina el turno de la tropa actual.
        Después de una tropa, SIEMPRE viene un enemigo.
        """
        if self.phase == AlternatingPhase.PLAYER_TROOP:
            self.current_troop_index += 1
            # Ir al siguiente enemigo (no a la siguiente tropa inmediatamente)
            self.next_turn()
    
    def _try_activate_troop(self):
        """
        Intenta activar la siguiente tropa disponible.
        Si no hay más, pasa a enemigo.
        """
        # Buscar siguiente tropa viva que no haya actuado
        while self.current_troop_index < len(self.player_troops):
            troop = self.player_troops[self.current_troop_index]
            if troop.is_alive():
                self.phase = AlternatingPhase.PLAYER_TROOP
                self.active_unit = troop
                if self.on_unit_activate:
                    self.on_unit_activate(troop, "player_troop")
                return
            self.current_troop_index += 1
        
        # No hay más tropas, nueva ronda
        self._start_new_round()
    
    def _start_new_round(self):
        """Inicia una nueva ronda, reseteando todo."""
        self.current_troop_index = 0
        self.current_enemy_index = 0
        self.turn_number += 1
        
        # Resetear flags de todas las unidades
        self._reset_unit_flags()
        
        # Recuperar AP del héroe
        if self.hero and hasattr(self.hero, 'action_points'):
            self.hero.action_points.recover()
        
        # Volver al héroe
        if self.hero and self.hero.is_alive():
            self.phase = AlternatingPhase.PLAYER_HERO
            self._activate_hero()
        else:
            # Sin héroe, ir a tropas
            self._try_activate_troop()
    
    def _activate_current_unit(self):
        """Activa la unidad según la fase actual."""
        if self.phase == AlternatingPhase.PLAYER_HERO:
            self._activate_hero()
        elif self.phase == AlternatingPhase.ENEMY:
            self._activate_enemy()
        elif self.phase == AlternatingPhase.PLAYER_TROOP:
            self._try_activate_troop()
    
    def _activate_hero(self):
        """Activa al héroe."""
        if self.hero and self.hero.is_alive():
            self.active_unit = self.hero
            self.waiting_for_input = True
            if self.on_unit_activate:
                self.on_unit_activate(self.hero, "hero")
        else:
            # Sin héroe, pasar a tropas
            self._try_activate_troop()
    
    def _activate_enemy(self):
        """Activa al siguiente enemigo vivo."""
        print(f"[DEBUG] Activando enemigo desde índice {self.current_enemy_index}, total enemigos: {len(self.enemies)}")
        
        # Buscar siguiente enemigo vivo desde el índice actual
        while self.current_enemy_index < len(self.enemies):
            enemy = self.enemies[self.current_enemy_index]
            is_alive = enemy.is_alive() if hasattr(enemy, 'is_alive') else False
            name = getattr(enemy, 'name', getattr(enemy, 'unit_type', 'Unknown'))
            print(f"[DEBUG]  - Enemigo {self.current_enemy_index}: {name}, vivo: {is_alive}")
            
            if is_alive:
                print(f"[DEBUG]  -> Activando {name}")
                self.active_unit = enemy
                self.waiting_for_input = False
                self.enemy_action_taken = False
                self.enemy_turn_timer = 0.0
                if self.on_unit_activate:
                    self.on_unit_activate(enemy, "enemy")
                return
            self.current_enemy_index += 1
        
        print(f"[DEBUG] No hay más enemigos vivos, yendo a tropas")
        # No hay más enemigos vivos en esta ronda
        self._activate_next_player_after_enemy()
    
    def update(self, dt):
        """Actualiza el temporizador del turno enemigo."""
        if self.phase == AlternatingPhase.ENEMY and self.enemy_action_taken:
            self.enemy_turn_timer += dt
            # Solo avanzar cuando haya pasado el tiempo mínimo
            if self.enemy_turn_timer >= self.ENEMY_TURN_DELAY:
                self.current_enemy_index += 1
                self.next_turn()
    
    def enemy_finished_action(self):
        """Llamar cuando el enemigo termina su acción."""
        if self.phase == AlternatingPhase.ENEMY:
            self.enemy_action_taken = True
            # El avance real se hace en update() cuando pase el tiempo
    
    def _check_combat_end(self):
        """Verifica si el combate debe terminar."""
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        alive_player = []
        if self.hero and self.hero.is_alive():
            alive_player.append(self.hero)
        alive_player.extend([t for t in self.player_troops if t.is_alive()])
        
        if not alive_enemies or not alive_player:
            self.phase = AlternatingPhase.ENDED
            if self.on_phase_change:
                winner = "player" if alive_player else "enemy"
                self.on_phase_change(self.phase, winner)
    
    def get_phase_name(self) -> str:
        """Retorna nombre legible de la fase."""
        names = {
            AlternatingPhase.PLAYER_HERO: "TURNO DEL HÉROE",
            AlternatingPhase.PLAYER_TROOP: "TURNO DE TROPA",
            AlternatingPhase.ENEMY: "TURNO ENEMIGO",
            AlternatingPhase.ENDED: "COMBATE TERMINADO",
        }
        return names.get(self.phase, "DESCONOCIDO")
    
    def get_phase_color(self):
        """Retorna color asociado a la fase."""
        colors = {
            AlternatingPhase.PLAYER_HERO: (255, 215, 0),    # Dorado
            AlternatingPhase.PLAYER_TROOP: (100, 255, 100), # Verde
            AlternatingPhase.ENEMY: (255, 100, 100),        # Rojo
            AlternatingPhase.ENDED: (200, 200, 200),        # Gris
        }
        return colors.get(self.phase, (255, 255, 255))
    
    def is_player_turn(self) -> bool:
        """True si es turno del jugador (héroe o tropa)."""
        return self.phase in [AlternatingPhase.PLAYER_HERO, AlternatingPhase.PLAYER_TROOP]
    
    def is_hero_turn(self) -> bool:
        """True si es turno específico del héroe."""
        return self.phase == AlternatingPhase.PLAYER_HERO
    
    def is_troop_turn(self) -> bool:
        """True si es turno de una tropa."""
        return self.phase == AlternatingPhase.PLAYER_TROOP
    
    def is_enemy_turn(self) -> bool:
        """True si es turno enemigo."""
        return self.phase == AlternatingPhase.ENEMY
    
    def skip_to_next(self):
        """Fuerza el salto al siguiente turno."""
        self.next_turn()
