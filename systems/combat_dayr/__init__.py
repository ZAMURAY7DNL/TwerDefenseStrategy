"""
Sistema de Combate Day R Style
===============================
Sistema de combate por turnos individuales inspirado en Day R Survival.

Cada unidad actúa individualmente con un pool de Puntos de Acción (AP).
No hay fase de "combate automático" - cada acción es decidida por el jugador.

Arquitectura modular:
- action_points: Sistema de Puntos de Acción
- turn_queue: Cola de turnos (quién actúa cuándo)
- combat_action: Clase base para acciones
- action_types: Tipos específicos de acciones
- damage_system: Cálculo de daño con zonas corporales
- targeting_system: Selección de objetivos
- combat_manager: Orquestador principal
"""

from .action_points import ActionPointsSystem
from .turn_queue import TurnQueue, TurnEntry
from .combat_action import CombatAction, ActionResult
from .action_types import AttackAction, DefendAction, MoveAction, UseItemAction, SkipAction
from .damage_system import DamageSystem, BodyZone, DamageResult
from .targeting_system import TargetingSystem
from .combat_manager import CombatManager, CombatState

__all__ = [
    'ActionPointsSystem',
    'TurnQueue',
    'TurnEntry', 
    'CombatAction',
    'ActionResult',
    'AttackAction',
    'DefendAction',
    'MoveAction',
    'UseItemAction',
    'SkipAction',
    'DamageSystem',
    'BodyZone',
    'DamageResult',
    'TargetingSystem',
    'CombatManager',
    'CombatState',
]
