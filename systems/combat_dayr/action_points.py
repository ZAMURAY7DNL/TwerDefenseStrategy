"""
Sistema de Puntos de Acción (Action Points)
===========================================
Maneja el pool de puntos de acción para cada unidad en combate.

Cada unidad tiene:
- AP máximo (base + modificadores)
- AP actual (gastado en acciones)
- AP por turno (cuánto recupera al inicio de su turno)

Reglas:
- Cada acción consume AP
- Si no hay suficientes AP, no se puede ejecutar la acción
- Al inicio del turno, se recupera AP_BASE + modificadores
"""


class ActionPointsSystem:
    """
    Gestiona los puntos de acción de una unidad.
    """
    
    # Costos base de acciones (pueden modificarse por habilidades/equipo)
    COST_MOVE = 2
    COST_ATTACK = 3
    COST_DEFEND = 1
    COST_USE_ITEM = 2
    COST_SPECIAL = 4
    
    # Recuperación base por turno
    AP_RECOVERY_BASE = 5
    AP_MAX_BASE = 8
    
    def __init__(self, max_ap: int = None, recovery_per_turn: int = None):
        """
        Inicializa el sistema de AP.
        
        Args:
            max_ap: AP máximo (default: AP_MAX_BASE)
            recovery_per_turn: AP recuperado por turno (default: AP_RECOVERY_BASE)
        """
        self._max_ap = max_ap or self.AP_MAX_BASE
        self._recovery = recovery_per_turn or self.AP_RECOVERY_BASE
        self._current_ap = self._max_ap
        
        # Modificadores temporales
        self._bonus_max_ap = 0
        self._bonus_recovery = 0
        self._cost_multiplier = 1.0
    
    @property
    def current(self) -> int:
        """AP actual disponible."""
        return int(self._current_ap)
    
    @property
    def maximum(self) -> int:
        """AP máximo (base + bonus)."""
        return self._max_ap + self._bonus_max_ap
    
    @property
    def recovery(self) -> int:
        """AP recuperado por turno."""
        return self._recovery + self._bonus_recovery
    
    @property
    def is_depleted(self) -> bool:
        """True si no queda AP."""
        return self._current_ap <= 0
    
    def can_afford(self, cost: int) -> bool:
        """
        Verifica si hay suficientes AP para una acción.
        
        Args:
            cost: Costo de la acción
            
        Returns:
            True si se puede pagar el costo
        """
        actual_cost = int(cost * self._cost_multiplier)
        return self._current_ap >= actual_cost
    
    def spend(self, cost: int) -> bool:
        """
        Gasta AP en una acción.
        
        Args:
            cost: Costo de la acción
            
        Returns:
            True si se pudo gastar (suficientes AP)
        """
        actual_cost = int(cost * self._cost_multiplier)
        
        if self._current_ap < actual_cost:
            return False
        
        self._current_ap -= actual_cost
        return True
    
    def recover(self, amount: int = None):
        """
        Recupera AP (inicio de turno).
        
        Args:
            amount: Cantidad a recuperar (default: recovery)
        """
        recover_amount = amount or self.recovery
        self._current_ap = min(self._current_ap + recover_amount, self.maximum)
    
    def reset(self):
        """Restaura AP al máximo (fin de combate)."""
        self._current_ap = self.maximum
        self.clear_modifiers()
    
    def add_bonus_max_ap(self, bonus: int):
        """Añade bonus temporal al AP máximo."""
        self._bonus_max_ap += bonus
    
    def add_bonus_recovery(self, bonus: int):
        """Añade bonus temporal a la recuperación."""
        self._bonus_recovery += bonus
    
    def set_cost_multiplier(self, multiplier: float):
        """Modifica el costo de todas las acciones (ej: fatiga)."""
        self._cost_multiplier = max(0.1, multiplier)
    
    def clear_modifiers(self):
        """Limpia todos los modificadores temporales."""
        self._bonus_max_ap = 0
        self._bonus_recovery = 0
        self._cost_multiplier = 1.0
    
    def get_cost(self, action_type: str) -> int:
        """
        Obtiene el costo de un tipo de acción.
        
        Args:
            action_type: 'move', 'attack', 'defend', 'use_item', 'special'
            
        Returns:
            Costo en AP
        """
        costs = {
            'move': self.COST_MOVE,
            'attack': self.COST_ATTACK,
            'defend': self.COST_DEFEND,
            'use_item': self.COST_USE_ITEM,
            'special': self.COST_SPECIAL,
        }
        base_cost = costs.get(action_type, self.COST_ATTACK)
        return int(base_cost * self._cost_multiplier)
    
    def __repr__(self) -> str:
        return f"ActionPoints({self.current}/{self.maximum})"
