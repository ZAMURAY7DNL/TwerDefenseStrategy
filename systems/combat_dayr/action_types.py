"""
Tipos de Acciones de Combate
============================
Implementaciones concretas de CombatAction.

Cada clase maneja UNA sola mecánica:
- AttackAction: Atacar a un objetivo
- DefendAction: Defenderse (reducir daño)
- MoveAction: Moverse a otra posición
- UseItemAction: Usar un item del inventario
"""

from typing import Any, Optional
from .combat_action import CombatAction, ActionResult, ActionResultType, ActionType


class AttackAction(CombatAction):
    """
    Acción de atacar a un objetivo.
    """
    action_id = "attack"
    action_type = ActionType.ATTACK
    base_ap_cost = 3
    display_name = "Atacar"
    description = "Ataca a un objetivo enemigo dentro del alcance."
    
    def __init__(self, performer: Any):
        super().__init__(performer)
        self.target: Optional[Any] = None
        self.weapon: Optional[Any] = None
    
    def set_target(self, target: Any):
        """Establece el objetivo del ataque."""
        self.target = target
    
    def set_weapon(self, weapon: Any):
        """Establece el arma a usar (None = ataque desarmado)."""
        self.weapon = weapon
    
    def can_execute(self, **kwargs) -> bool:
        """Verifica si se puede atacar."""
        # Verificar AP
        if not self.validate_ap():
            return False
        
        # Verificar objetivo
        if self.target is None:
            return False
        
        # Verificar que el objetivo esté vivo
        if hasattr(self.target, 'is_alive') and not self.target.is_alive():
            return False
        
        # Verificar rango
        if not self._check_range():
            return False
        
        return True
    
    def get_cost(self) -> int:
        """Costo en AP (modificado por arma si aplica)."""
        cost = self.base_ap_cost
        
        # Algunas armas pueden modificar el costo
        if self.weapon and hasattr(self.weapon, 'ap_cost_modifier'):
            cost += self.weapon.ap_cost_modifier
        
        return max(1, cost)
    
    def execute(self, **kwargs) -> ActionResult:
        """Ejecuta el ataque."""
        # Validar
        if not self.can_execute():
            if not self.validate_ap():
                return ActionResult.failure_result(
                    ActionResultType.FAILED_NO_AP,
                    "No tienes suficientes Puntos de Acción"
                )
            if self.target is None:
                return ActionResult.failure_result(
                    ActionResultType.FAILED_NO_TARGET,
                    "No hay objetivo seleccionado"
                )
            return ActionResult.failure_result(
                ActionResultType.FAILED_OUT_OF_RANGE,
                "Objetivo fuera de alcance"
            )
        
        # Gastar AP
        ap_cost = self.get_cost()
        self.spend_ap()
        
        # Calcular daño
        damage = self._calculate_damage()
        
        # Aplicar daño
        actual_damage = 0
        if hasattr(self.target, 'take_damage'):
            actual_damage = self.target.take_damage(damage)
        
        # Mensaje de resultado
        msg = f"Ataque exitoso! Daño: {actual_damage}"
        
        return ActionResult.success_result(
            message=msg,
            ap_spent=ap_cost,
            damage_dealt=actual_damage
        )
    
    def _check_range(self) -> bool:
        """Verifica si el objetivo está en rango."""
        if not hasattr(self.performer, 'visual_x') or not hasattr(self.target, 'visual_x'):
            return True  # Sin posición, asumir válido
        
        px, py = self.performer.visual_x, self.performer.visual_y
        tx, ty = self.target.visual_x, self.target.visual_y
        
        distance = ((px - tx)**2 + (py - ty)**2)**0.5
        
        # Obtener rango del performer
        attack_range = getattr(self.performer, 'range', 1)
        if hasattr(self.performer, 'get_attack_range_pixels'):
            attack_range = self.performer.get_attack_range_pixels()
        
        return distance <= attack_range
    
    def _calculate_damage(self) -> int:
        """Calcula el daño del ataque."""
        base_damage = getattr(self.performer, 'attack', 10)
        
        # Modificadores de arma
        if self.weapon and hasattr(self.weapon, 'damage_bonus'):
            base_damage += self.weapon.damage_bonus
        
        # Aquí se podrían agregar críticos, etc.
        
        return max(1, base_damage)


class DefendAction(CombatAction):
    """
    Acción de defenderse (reduce daño recibido hasta el próximo turno).
    """
    action_id = "defend"
    action_type = ActionType.DEFEND
    base_ap_cost = 1
    display_name = "Defender"
    description = "Reduce el daño recibido en 50% hasta tu próximo turno."
    
    def __init__(self, performer: Any):
        super().__init__(performer)
        self.damage_reduction = 0.5  # 50% reducción
    
    def can_execute(self, **kwargs) -> bool:
        """Siempre se puede defender si hay AP."""
        return self.validate_ap()
    
    def get_cost(self) -> int:
        return self.base_ap_cost
    
    def execute(self, **kwargs) -> ActionResult:
        """Aplica estado de defensa."""
        if not self.can_execute():
            return ActionResult.failure_result(
                ActionResultType.FAILED_NO_AP,
                "No tienes suficientes Puntos de Acción"
            )
        
        self.spend_ap()
        
        # Aplicar estado defensivo al performer
        if hasattr(self.performer, 'set_defending'):
            self.performer.set_defending(True, self.damage_reduction)
        
        return ActionResult.success_result(
            message="Te pones en posición defensiva. Daño reducido 50%.",
            ap_spent=self.get_cost(),
            effects_applied=["defending"]
        )


