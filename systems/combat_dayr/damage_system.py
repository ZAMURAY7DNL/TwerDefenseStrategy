"""
Sistema de Daño con Zonas Corporales (Day R Style)
==================================================
Maneja el cálculo de daño con sistema de zonas/body parts.

Zonas corporales:
- HEAD: Daño x2, baja probabilidad de acierto
- TORSO: Daño normal, alta probabilidad
- ARMS: Daño x0.7, puede desarmar
- LEGS: Daño x0.8, reduce movimiento

Cada ataque apunta a una zona con probabilidades diferentes.
"""

import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any


class BodyZone(Enum):
    """Zonas corporales para el sistema de daño."""
    HEAD = auto()
    TORSO = auto()
    LEFT_ARM = auto()
    RIGHT_ARM = auto()
    LEFT_LEG = auto()
    RIGHT_LEG = auto()


@dataclass
class DamageResult:
    """
    Resultado de un cálculo de daño.
    """
    raw_damage: int
    final_damage: int
    zone_hit: BodyZone
    is_critical: bool
    is_hit: bool  # Si acertó o falló
    effects: List[str] = None
    message: str = ""
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []


class DamageSystem:
    """
    Sistema centralizado de cálculo de daño.
    """
    
    # Multiplicadores de daño por zona
    ZONE_MULTIPLIERS = {
        BodyZone.HEAD: 2.0,
        BodyZone.TORSO: 1.0,
        BodyZone.LEFT_ARM: 0.7,
        BodyZone.RIGHT_ARM: 0.7,
        BodyZone.LEFT_LEG: 0.8,
        BodyZone.RIGHT_LEG: 0.8,
    }
    
    # Probabilidad base de impactar cada zona (debe sumar 100)
    ZONE_HIT_CHANCES = {
        BodyZone.HEAD: 10,
        BodyZone.TORSO: 40,
        BodyZone.LEFT_ARM: 12,
        BodyZone.RIGHT_ARM: 12,
        BodyZone.LEFT_LEG: 13,
        BodyZone.RIGHT_LEG: 13,
    }
    
    # Efectos especiales por zona
    ZONE_EFFECTS = {
        BodyZone.HEAD: ["dizzy", "vision_impaired"],
        BodyZone.LEFT_ARM: ["attack_penalty"],
        BodyZone.RIGHT_ARM: ["attack_penalty"],
        BodyZone.LEFT_LEG: ["movement_penalty"],
        BodyZone.RIGHT_LEG: ["movement_penalty"],
    }
    
    def __init__(self):
        self._critical_chance = 0.05  # 5% base
        self._critical_multiplier = 1.5
    
    def calculate_damage(
        self,
        attacker: Any,
        target: Any,
        base_damage: int,
        targeted_zone: BodyZone = None,
        accuracy_modifier: float = 1.0
    ) -> DamageResult:
        """
        Calcula el daño completo de un ataque.
        
        Args:
            attacker: Unidad atacante
            target: Unidad objetivo
            base_damage: Daño base del ataque
            targeted_zone: Zona específica (None = aleatoria ponderada)
            accuracy_modifier: Modificador de precisión
            
        Returns:
            Resultado del daño calculado
        """
        # 1. Determinar zona impactada
        zone = targeted_zone or self._roll_zone()
        
        # 2. Verificar si acierta (con modificadores)
        hit_chance = self._calculate_hit_chance(attacker, target, zone, accuracy_modifier)
        
        if random.random() > hit_chance:
            return DamageResult(
                raw_damage=base_damage,
                final_damage=0,
                zone_hit=zone,
                is_critical=False,
                is_hit=False,
                message="¡Falló!"
            )
        
        # 3. Aplicar multiplicador de zona
        zone_mult = self.ZONE_MULTIPLIERS.get(zone, 1.0)
        damage_after_zone = base_damage * zone_mult
        
        # 4. Verificar crítico
        is_critical = random.random() < self._critical_chance
        if is_critical:
            damage_after_zone *= self._critical_multiplier
        
        # 5. Aplicar defensa del objetivo
        final_damage = self._apply_defense(target, int(damage_after_zone))
        
        # 6. Determinar efectos especiales
        effects = self._determine_effects(zone, is_critical)
        
        # 7. Generar mensaje
        msg = self._generate_message(zone, final_damage, is_critical, is_hit=True)
        
        return DamageResult(
            raw_damage=base_damage,
            final_damage=final_damage,
            zone_hit=zone,
            is_critical=is_critical,
            is_hit=True,
            effects=effects,
            message=msg
        )
    
    def _roll_zone(self) -> BodyZone:
        """Determina la zona impactada aleatoriamente."""
        roll = random.randint(1, 100)
        cumulative = 0
        
        for zone, chance in self.ZONE_HIT_CHANCES.items():
            cumulative += chance
            if roll <= cumulative:
                return zone
        
        return BodyZone.TORSO  # Default
    
    def _calculate_hit_chance(
        self,
        attacker: Any,
        target: Any,
        zone: BodyZone,
        accuracy_modifier: float
    ) -> float:
        """Calcula la probabilidad de acertar."""
        # Base: 90%
        base_chance = 0.90
        
        # Modificador por zona (cabeza es más difícil)
        zone_modifiers = {
            BodyZone.HEAD: 0.7,
            BodyZone.TORSO: 1.0,
            BodyZone.LEFT_ARM: 0.9,
            BodyZone.RIGHT_ARM: 0.9,
            BodyZone.LEFT_LEG: 0.85,
            BodyZone.RIGHT_LEG: 0.85,
        }
        
        zone_mod = zone_modifiers.get(zone, 1.0)
        
        # Modificador por habilidad del atacante
        attacker_skill = getattr(attacker, 'accuracy', 0)
        skill_bonus = attacker_skill * 0.01  # +1% por punto
        
        # Modificador por evasión del objetivo
        target_evasion = getattr(target, 'evasion', 0)
        evasion_penalty = target_evasion * 0.01
        
        # Aplicar todos los modificadores
        final_chance = (base_chance + skill_bonus - evasion_penalty) * zone_mod * accuracy_modifier
        
        return min(0.95, max(0.05, final_chance))  # Entre 5% y 95%
    
    def _apply_defense(self, target: Any, damage: int) -> int:
        """Aplica reducción de daño por defensa/armadura."""
        # Defensa base
        defense = getattr(target, 'defense', 0)
        
        # Estado defensivo
        if hasattr(target, 'is_defending') and target.is_defending:
            defense_multiplier = getattr(target, 'defense_multiplier', 0.5)
            damage = int(damage * defense_multiplier)
        
        # Reducción lineal de daño por defensa
        # Cada punto de defensa reduce 2% el daño, máx 50%
        reduction = min(0.5, defense * 0.02)
        damage = int(damage * (1 - reduction))
        
        return max(1, damage)  # Mínimo 1 de daño
    
    def _determine_effects(self, zone: BodyZone, is_critical: bool) -> List[str]:
        """Determina efectos de estado según la zona."""
        effects = []
        
        # Efectos base por zona
        zone_effects = self.ZONE_EFFECTS.get(zone, [])
        effects.extend(zone_effects)
        
        # Crítico añade efectos extra
        if is_critical:
            effects.append("critical_hit")
            if zone == BodyZone.HEAD:
                effects.append("stunned")
        
        return effects
    
    def _generate_message(
        self,
        zone: BodyZone,
        damage: int,
        is_critical: bool,
        is_hit: bool
    ) -> str:
        """Genera mensaje descriptivo del impacto."""
        if not is_hit:
            return "¡Falló!"
        
        zone_names = {
            BodyZone.HEAD: "cabeza",
            BodyZone.TORSO: "torso",
            BodyZone.LEFT_ARM: "brazo izquierdo",
            BodyZone.RIGHT_ARM: "brazo derecho",
            BodyZone.LEFT_LEG: "pierna izquierda",
            BodyZone.RIGHT_LEG: "pierna derecha",
        }
        
        zone_name = zone_names.get(zone, "cuerpo")
        
        if is_critical:
            return f"¡CRÍTICO en {zone_name}! {damage} daño"
        
        return f"Impacto en {zone_name}: {damage} daño"
    
    def get_zone_name(self, zone: BodyZone) -> str:
        """Obtiene nombre legible de una zona."""
        names = {
            BodyZone.HEAD: "Cabeza",
            BodyZone.TORSO: "Torso",
            BodyZone.LEFT_ARM: "Brazo Izq.",
            BodyZone.RIGHT_ARM: "Brazo Der.",
            BodyZone.LEFT_LEG: "Pierna Izq.",
            BodyZone.RIGHT_LEG: "Pierna Der.",
        }
        return names.get(zone, "Cuerpo")
    
    def get_all_zones(self) -> List[BodyZone]:
        """Retorna todas las zonas corporales."""
        return list(BodyZone)
