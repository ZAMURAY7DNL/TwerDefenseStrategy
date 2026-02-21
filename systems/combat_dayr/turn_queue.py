"""
Sistema de Cola de Turnos (Turn Queue)
======================================
Determina el orden en que las unidades actúan durante el combate.

Reglas:
- Las unidades actúan una a la vez, nunca simultáneamente
- El orden se determina por iniciativa/velocidad
- Una vez que todas las unidades actúan, se inicia una nueva ronda
- Las unidades muertas se eliminan de la cola

Flujo:
1. Generar cola ordenada por velocidad
2. Tomar siguiente unidad activa
3. Ejecutar turno (gastar AP)
4. Pasar a siguiente unidad
5. Al terminar la cola, nueva ronda
"""

from typing import List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class TurnEntry:
    """
    Representa una entrada en la cola de turnos.
    """
    unit: Any  # Referencia a la unidad
    initiative: int  # Valor para ordenar (velocidad + random)
    round_number: int  # En qué ronda actúa
    has_acted: bool = False  # Ya gastó su turno
    
    def __lt__(self, other):
        """Para ordenar por iniciativa descendente."""
        if not isinstance(other, TurnEntry):
            return NotImplemented
        return self.initiative > other.initiative  # Mayor iniciativa primero


class TurnQueue:
    """
    Gestiona la cola de turnos del combate.
    """
    
    def __init__(self):
        self._queue: List[TurnEntry] = []
        self._current_index: int = 0
        self._current_round: int = 1
        self._active_entry: Optional[TurnEntry] = None
    
    @property
    def current_round(self) -> int:
        """Número de ronda actual."""
        return self._current_round
    
    @property
    def is_empty(self) -> bool:
        """True si no hay unidades en la cola."""
        return len(self._queue) == 0
    
    @property
    def total_units(self) -> int:
        """Total de unidades en la cola (vivas)."""
        return len([e for e in self._queue if self._is_alive(e.unit)])
    
    @property
    def active_unit(self) -> Optional[Any]:
        """Unidad que está actuando actualmente."""
        if self._active_entry:
            return self._active_entry.unit
        return None
    
    def build_queue(self, units: List[Any]):
        """
        Construye la cola inicial ordenada por iniciativa.
        
        Args:
            units: Lista de unidades para agregar a la cola
        """
        import random
        
        self._queue.clear()
        self._current_index = 0
        self._current_round = 1
        
        for unit in units:
            if not self._is_alive(unit):
                continue
            
            # Iniciativa = velocidad + random(-2, 2) para variabilidad
            speed = getattr(unit, 'speed', 5)
            initiative = speed + random.randint(-2, 2)
            
            entry = TurnEntry(
                unit=unit,
                initiative=initiative,
                round_number=self._current_round
            )
            self._queue.append(entry)
        
        # Ordenar por iniciativa (mayor primero)
        self._queue.sort()
        
        # Establecer primera unidad activa
        self._advance_to_next_active()
    
    def next_turn(self) -> Optional[Any]:
        """
        Avanza al siguiente turno.
        
        Returns:
            La siguiente unidad activa o None si terminó combate
        """
        # Marcar actual como actuado
        if self._active_entry:
            self._active_entry.has_acted = True
        
        # Avanzar índice
        self._current_index += 1
        
        # Verificar si terminó la ronda
        if self._current_index >= len(self._queue):
            self._start_new_round()
        
        # Buscar siguiente unidad activa
        self._advance_to_next_active()
        
        return self.active_unit
    
    def remove_dead_units(self):
        """Elimina unidades muertas de la cola y ajusta índices."""
        if not self._queue:
            return
        
        # Guardar unidad activa antes de filtrar
        active_unit_id = id(self._active_entry.unit) if self._active_entry else None
        
        # Filtrar unidades vivas
        new_queue = []
        for entry in self._queue:
            if self._is_alive(entry.unit):
                new_queue.append(entry)
        
        self._queue = new_queue
        
        # Recalcular índice de la unidad activa
        if active_unit_id and self._queue:
            for i, entry in enumerate(self._queue):
                if id(entry.unit) == active_unit_id:
                    self._current_index = i
                    self._active_entry = entry
                    return
        
        # Si no se encontró, buscar siguiente activa
        self._advance_to_next_active()
    
    def get_queue_display(self) -> List[tuple]:
        """
        Obtiene información para mostrar la cola de turnos en UI.
        
        Returns:
            Lista de (nombre_unidad, iniciativa, es_actual)
        """
        result = []
        for i, entry in enumerate(self._queue):
            name = getattr(entry.unit, 'name', 'Unknown')
            is_current = (entry == self._active_entry)
            result.append((name, entry.initiative, is_current))
        return result
    
    def _start_new_round(self):
        """Inicia una nueva ronda, reseteando estados."""
        self._current_round += 1
        self._current_index = 0
        
        # Resetear flag de actuado
        for entry in self._queue:
            entry.has_acted = False
            entry.round_number = self._current_round
        
        # Reordenar por nueva iniciativa
        import random
        for entry in self._queue:
            speed = getattr(entry.unit, 'speed', 5)
            entry.initiative = speed + random.randint(-2, 2)
        
        self._queue.sort()
    
    def _advance_to_next_active(self):
        """Avanza al siguiente slot con una unidad viva."""
        while self._current_index < len(self._queue):
            entry = self._queue[self._current_index]
            if self._is_alive(entry.unit):
                self._active_entry = entry
                return
            self._current_index += 1
        
        # No hay más unidades activas
        self._active_entry = None
    
    def _is_alive(self, unit) -> bool:
        """Verifica si una unidad está viva."""
        if unit is None:
            return False
        if hasattr(unit, 'is_alive'):
            return unit.is_alive()
        if hasattr(unit, 'health'):
            return unit.health > 0
        return True
    
    def __len__(self) -> int:
        return len(self._queue)
    
    def __iter__(self):
        return iter(self._queue)
