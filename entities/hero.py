"""
Héroe Principal - Sistema AP + Geometría Avanzada
=================================================
El personaje principal del jugador.
- Sistema de Puntos de Acción (AP)
- +25 figuras geométricas para personalización
- Poderes/habilidades con costo de AP proporcional
- Movimiento gratuito (no consume AP)
- Animaciones detalladas
"""

import pygame
import math
import random
from systems.combat_dayr import ActionPointsSystem


class HeroPowers:
    """Poderes disponibles para el héroe."""
    
    POWERS = {
        'slash': {
            'name': 'Corte Rápido',
            'description': 'Ataque básico rápido',
            'ap_cost': 2,
            'damage_mult': 1.0,
            'range': 1,
            'icon': 'sword',
            'color': (200, 200, 200),
        },
        'power_strike': {
            'name': 'Golpe Poderoso',
            'description': 'Ataque fuerte que consume más AP',
            'ap_cost': 4,
            'damage_mult': 2.0,
            'range': 1,
            'icon': 'hammer',
            'color': (255, 100, 50),
        },
        'whirlwind': {
            'name': 'Torbellino',
            'description': 'Ataque en área a todas las unidades adyacentes',
            'ap_cost': 5,
            'damage_mult': 0.8,
            'range': 1,
            'aoe': True,
            'icon': 'spin',
            'color': (100, 200, 255),
        },
        'snipe': {
            'name': 'Disparo Preciso',
            'description': 'Ataque a larga distancia con alta precisión',
            'ap_cost': 4,
            'damage_mult': 1.5,
            'range': 4,
            'icon': 'crosshair',
            'color': (255, 255, 100),
        },
        'heal': {
            'name': 'Autocuración',
            'description': 'Recupera salud propia',
            'ap_cost': 3,
            'heal_amount': 30,
            'icon': 'plus',
            'color': (100, 255, 100),
        },
        'shield_bash': {
            'name': 'Golpe de Escudo',
            'description': 'Ataque que stunea al enemigo',
            'ap_cost': 3,
            'damage_mult': 0.7,
            'stun': True,
            'icon': 'shield',
            'color': (100, 100, 255),
        },
        'berserk': {
            'name': 'Furia',
            'description': 'Aumenta daño pero reduce defensa por 2 turnos',
            'ap_cost': 3,
            'buff': 'berserk',
            'icon': 'flame',
            'color': (255, 50, 50),
        },
        'teleport': {
            'name': 'Teletransporte',
            'description': 'Movimiento instantáneo a cualquier casilla',
            'ap_cost': 4,
            'teleport': True,
            'icon': 'portal',
            'color': (200, 100, 255),
        },
    }
    
    @classmethod
    def get_power(cls, power_id):
        return cls.POWERS.get(power_id, None)
    
    @classmethod
    def get_available_powers(cls, hero_level=1):
        """Retorna poderes disponibles según nivel."""
        available = ['slash', 'power_strike']
        if hero_level >= 2:
            available.append('shield_bash')
        if hero_level >= 3:
            available.append('heal')
        if hero_level >= 4:
            available.append('whirlwind')
        if hero_level >= 5:
            available.append('snipe')
        if hero_level >= 6:
            available.append('berserk')
        if hero_level >= 7:
            available.append('teleport')
        return {k: cls.POWERS[k] for k in available}


