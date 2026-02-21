"""
Clase Base para Acciones de Combate
====================================
Define la interfaz común para todas las acciones de combate.

Cada acción debe:
1. Validar si puede ejecutarse (can_execute)
2. Calcular costo en AP (get_cost)
3. Ejecutar la acción (execute)
4. Retornar resultado (ActionResult)

Principio: Una acción = Una responsabilidad
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List
from dataclasses import dataclass
from enum import Enum, auto


class ActionType(Enum):
    """Tipos de acciones de combate."""
    ATTACK = auto()
    DEFEND = auto()
    MOVE = auto()
    USE_ITEM = auto()
    SPECIAL = auto()
    SKIP = auto()


class ActionResultType(Enum):
    """Resultados posibles de una acción."""
    SUCCESS = auto()
    FAILED_NO_AP = auto()
    FAILED_NO_TARGET = auto()
    FAILED_OUT_OF_RANGE = auto()
    FAILED_INVALID = auto()
    CANCELLED = auto()


@dataclass
class ActionResult:
    """
    Resultado de ejecutar una acción.
    """
    success: bool
    result_type: ActionResultType
    message: str = ""
    ap_spent: int = 0
    damage_dealt: int = 0
    effects_applied: List[str] = None
    
    def __post_init__(self):
        if self.effects_applied is None:
            self.effects_applied = []
    
    @classmethod
    def success_result(cls, message: str = "", ap_spent: int = 0, **kwargs):
        """Factory para resultado exitoso."""
        return cls(
            success=True,
            result_type=ActionResultType.SUCCESS,
            message=message,
            ap_spent=ap_spent,
            **kwargs
        )
    
    @classmethod
    def failure_result(cls, result_type: ActionResultType, message: str = ""):
        """Factory para resultado fallido."""
        return cls(
            success=False,
            result_type=result_type,
            message=message,
            ap_spent=0
        )


class CombatAction(ABC):
    """
    Clase base abstracta para todas las acciones de combate.
    """
    
    # Identificador único de la acción
    action_id: str = "base_action"
    
    # Tipo de acción
    action_type: ActionType = ActionType.SPECIAL
    
    # Costo base en AP (sobrescribir en subclases)
    base_ap_cost: int = 0
    
    # Nombre mostrado en UI
    display_name: str = "Acción Base"
    
    # Descripción para tooltips
    description: str = ""
    
    def __init__(self, performer: Any):
        """
        Inicializa la acción.
        
        Args:
            performer: Unidad que ejecuta la acción
        """
        self.performer = performer
    
    @abstractmethod
    def can_execute(self, **kwargs) -> bool:
        """
        Verifica si la acción puede ejecutarse.
        
        Returns:
            True si se puede ejecutar
        """
        pass
    
    @abstractmethod
    def get_cost(self) -> int:
        """
        Calcula el costo en AP de esta acción.
        
        Returns:
            Costo en AP
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ActionResult:
        """
        Ejecuta la acción.
        
        Returns:
            Resultado de la acción
        """
        pass
    
    def validate_ap(self) -> bool:
        """
        Verifica si el performer tiene suficientes AP.
        
        Returns:
            True si tiene AP suficiente
        """
        if not hasattr(self.performer, 'action_points'):
            return True  # Sin sistema de AP, siempre puede
        
        return self.performer.action_points.can_afford(self.get_cost())
    
    def spend_ap(self) -> bool:
        """
        Gasta los AP de la acción.
        
        Returns:
            True si se gastó correctamente
        """
        if not hasattr(self.performer, 'action_points'):
            return True
        
        return self.performer.action_points.spend(self.get_cost())
    
    def get_ui_info(self) -> dict:
        """
        Obtiene información para mostrar en la UI.
        
        Returns:
            Diccionario con información de la acción
        """
        return {
            'id': self.action_id,
            'name': self.display_name,
            'description': self.description,
            'cost': self.get_cost(),
            'can_use': self.can_execute(),
            'type': self.action_type.name
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(performer={self.performer}, cost={self.get_cost()})"
