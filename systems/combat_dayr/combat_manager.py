"""
Combat Manager - Orquestador Principal
======================================
Coordina todos los sistemas de combate.

Responsabilidades:
1. Iniciar/terminar combates
2. Gestionar la cola de turnos
3. Procesar acciones de unidades
4. Mantener estado del combate
5. Notificar eventos a la UI

NO implementa mecánicas de combate directamente,
delega a los sistemas especializados.
"""

from typing import List, Any, Optional, Callable
from enum import Enum, auto

from .action_points import ActionPointsSystem
from .turn_queue import TurnQueue
from .combat_action import CombatAction, ActionResult, ActionType
from .action_types import AttackAction, DefendAction, MoveAction, UseItemAction, SkipAction
from .damage_system import DamageSystem, BodyZone, DamageResult
from .targeting_system import TargetingSystem


class CombatState(Enum):
    """Estados posibles del combate."""
    INACTIVE = auto()
    SETUP = auto()
    WAITING_PLAYER = auto()  # Esperando input del jugador
    WAITING_ENEMY = auto()   # IA procesando
    EXECUTING_ACTION = auto()  # Animando acción
    ENDED = auto()


class CombatManager:
    """
    Gestor principal del sistema de combate Day R style.
    """
    
    def __init__(self):
        # Sistemas especializados
        self.turn_queue = TurnQueue()
        self.damage_system = DamageSystem()
        self.targeting = TargetingSystem()
        
        # Estado
        self.state = CombatState.INACTIVE
        self.player_units: List[Any] = []
        self.enemy_units: List[Any] = []
        self.all_units: List[Any] = []
        
        # Callbacks para UI
        self.on_turn_start: Optional[Callable] = None
        self.on_action_executed: Optional[Callable] = None
        self.on_combat_end: Optional[Callable] = None
        self.on_unit_died: Optional[Callable] = None
        
        # Acción pendiente del jugador
        self.pending_action: Optional[CombatAction] = None
        self.selected_target: Optional[Any] = None
        
        # Log de combate
        self.combat_log: List[str] = []
    
    def start_combat(self, player_units: List[Any], enemy_units: List[Any]):
        """
        Inicia un nuevo combate.
        
        Args:
            player_units: Lista de unidades del jugador
            enemy_units: Lista de unidades enemigas
        """
        self.state = CombatState.SETUP
        
        # Guardar referencias
        self.player_units = [u for u in player_units if self._is_alive(u)]
        self.enemy_units = [u for u in enemy_units if self._is_alive(u)]
        self.all_units = self.player_units + self.enemy_units
        
        # Inicializar AP para todas las unidades
        for unit in self.all_units:
            if not hasattr(unit, 'action_points'):
                unit.action_points = ActionPointsSystem()
            unit.action_points.reset()
        
        # Construir cola de turnos
        self.turn_queue.build_queue(self.all_units)
        
        # Limpiar log
        self.combat_log.clear()
        self._log("=== COMBATE INICIADO ===")
        
        # Iniciar primer turno
        self._start_next_turn()
    
    def end_combat(self):
        """Termina el combate actual."""
        self.state = CombatState.ENDED
        self._log("=== COMBATE TERMINADO ===")
        
        # Limpiar estados temporales
        for unit in self.all_units:
            if hasattr(unit, 'set_defending'):
                unit.set_defending(False)
        
        if self.on_combat_end:
            winner = "player" if self.get_alive_enemies() == 0 else "enemy"
            self.on_combat_end(winner)
    
    def update(self, dt: float):
        """
        Actualiza el estado del combate (llamar cada frame).
        
        Args:
            dt: Delta time en segundos
        """
        if self.state == CombatState.INACTIVE or self.state == CombatState.ENDED:
            return
        
        # Verificar condiciones de victoria/derrota
        if self._check_combat_end():
            return
        
        # Procesar turno actual según estado
        if self.state == CombatState.WAITING_ENEMY:
            self._process_enemy_turn(dt)
        
        # Actualizar unidades (manejar diferentes firmas de update)
        import inspect
        for unit in self.all_units:
            if hasattr(unit, 'update'):
                try:
                    # Verificar firma del método update
                    sig = inspect.signature(unit.update)
                    params = list(sig.parameters.keys())
                    
                    if len(params) >= 3:  # self, dt, grass_system
                        unit.update(dt, None)
                    else:  # Solo self, dt (torres)
                        unit.update(dt)
                except Exception:
                    # Fallback: intentar sin parámetro extra
                    try:
                        unit.update(dt)
                    except Exception:
                        pass
    
    def execute_player_action(self, action: CombatAction) -> ActionResult:
        """
        Ejecuta una acción del jugador.
        
        Args:
            action: Acción a ejecutar
            
        Returns:
            Resultado de la acción
        """
        if self.state != CombatState.WAITING_PLAYER:
            return action.execute()  # Fallback
        
        # Verificar que sea turno del jugador
        active = self.turn_queue.active_unit
        if active != action.performer:
            from .combat_action import ActionResult, ActionResultType
            return ActionResult.failure_result(
                ActionResultType.FAILED_INVALID,
                "No es tu turno"
            )
        
        # Verificar que el performer sea del jugador
        if active not in self.player_units:
            return ActionResult.failure_result(
                ActionResultType.FAILED_INVALID,
                "No es una unidad del jugador"
            )
        
        # Ejecutar
        result = action.execute()
        
        # Procesar resultado
        self._process_action_result(action, result)
        
        return result
    
    def can_execute_action(self, action: CombatAction) -> bool:
        """
        Verifica si una acción puede ejecutarse ahora.
        
        Args:
            action: Acción a verificar
            
        Returns:
            True si se puede ejecutar
        """
        if self.state != CombatState.WAITING_PLAYER:
            return False
        
        active = self.turn_queue.active_unit
        if active != action.performer:
            return False
        
        return action.can_execute()
    
    def skip_turn(self) -> ActionResult:
        """
        Salta el turno actual (recupera AP extra).
        
        Returns:
            Resultado de la acción
        """
        active = self.turn_queue.active_unit
        if not active:
            from .combat_action import ActionResult, ActionResultType
            return ActionResult.failure_result(
                ActionResultType.FAILED_INVALID,
                "No hay unidad activa"
            )
        
        action = SkipAction(active)
        
        if active in self.player_units:
            return self.execute_player_action(action)
        else:
            result = action.execute()
            self._process_action_result(action, result)
            return result
    
    def end_current_turn(self):
        """Fuerza el fin del turno actual."""
        active = self.turn_queue.active_unit
        if active:
            self._log(f"{self._get_unit_name(active)} termina su turno")
        
        # Quitar estado defensivo
        if active and hasattr(active, 'set_defending'):
            active.set_defending(False)
        
        # Avanzar cola
        next_unit = self.turn_queue.next_turn()
        
        if next_unit:
            self._start_next_turn()
        else:
            # No hay más unidades, terminar combate
            self.end_combat()
    
    def get_active_unit(self) -> Optional[Any]:
        """Retorna la unidad que está actuando actualmente."""
        return self.turn_queue.active_unit
    
    def get_active_unit_ap(self) -> Optional[ActionPointsSystem]:
        """Retorna el sistema de AP de la unidad activa."""
        active = self.get_active_unit()
        if active and hasattr(active, 'action_points'):
            return active.action_points
        return None
    
    def get_available_actions(self, unit: Any) -> List[CombatAction]:
        """
        Obtiene lista de acciones disponibles para una unidad.
        
        Args:
            unit: Unidad a consultar
            
        Returns:
            Lista de acciones posibles
        """
        actions = []
        
        # Movimiento
        move = MoveAction(unit)
        actions.append(move)
        
        # Ataque (si hay enemigos en rango)
        attack = AttackAction(unit)
        enemies = self.get_alive_enemies()
        valid_targets = self.targeting.get_valid_targets(
            unit, enemies, "enemy", max_range=unit.get_attack_range_pixels() if hasattr(unit, 'get_attack_range_pixels') else 100
        )
        if valid_targets:
            attack.set_target(valid_targets[0])  # Primer objetivo por defecto
            actions.append(attack)
        
        # Defensa
        actions.append(DefendAction(unit))
        
        # Usar item (si tiene inventario)
        if hasattr(unit, 'inventory') and unit.inventory:
            item_action = UseItemAction(unit)
            item_action.set_item(unit.inventory[0])
            actions.append(item_action)
        
        # Saltar turno
        actions.append(SkipAction(unit))
        
        return actions
    
    def get_alive_player_units(self) -> List[Any]:
        """Retorna unidades del jugador vivas."""
        return [u for u in self.player_units if self._is_alive(u)]
    
    def get_alive_enemies(self) -> List[Any]:
        """Retorna enemigos vivos."""
        return [u for u in self.enemy_units if self._is_alive(u)]
    
    def get_combat_log(self, max_entries: int = 10) -> List[str]:
        """Retorna últimas entradas del log."""
        return self.combat_log[-max_entries:]
    
    def _start_next_turn(self):
        """Inicia el siguiente turno en la cola."""
        active = self.turn_queue.active_unit
        
        if not active:
            self.end_combat()
            return
        
        # Recuperar AP
        if hasattr(active, 'action_points'):
            active.action_points.recover()
        
        # Limpiar estado defensivo previo
        if hasattr(active, 'set_defending'):
            active.set_defending(False)
        
        self._log(f"Turno de: {self._get_unit_name(active)} (AP: {active.action_points.current if hasattr(active, 'action_points') else 'N/A'})")
        
        # Determinar estado
        if active in self.player_units:
            self.state = CombatState.WAITING_PLAYER
            if self.on_turn_start:
                self.on_turn_start(active, "player")
        else:
            self.state = CombatState.WAITING_ENEMY
            if self.on_turn_start:
                self.on_turn_start(active, "enemy")
    
    def _process_enemy_turn(self, dt: float):
        """
        Procesa el turno de la IA (simplificado).
        En una implementación completa esto usaría un sistema de IA más sofisticado.
        """
        active = self.turn_queue.active_unit
        if not active or active in self.player_units:
            return
        
        # IA básica: atacar al jugador más cercano si puede, sino acercarse
        # Esto es un placeholder - en producción usar sistema de IA dedicado
        self._execute_basic_ai(active)
    
    def _execute_basic_ai(self, enemy: Any):
        """IA básica para enemigos."""
        # Obtener jugadores vivos
        players = self.get_alive_player_units()
        if not players:
            self.end_current_turn()
            return
        
        # Intentar atacar
        nearest = self.targeting.get_nearest_target(enemy, players)
        if nearest and hasattr(enemy, 'action_points'):
            attack_range = getattr(enemy, 'range', 1) * 40  # Aproximación
            distance = self.targeting.get_distance_to(enemy, nearest)
            
            if distance <= attack_range and enemy.action_points.can_afford(3):
                # Atacar
                action = AttackAction(enemy)
                action.set_target(nearest)
                result = action.execute()
                self._process_action_result(action, result)
                
                if enemy.action_points.is_depleted:
                    self.end_current_turn()
                return
        
        # No puede atacar o no tiene AP, terminar turno
        self.end_current_turn()
    
    def _process_action_result(self, action: CombatAction, result: ActionResult):
        """Procesa el resultado de una acción."""
        # Loggear
        if result.message:
            self._log(result.message)
        
        # Notificar
        if self.on_action_executed:
            self.on_action_executed(action, result)
        
        # Verificar muertes
        self._check_deaths()
        
        # Verificar si la unidad se quedó sin AP
        performer = action.performer
        if hasattr(performer, 'action_points') and performer.action_points.is_depleted:
            self._log(f"{self._get_unit_name(performer)} se quedó sin AP")
            self.end_current_turn()
    
    def _check_deaths(self):
        """Verifica y procesa unidades muertas."""
        for unit in self.all_units[:]:
            if not self._is_alive(unit):
                self._log(f"¡{self._get_unit_name(unit)} ha caído!")
                if self.on_unit_died:
                    self.on_unit_died(unit)
        
        # Limpiar cola
        self.turn_queue.remove_dead_units()
    
    def _check_combat_end(self) -> bool:
        """Verifica si el combate debe terminar."""
        alive_players = len(self.get_alive_player_units())
        alive_enemies = len(self.get_alive_enemies())
        
        if alive_players == 0 or alive_enemies == 0:
            self.end_combat()
            return True
        
        return False
    
    def _is_alive(self, unit: Any) -> bool:
        """Verifica si una unidad está viva."""
        if unit is None:
            return False
        if hasattr(unit, 'is_alive'):
            return unit.is_alive()
        if hasattr(unit, 'health'):
            return unit.health > 0
        return True
    
    def _get_unit_name(self, unit: Any) -> str:
        """Obtiene nombre legible de una unidad."""
        if hasattr(unit, 'name'):
            return unit.name
        if hasattr(unit, 'unit_type'):
            return unit.unit_type.capitalize()
        return "Unidad"
    
    def _log(self, message: str):
        """Añade entrada al log de combate."""
        self.combat_log.append(message)
