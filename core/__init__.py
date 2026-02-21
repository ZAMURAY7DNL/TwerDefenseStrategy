"""
Núcleo del juego - Módulos principales
"""

from .game import TacticalDefenseGame
from .grid_manager import GridManager
from .unit_manager import UnitManager
from .combat_handler import CombatHandler
from .animation_manager import AnimationManager
from .renderer import GameRenderer

__all__ = [
    'TacticalDefenseGame',
    'GridManager',
    'UnitManager', 
    'CombatHandler',
    'AnimationManager',
    'GameRenderer',
]

# Nota: Dev tools se importan por separado, no son parte del juego
# from dev_tools.inspector import InspectorApp  # Solo para desarrollo