class MoveAction(CombatAction):
    """
    Acción de moverse a otra posición.
    """
    action_id = "move"
    action_type = ActionType.MOVE
    base_ap_cost = 2
    display_name = "Mover"
    description = "Mueve la unidad a una posición adyacente."
    
    def __init__(self, performer: Any):
        super().__init__(performer)
        self.destination: Optional[Any] = None  # Tile destino
    
    def set_destination(self, tile: Any):
        """Establece el tile destino."""
        self.destination = tile
    
    def can_execute(self, **kwargs) -> bool:
        """Verifica si se puede mover."""
        if not self.validate_ap():
            return False
        
        if self.destination is None:
            return False
        
        # Verificar que el destino esté vacío
        if hasattr(self.destination, 'is_empty'):
            if not self.destination.is_empty():
                return False
        
        # Verificar que sea adyacente
        if not self._is_adjacent():
            return False
        
        return True
    
    def get_cost(self) -> int:
        """Costo modificado por terreno si aplica."""
        cost = self.base_ap_cost
        
        # Terreno difícil puede aumentar costo
        if self.destination and hasattr(self.destination, 'movement_cost'):
            cost += self.destination.movement_cost
        
        return cost
    
    def execute(self, **kwargs) -> ActionResult:
        """Ejecuta el movimiento."""
        if not self.can_execute():
            if not self.validate_ap():
                return ActionResult.failure_result(
                    ActionResultType.FAILED_NO_AP,
                    "No tienes suficientes Puntos de Acción"
                )
            return ActionResult.failure_result(
                ActionResultType.FAILED_INVALID,
                "Movimiento inválido"
            )
        
        ap_cost = self.get_cost()
        self.spend_ap()
        
        # Realizar movimiento
        if hasattr(self.performer, 'move_to') and hasattr(self.destination, 'x'):
            self.performer.move_to(self.destination.x, self.destination.y)
        
        return ActionResult.success_result(
            message="Movimiento completado",
            ap_spent=ap_cost
        )
    
    def _is_adjacent(self) -> bool:
        """Verifica si el destino es adyacente al performer."""
        # Simplificado: asumir válido si no tenemos coordenadas
        if not hasattr(self.performer, 'visual_x') or not hasattr(self.destination, 'x'):
            return True
        
        # Aquí se debería verificar vecindad en grid hexagonal
        return True


class UseItemAction(CombatAction):
    """
    Acción de usar un item del inventario.
    """
    action_id = "use_item"
    action_type = ActionType.USE_ITEM
    base_ap_cost = 2
    display_name = "Usar Item"
    description = "Usa un item de tu inventario."
    
    def __init__(self, performer: Any):
        super().__init__(performer)
        self.item: Optional[Any] = None
        self.target: Optional[Any] = None  # Puede ser uno mismo u otro
    
    def set_item(self, item: Any):
        """Establece el item a usar."""
        self.item = item
    
    def set_target(self, target: Any):
        """Establece el objetivo (default: uno mismo)."""
        self.target = target
    
    def can_execute(self, **kwargs) -> bool:
        """Verifica si se puede usar el item."""
        if not self.validate_ap():
            return False
        
        if self.item is None:
            return False
        
        # Verificar que el performer tenga el item
        if hasattr(self.performer, 'inventory'):
            if self.item not in self.performer.inventory:
                return False
        
        return True
    
    def get_cost(self) -> int:
        """Costo base (items pueden modificar)."""
        cost = self.base_ap_cost
        
        if self.item and hasattr(self.item, 'ap_cost'):
            cost = self.item.ap_cost
        
        return cost
    
    def execute(self, **kwargs) -> ActionResult:
        """Usa el item."""
        if not self.can_execute():
            return ActionResult.failure_result(
                ActionResultType.FAILED_NO_AP,
                "No puedes usar este item"
            )
        
        ap_cost = self.get_cost()
        self.spend_ap()
        
        # Aplicar efecto del item
        target = self.target or self.performer
        effects = []
        
        if self.item and hasattr(self.item, 'use'):
            effects = self.item.use(target)
        
        item_name = getattr(self.item, 'name', 'Item')
        
        return ActionResult.success_result(
            message=f"Usado: {item_name}",
            ap_spent=ap_cost,
            effects_applied=effects
        )


class SkipAction(CombatAction):
    """
    Acción de saltar turno (recupera AP extra).
    """
    action_id = "skip"
    action_type = ActionType.SKIP
    base_ap_cost = 0
    display_name = "Saltar Turno"
    description = "Termina tu turno temprano y recupera +2 AP."
    
    def can_execute(self, **kwargs) -> bool:
        """Siempre se puede saltar turno."""
        return True
    
    def get_cost(self) -> int:
        return 0
    
    def execute(self, **kwargs) -> ActionResult:
        """Salta el turno y recupera AP."""
        bonus_ap = 2
        
        if hasattr(self.performer, 'action_points'):
            self.performer.action_points.recover(bonus_ap)
        
        return ActionResult.success_result(
            message=f"Turno saltado. Recuperaste +{bonus_ap} AP.",
            ap_spent=0,
            effects_applied=["skip_turn", f"recover_{bonus_ap}_ap"]
        )