class HeroRenderer:
    """
    Renderizador geométrico avanzado para el héroe.
    Incluye 25+ figuras geométricas combinables.
    """
    
    def __init__(self):
        self.animation_time = 0
        self.breathing_offset = 0
        self.glow_phase = 0
        
        # Paleta de colores personalizable
        self.colors = {
            'primary': (80, 120, 200),      # Azul principal
            'secondary': (200, 180, 100),   # Dorado secundario
            'accent': (255, 100, 100),      # Rojo acento
            'metal': (180, 180, 190),       # Metal plateado
            'dark': (40, 40, 60),           # Sombra oscura
            'glow': (100, 150, 255, 150),   # Brillo
        }
        
        # Partes del cuerpo (figuras geométricas)
        self.body_parts = {
            'core': True,           # Núcleo hexagonal
            'armor_chest': True,    # Pecho con armadura
            'armor_shoulders': True,# Hombreras
            'helmet': True,         # Casco
            'visor': True,          # Visor del casco
            'cape': True,           # Capa
            'weapon_main': True,    # Arma principal
            'weapon_offhand': True, # Arma secundaria/escudo
            'energy_core': True,    # Núcleo de energía brillante
            'runes': True,          # Runas flotantes
            'particles': True,      # Partículas de aura
            'halo': False,          # Halo (modo especial)
            'wings': False,         # Alas (modo especial)
        }
    
    def draw(self, screen, x, y, scale=1.0, anim_time=0, selected=False):
        """
        Dibuja el héroe con todas las figuras geométricas.
        """
        self.animation_time = anim_time
        self.breathing_offset = math.sin(anim_time * 2) * 3
        self.glow_phase = (math.sin(anim_time * 3) + 1) / 2
        
        base_x, base_y = int(x), int(y + self.breathing_offset)
        s = scale
        
        # 1. SOMBRA (Elipse)
        if self.body_parts['particles']:
            self._draw_shadow(screen, base_x, base_y + 35 * s, 25 * s, 10 * s)
        
        # 2. CAPA (Polígono triangular curvo)
        if self.body_parts['cape']:
            self._draw_cape(screen, base_x, base_y, s)
        
        # 3. HALO/AURA (Círculos concéntricos)
        if self.body_parts['halo']:
            self._draw_halo(screen, base_x, base_y - 45 * s, 30 * s)
        
        # 4. ALAS (Curvas de Bézier simuladas con polígonos)
        if self.body_parts['wings']:
            self._draw_wings(screen, base_x, base_y - 20 * s, s)
        
        # 5. NÚCLEO - Hexágono principal
        if self.body_parts['core']:
            self._draw_hexagon_filled(
                screen, base_x, base_y, 20 * s,
                self.colors['primary'], self.colors['dark']
            )
        
        # 6. ARMADURA DE PECHO (Rectángulos redondeados + Triángulos)
        if self.body_parts['armor_chest']:
            self._draw_chest_armor(screen, base_x, base_y - 5 * s, s)
        
        # 7. HOMBRERAS (Círculos + Rectángulos)
        if self.body_parts['armor_shoulders']:
            self._draw_shoulders(screen, base_x, base_y - 15 * s, s)
        
        # 8. CASCO (Forma compleja: Hexágono + Círculo + Rectángulos)
        if self.body_parts['helmet']:
            self._draw_helmet(screen, base_x, base_y - 25 * s, s)
        
        # 9. VISOR (Elipse + Líneas)
        if self.body_parts['visor']:
            self._draw_visor(screen, base_x, base_y - 28 * s, s)
        
        # 10. NÚCLEO DE ENERGÍA (Círculo brillante + Glow)
        if self.body_parts['energy_core']:
            self._draw_energy_core(screen, base_x, base_y, 8 * s)
        
        # 11. ARMA PRINCIPAL (Rectángulos + Círculos + Triángulos)
        if self.body_parts['weapon_main']:
            self._draw_main_weapon(screen, base_x + 25 * s, base_y - 10 * s, s)
        
        # 12. ESCUDO/ARMA SECUNDARIA (Forma de escudo geométrica)
        if self.body_parts['weapon_offhand']:
            self._draw_offhand(screen, base_x - 25 * s, base_y - 5 * s, s)
        
        # 13. RUNAS FLOTANTES (Pequeños polígonos orbitando)
        if self.body_parts['runes']:
            self._draw_runes(screen, base_x, base_y - 35 * s, 35 * s, anim_time)
        
        # 14. PARTÍCULAS DE AURA (Círculos pequeños flotantes)
        if self.body_parts['particles']:
            self._draw_aura_particles(screen, base_x, base_y, s, anim_time)
        
        # 15. SELECCIÓN (Brillo exterior si está seleccionado)
        if selected:
            self._draw_selection_glow(screen, base_x, base_y, 45 * s)
    
    # === MÉTODOS DE DIBUJO DE FIGURAS ===
    
    def _draw_shadow(self, screen, x, y, w, h):
        """Figura 1: Sombra elíptica."""
        shadow_surf = pygame.Surface((int(w*2), int(h*2)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (0, 0, int(w*2), int(h*2)))
        screen.blit(shadow_surf, (int(x - w), int(y - h)))
    
    def _draw_cape(self, screen, x, y, s):
        """Figura 2: Capa triangular con curvas."""
        points = [
            (x - 20 * s, y - 10 * s),
            (x + 20 * s, y - 10 * s),
            (x + 25 * s, y + 40 * s),
            (x, y + 50 * s),
            (x - 25 * s, y + 40 * s),
        ]
        pygame.draw.polygon(screen, (120, 40, 40), points)
        pygame.draw.polygon(screen, (80, 30, 30), points, 2)
    
    def _draw_halo(self, screen, x, y, r):
        """Figura 3: Halo circular."""
        glow = int(50 + self.glow_phase * 50)
        pygame.draw.circle(screen, (255, 215, 0, glow), (int(x), int(y)), int(r), 3)
        pygame.draw.circle(screen, (255, 255, 200, 100), (int(x), int(y)), int(r * 0.7), 2)
    
    def _draw_wings(self, screen, x, y, s):
        """Figura 4: Alas compuestas de múltiples triángulos."""
        # Ala izquierda
        left_wing = [
            (x - 15 * s, y),
            (x - 45 * s, y - 25 * s),
            (x - 50 * s, y - 5 * s),
            (x - 40 * s, y + 10 * s),
            (x - 20 * s, y + 5 * s),
        ]
        pygame.draw.polygon(screen, (200, 200, 220), left_wing)
        pygame.draw.polygon(screen, (150, 150, 170), left_wing, 2)
        
        # Ala derecha
        right_wing = [(x + (xi - x) * -1 if xi < x else x + (xi - x), yi) for xi, yi in left_wing]
        pygame.draw.polygon(screen, (200, 200, 220), right_wing)
        pygame.draw.polygon(screen, (150, 150, 170), right_wing, 2)
    
    def _draw_hexagon_filled(self, screen, x, y, r, fill_color, border_color):
        """Figura 5: Hexágono base (cuerpo)."""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, fill_color, points)
        pygame.draw.polygon(screen, border_color, points, 2)
    
    def _draw_chest_armor(self, screen, x, y, s):
        """Figura 6: Armadura de pecho (rectángulos + triángulo)."""
        # Placa central
        rect = pygame.Rect(x - 12 * s, y - 10 * s, 24 * s, 25 * s)
        pygame.draw.rect(screen, self.colors['metal'], rect, border_radius=3)
        pygame.draw.rect(screen, self.colors['dark'], rect, 2, border_radius=3)
        
        # Detalle central - triángulo
        tri_points = [
            (x, y - 5 * s),
            (x - 5 * s, y + 10 * s),
            (x + 5 * s, y + 10 * s),
        ]
        pygame.draw.polygon(screen, self.colors['secondary'], tri_points)
    
    def _draw_shoulders(self, screen, x, y, s):
        """Figura 7: Hombreras (círculos con detalles)."""
        # Hombro izquierdo
        pygame.draw.circle(screen, self.colors['metal'], (int(x - 22 * s), int(y)), int(10 * s))
        pygame.draw.circle(screen, self.colors['dark'], (int(x - 22 * s), int(y)), int(10 * s), 2)
        pygame.draw.circle(screen, self.colors['accent'], (int(x - 22 * s), int(y)), int(5 * s))
        
        # Hombro derecho
        pygame.draw.circle(screen, self.colors['metal'], (int(x + 22 * s), int(y)), int(10 * s))
        pygame.draw.circle(screen, self.colors['dark'], (int(x + 22 * s), int(y)), int(10 * s), 2)
        pygame.draw.circle(screen, self.colors['accent'], (int(x + 22 * s), int(y)), int(5 * s))
    
    def _draw_helmet(self, screen, x, y, s):
        """Figura 8: Casco (hexágono superior + rectángulos)."""
        # Base del casco - hexágono más pequeño
        points = []
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 2
            px = x + 15 * s * math.cos(angle)
            py = y + 12 * s * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(screen, self.colors['metal'], points)
        pygame.draw.polygon(screen, self.colors['dark'], points, 2)
        
        # Cresta
        crest_points = [
            (x, y - 18 * s),
            (x - 8 * s, y - 8 * s),
            (x + 8 * s, y - 8 * s),
        ]
        pygame.draw.polygon(screen, self.colors['secondary'], crest_points)
    
    def _draw_visor(self, screen, x, y, s):
        """Figura 9: Visor (elipse + líneas)."""
        # Visor oscuro
        rect = pygame.Rect(x - 10 * s, y - 3 * s, 20 * s, 8 * s)
        pygame.draw.ellipse(screen, (20, 30, 50), rect)
        pygame.draw.ellipse(screen, (100, 150, 255), rect, 1)
        
        # Brillo del visor
        glow_x = x + 3 * s * math.sin(self.animation_time * 2)
        pygame.draw.ellipse(screen, (150, 200, 255), 
                           (glow_x - 3 * s, y - 1 * s, 6 * s, 3 * s))
    
    def _draw_energy_core(self, screen, x, y, r):
        """Figura 10: Núcleo de energía (círculo con glow)."""
        # Glow exterior
        for i in range(3, 0, -1):
            alpha = int(50 * self.glow_phase / i)
            pygame.draw.circle(screen, (100, 200, 255, alpha), 
                             (int(x), int(y)), int(r + i * 3))
        
        # Núcleo brillante
        pygame.draw.circle(screen, (200, 240, 255), (int(x), int(y)), int(r))
        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), int(r * 0.5))
    
    def _draw_main_weapon(self, screen, x, y, s):
        """Figura 11: Arma principal (rectángulos + triángulos)."""
        # Mango
        handle = pygame.Rect(x - 3 * s, y, 6 * s, 20 * s)
        pygame.draw.rect(screen, (101, 67, 33), handle)
        
        # Guardia
        guard = pygame.Rect(x - 8 * s, y - 5 * s, 16 * s, 4 * s)
        pygame.draw.rect(screen, self.colors['metal'], guard)
        
        # Hoja - espada grande
        blade_points = [
            (x, y - 35 * s),
            (x - 6 * s, y - 5 * s),
            (x + 6 * s, y - 5 * s),
        ]
        pygame.draw.polygon(screen, (220, 220, 230), blade_points)
        pygame.draw.polygon(screen, (150, 150, 160), blade_points, 2)
        
        # Brillo de la hoja
        shine_y = y - 20 * s + 5 * s * math.sin(self.animation_time * 3)
        pygame.draw.line(screen, (255, 255, 255), 
                        (x - 2 * s, shine_y), (x - 2 * s, shine_y - 8 * s), 2)
    
    def _draw_offhand(self, screen, x, y, s):
        """Figura 12: Escudo (forma geométrica compuesta)."""
        # Forma de escudo - hexágono alargado
        points = [
            (x, y - 20 * s),
            (x + 12 * s, y - 10 * s),
            (x + 12 * s, y + 10 * s),
            (x, y + 25 * s),
            (x - 12 * s, y + 10 * s),
            (x - 12 * s, y - 10 * s),
        ]
        pygame.draw.polygon(screen, self.colors['metal'], points)
        pygame.draw.polygon(screen, self.colors['dark'], points, 3)
        
        # Emblema central
        pygame.draw.circle(screen, self.colors['primary'], (int(x), int(y + 5 * s)), int(6 * s))
        pygame.draw.circle(screen, self.colors['secondary'], (int(x), int(y + 5 * s)), int(3 * s))
    
    def _draw_runes(self, screen, x, y, radius, anim_time):
        """Figura 13-17: Runas flotantes (5 polígonos pequeños orbitando)."""
        for i in range(5):
            angle = anim_time * 0.5 + (2 * math.pi / 5) * i
            rx = x + radius * math.cos(angle)
            ry = y + radius * math.sin(angle) * 0.3
            
            # Rune shape - pequeño rombo
            size = 3 + math.sin(anim_time * 3 + i) * 1
            rune_points = [
                (rx, ry - size),
                (rx + size, ry),
                (rx, ry + size),
                (rx - size, ry),
            ]
            color = (255, 215, 0) if i % 2 == 0 else (100, 200, 255)
            pygame.draw.polygon(screen, color, rune_points)
    
    def _draw_aura_particles(self, screen, x, y, s, anim_time):
        """Figura 18-25: Partículas de aura (8 círculos flotantes)."""
        for i in range(8):
            angle = anim_time * 0.3 + (2 * math.pi / 8) * i
            dist = 30 + 5 * math.sin(anim_time * 2 + i)
            px = x + dist * s * math.cos(angle)
            py = y + dist * s * math.sin(angle) * 0.5 - 10
            
            size = 2 + math.sin(anim_time * 4 + i) * 1
            alpha = int(100 + 50 * math.sin(anim_time * 3 + i))
            
            particle_surf = pygame.Surface((int(size*4), int(size*4)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (100, 200, 255, alpha), 
                            (int(size*2), int(size*2)), int(size))
            screen.blit(particle_surf, (int(px - size*2), int(py - size*2)))
    
    def _draw_selection_glow(self, screen, x, y, r):
        """Figura extra: Brillo de selección."""
        pulse = 1 + 0.1 * math.sin(self.animation_time * 5)
        for i in range(2, 0, -1):
            pygame.draw.circle(screen, (255, 215, 0, 80), 
                             (int(x), int(y)), int(r * pulse + i * 5), 2)


class Hero:
    """
    Héroe principal del jugador.
    Única unidad que consume Puntos de Acción.
    """
    
    def __init__(self, name="Comandante"):
        self.name = name
        self.unit_type = "hero"
        self.owner = "player"
        self.is_hero = True  # Flag importante
        
        # Stats base
        self.max_health = 150
        self.health = self.max_health
        self.attack = 40
        self.defense = 10
        self.speed = 5
        self.range = 2
        
        # Sistema de AP (único en el héroe)
        self.action_points = ActionPointsSystem(max_ap=10, recovery_per_turn=6)
        
        # Posición
        self.visual_x = 0
        self.visual_y = 0
        self.target_x = 0
        self.target_y = 0
        self.is_moving = False
        self.animation_time = 0
        self.bounce_offset = 0
        
        # Estado
        self.has_moved = False
        self.is_defending = False
        self.defense_multiplier = 1.0
        self.active_buffs = []
        
        # Poderes
        self.level = 1
        self.available_powers = HeroPowers.get_available_powers(self.level)
        self.selected_power = 'slash'
        
        # Renderizador geométrico
        self.renderer = HeroRenderer()
    
    def set_position(self, x, y):
        """Establece posición visual."""
        self.visual_x = x
        self.visual_y = y
        self.target_x = x
        self.target_y = y
    
    def move_to(self, x, y):
        """
        Inicia movimiento hacia coordenadas.
        NOTA: El héroe puede moverse 1 vez gratis por turno.
        """
        self.target_x = x
        self.target_y = y
        self.is_moving = True
        self.animation_time = 0
        self.has_moved = True  # Marcar que ya se movió este turno
    
    def update(self, dt, grass_system=None):
        """Actualiza animaciones y estado."""
        if self.is_moving:
            dx = self.target_x - self.visual_x
            dy = self.target_y - self.visual_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 2:
                self.visual_x = self.target_x
                self.visual_y = self.target_y
                self.is_moving = False
                self.bounce_offset = 0
            else:
                speed = 300 * dt
                self.visual_x += (dx / distance) * min(speed, distance)
                self.visual_y += (dy / distance) * min(speed, distance)
                
                self.animation_time += dt * 12
                self.bounce_offset = abs(math.sin(self.animation_time)) * -8
                
                # Efecto de pasto
                if grass_system:
                    grass_system.add_footstep_wave(self.visual_x, self.visual_y + 10)
        else:
            self.animation_time += dt * 2
            self.bounce_offset = math.sin(self.animation_time) * 1.5
        
        # Actualizar buffs
        self._update_buffs(dt)
    
    def _update_buffs(self, dt):
        """Actualiza buffs activos."""
        for buff in self.active_buffs[:]:
            buff['duration'] -= dt
            if buff['duration'] <= 0:
                self._remove_buff(buff)
                self.active_buffs.remove(buff)
    
    def _remove_buff(self, buff):
        """Remueve efectos de un buff."""
        if buff['type'] == 'berserk':
            # Revertir furia
            self.attack = int(self.attack / 1.5)
            self.defense_multiplier = 1.0
    
    def use_power(self, power_id, target=None) -> dict:
        """
        Usa un poder consumiendo AP.
        
        Returns:
            Dict con resultado: {'success': bool, 'message': str, 'ap_spent': int}
        """
        if power_id not in self.available_powers:
            return {'success': False, 'message': 'Poder no disponible', 'ap_spent': 0}
        
        power = self.available_powers[power_id]
        ap_cost = power['ap_cost']
        
        # Verificar AP
        if not self.action_points.can_afford(ap_cost):
            return {'success': False, 'message': 'Sin AP suficientes', 'ap_spent': 0}
        
        # Gastar AP
        self.action_points.spend(ap_cost)
        
        # Ejecutar poder
        result = self._execute_power_effect(power_id, power, target)
        result['ap_spent'] = ap_cost
        
        return result
    
    def _execute_power_effect(self, power_id, power, target):
        """Ejecuta el efecto específico del poder."""
        if power_id == 'heal':
            heal = power.get('heal_amount', 30)
            self.health = min(self.max_health, self.health + heal)
            return {'success': True, 'message': f'Curado +{heal} HP', 'damage': 0}
        
        elif power_id == 'berserk':
            self.attack = int(self.attack * 1.5)
            self.defense_multiplier = 1.3
            self.active_buffs.append({'type': 'berserk', 'duration': 10.0})
            return {'success': True, 'message': '¡Furia activada!', 'damage': 0}
        
        elif power_id == 'teleport':
            if target:
                self.set_position(target.x, target.y)
            return {'success': True, 'message': 'Teletransporte!', 'damage': 0}
        
        elif 'damage_mult' in power:
            # Poderes de daño
            if target and hasattr(target, 'take_damage'):
                damage = int(self.attack * power['damage_mult'])
                actual = target.take_damage(damage)
                return {'success': True, 'message': f'Daño: {actual}', 'damage': actual}
            return {'success': False, 'message': 'Sin objetivo', 'damage': 0}
        
        return {'success': False, 'message': 'Efecto no implementado', 'damage': 0}
    
    def can_use_power(self, power_id) -> bool:
        """Verifica si puede usar un poder (tiene AP)."""
        if power_id not in self.available_powers:
            return False
        power = self.available_powers[power_id]
        return self.action_points.can_afford(power['ap_cost'])
    
    def set_defending(self, defending, multiplier=0.5):
        """Establece estado defensivo."""
        self.is_defending = defending
        self.defense_multiplier = multiplier if defending else 1.0
    
    def take_damage(self, damage):
        """Recibe daño aplicando defensa."""
        if self.is_defending:
            damage = int(damage * 0.5)
        
        # Aplicar defensa base
        damage = max(1, damage - self.defense // 5)
        
        self.health -= damage
        return damage
    
    def is_alive(self):
        """Verifica si está vivo."""
        return self.health > 0
    
    def get_attack_range_pixels(self):
        """Retorna rango de ataque en píxeles."""
        from config.constants import HEX_WIDTH
        return self.range * HEX_WIDTH * 0.9
    
    def draw(self, screen, x, y, selected=False):
        """Dibuja el héroe con renderizado geométrico avanzado."""
        base_x = int(self.visual_x if self.is_moving else x)
        base_y = int(self.visual_y + self.bounce_offset if self.is_moving else y + self.bounce_offset)
        
        self.renderer.draw(screen, base_x, base_y, scale=0.6, 
                          anim_time=self.animation_time, selected=selected)
        
        # Barra de vida
        self._draw_health_bar(screen, base_x, base_y - 45)
        
        # Indicador de AP (solo para héroe)
        self._draw_ap_bar(screen, base_x, base_y - 55)
        
        # Indicador de unidad activa
        if self.can_act():
            pygame.draw.circle(screen, (255, 215, 0), (base_x, base_y - 60), 5)
    
    def _draw_health_bar(self, screen, x, y):
        """Dibuja barra de vida."""
        bar_w, bar_h = 35, 5
        ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (50, 0, 0), (x - bar_w//2, y, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 255, 0), (x - bar_w//2, y, bar_w * ratio, bar_h))
        pygame.draw.rect(screen, (0, 0, 0), (x - bar_w//2, y, bar_w, bar_h), 1)
    
    def _draw_ap_bar(self, screen, x, y):
        """Dibuja barra de AP (pequeña, dorada)."""
        bar_w, bar_h = 25, 3
        ratio = self.action_points.current / self.action_points.maximum
        
        pygame.draw.rect(screen, (50, 50, 0), (x - bar_w//2, y, bar_w, bar_h))
        pygame.draw.rect(screen, (255, 215, 0), (x - bar_w//2, y, bar_w * ratio, bar_h))
        pygame.draw.rect(screen, (0, 0, 0), (x - bar_w//2, y, bar_w, bar_h), 1)
    
    def can_act(self):
        """Verifica si puede realizar acciones."""
        return self.is_alive() and not self.is_moving
    
    def end_turn(self):
        """Termina turno del héroe."""
        self.has_moved = False
        self.is_defending = False
        self.defense_multiplier = 1.0
