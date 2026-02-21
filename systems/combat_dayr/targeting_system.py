"""
Sistema de Targeting (Selección de Objetivos)
=============================================
Maneja la selección de objetivos para acciones de combate.

Funcionalidades:
- Obtener objetivos válidos según criterios
- Filtrar por facción (amigo/enemigo)
- Filtrar por rango/distancia
- Selección de objetivos prioritarios
"""

from typing import List, Any, Optional, Callable
import math


class TargetingSystem:
    """
    Sistema para encontrar y seleccionar objetivos.
    """
    
    def __init__(self):
        self._filter_chain: List[Callable] = []
    
    def get_valid_targets(
        self,
        performer: Any,
        potential_targets: List[Any],
        target_faction: str = "enemy",
        require_line_of_sight: bool = False,
        max_range: float = None
    ) -> List[Any]:
        """
        Obtiene lista de objetivos válidos.
        
        Args:
            performer: Unidad que realiza la acción
            potential_targets: Lista de posibles objetivos
            target_faction: 'enemy', 'ally', 'any'
            require_line_of_sight: Si requiere línea de visión
            max_range: Rango máximo (None = cualquier distancia)
            
        Returns:
            Lista de objetivos válidos
        """
        valid = []
        
        for target in potential_targets:
            if not self._is_valid_target(target):
                continue
            
            # Filtrar por facción
            if not self._check_faction(performer, target, target_faction):
                continue
            
            # Filtrar por rango
            if max_range is not None:
                if not self._is_in_range(performer, target, max_range):
                    continue
            
            # Filtrar por línea de visión
            if require_line_of_sight:
                if not self._has_line_of_sight(performer, target):
                    continue
            
            valid.append(target)
        
        return valid
    
    def get_nearest_target(
        self,
        performer: Any,
        targets: List[Any]
    ) -> Optional[Any]:
        """
        Encuentra el objetivo más cercano.
        
        Args:
            performer: Unidad de referencia
            targets: Lista de objetivos a considerar
            
        Returns:
            Objetivo más cercano o None
        """
        nearest = None
        nearest_dist = float('inf')
        
        for target in targets:
            if not self._is_valid_target(target):
                continue
            
            dist = self._get_distance(performer, target)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = target
        
        return nearest
    
    def get_weakest_target(
        self,
        targets: List[Any],
        health_threshold: float = 0.5
    ) -> Optional[Any]:
        """
        Encuentra el objetivo más débil (menos salud).
        
        Args:
            targets: Lista de objetivos
            health_threshold: Solo considerar si tiene menos de X% de vida
            
        Returns:
            Objetivo más débil o None
        """
        weakest = None
        weakest_health = float('inf')
        
        for target in targets:
            if not self._is_valid_target(target):
                continue
            
            health = getattr(target, 'health', 100)
            max_health = getattr(target, 'max_health', 100)
            health_pct = health / max_health if max_health > 0 else 1.0
            
            # Solo considerar si está debajo del umbral
            if health_pct > health_threshold:
                continue
            
            if health < weakest_health:
                weakest_health = health
                weakest = target
        
        return weakest
    
    def get_strongest_target(
        self,
        targets: List[Any]
    ) -> Optional[Any]:
        """
        Encuentra el objetivo más fuerte (mayor ataque).
        
        Args:
            targets: Lista de objetivos
            
        Returns:
            Objetivo más fuerte o None
        """
        strongest = None
        strongest_attack = -1
        
        for target in targets:
            if not self._is_valid_target(target):
                continue
            
            attack = getattr(target, 'attack', 0)
            if attack > strongest_attack:
                strongest_attack = attack
                strongest = target
        
        return strongest
    
    def sort_by_distance(
        self,
        performer: Any,
        targets: List[Any],
        ascending: bool = True
    ) -> List[Any]:
        """
        Ordena objetivos por distancia.
        
        Args:
            performer: Unidad de referencia
            targets: Lista a ordenar
            ascending: True = más cercano primero
            
        Returns:
            Lista ordenada
        """
        targets_with_dist = []
        for target in targets:
            dist = self._get_distance(performer, target)
            targets_with_dist.append((dist, target))
        
        targets_with_dist.sort(key=lambda x: x[0], reverse=not ascending)
        return [t[1] for t in targets_with_dist]
    
    def get_targets_in_area(
        self,
        center_x: float,
        center_y: float,
        radius: float,
        potential_targets: List[Any]
    ) -> List[Any]:
        """
        Obtiene objetivos dentro de un área circular.
        
        Args:
            center_x, center_y: Centro del área
            radius: Radio del área
            potential_targets: Lista de posibles objetivos
            
        Returns:
            Objetivos dentro del área
        """
        in_area = []
        
        for target in potential_targets:
            if not self._is_valid_target(target):
                continue
            
            tx = getattr(target, 'visual_x', getattr(target, 'x', 0))
            ty = getattr(target, 'visual_y', getattr(target, 'y', 0))
            
            dist = math.sqrt((center_x - tx)**2 + (center_y - ty)**2)
            if dist <= radius:
                in_area.append(target)
        
        return in_area
    
    def _is_valid_target(self, target: Any) -> bool:
        """Verifica si el objetivo es válido (vivo y existente)."""
        if target is None:
            return False
        
        if hasattr(target, 'is_alive'):
            return target.is_alive()
        
        if hasattr(target, 'health'):
            return target.health > 0
        
        return True
    
    def _check_faction(
        self,
        performer: Any,
        target: Any,
        target_faction: str
    ) -> bool:
        """Verifica si el objetivo es de la facción requerida."""
        if target_faction == "any":
            return True
        
        performer_faction = getattr(performer, 'owner', None)
        target_owner = getattr(target, 'owner', None)
        
        if target_faction == "enemy":
            return performer_faction != target_owner
        elif target_faction == "ally":
            return performer_faction == target_owner
        
        return True
    
    def _is_in_range(
        self,
        performer: Any,
        target: Any,
        max_range: float
    ) -> bool:
        """Verifica si el objetivo está dentro del rango."""
        dist = self._get_distance(performer, target)
        return dist <= max_range
    
    def _has_line_of_sight(
        self,
        performer: Any,
        target: Any
    ) -> bool:
        """
        Verifica línea de visión (simplificado).
        En una implementación completa verificaría obstáculos.
        """
        # Simplificado: siempre tiene línea de visión
        return True
    
    def _get_distance(self, entity_a: Any, entity_b: Any) -> float:
        """Calcula distancia entre dos entidades."""
        ax = getattr(entity_a, 'visual_x', getattr(entity_a, 'x', 0))
        ay = getattr(entity_a, 'visual_y', getattr(entity_a, 'y', 0))
        bx = getattr(entity_b, 'visual_x', getattr(entity_b, 'x', 0))
        by = getattr(entity_b, 'visual_y', getattr(entity_b, 'y', 0))
        
        return math.sqrt((ax - bx)**2 + (ay - by)**2)
    
    def get_distance_to(self, performer: Any, target: Any) -> float:
        """Distancia pública entre performer y target."""
        return self._get_distance(performer, target)
