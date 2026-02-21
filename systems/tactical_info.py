"""
Sistema de Información Táctica (IT)
====================================
La Torre de Comunicaciones acumula puntos de IT cada turno para el jugador.
El jugador gasta IT para ejecutar ataques especiales y acciones tácticas.
Las tropas actúan libremente sin gastar IT.

Arquitectura escalable: soporta bonificadores futuros (ej. clase Rogue League)
que amplíen la tasa de generación de IT por turno.
"""
import pygame
import math


# ─────────────────────────────────────────────────────────────────────────────
#  Constantes del sistema IT
# ─────────────────────────────────────────────────────────────────────────────
IT_MAX_BASE        = 200    # Capacidad base de la barra de IT
IT_REGEN_PER_TURN  = 30     # IT generada por turno (base, sin bonificadores)
IT_COLOR_FILL      = (0, 200, 255)    # Azul cian — color de la barra IT
IT_COLOR_BG        = (10, 40, 60)     # Fondo oscuro de la barra
IT_COLOR_BORDER    = (0, 150, 220)    # Borde de la barra
IT_COLOR_LABEL     = (180, 240, 255)  # Color del texto IT


# ─────────────────────────────────────────────────────────────────────────────
#  Costos de ataques especiales (IT)
# ─────────────────────────────────────────────────────────────────────────────
IT_COST_AIRSTRIKE   = 80   # Ataque aéreo en área (3 hexágonos)
IT_COST_SNIPE       = 50   # Disparo de precisión (ignora defensa)
IT_COST_SHIELD      = 40   # Escudo táctico (reduce daño recibido 1 turno)
IT_COST_RECON       = 20   # Reconocimiento (revela stats enemigas)
IT_COST_RALLY       = 60   # Reagrupamiento (todas las tropas +20% ataque 1 turno)


class TacticalInfoSystem:
    """
    Gestiona la barra de Información Táctica (IT) del jugador.
    
    - La Torre de Comunicaciones genera IT cada turno.
    - El jugador gasta IT en acciones especiales.
    - Las tropas NO gastan IT; actúan libremente.
    - Soporta bonificadores externos (bonifier_multiplier).
    """

    def __init__(self):
        self.current_it    = 0          # IT actual
        self.max_it        = IT_MAX_BASE
        self.regen_base    = IT_REGEN_PER_TURN
        
        # Lista de bonificadores activos: cada uno es un dict con
        # {"name": str, "multiplier": float, "source": str}
        # Ejemplo futuro: {"name": "Rogue League", "multiplier": 1.5, "source": "class"}
        self._bonifiers: list = []
        
        # Historial de acciones especiales usadas (para UI/log)
        self.action_log: list = []

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def regen_per_turn(self) -> float:
        """IT generada por turno, aplicando todos los bonificadores activos."""
        total_multiplier = 1.0
        for b in self._bonifiers:
            total_multiplier *= b.get("multiplier", 1.0)
        return self.regen_base * total_multiplier

    @property
    def fill_ratio(self) -> float:
        """Proporción de llenado de la barra (0.0 – 1.0)."""
        return min(self.current_it / self.max_it, 1.0) if self.max_it > 0 else 0.0

    # ── Operaciones principales ───────────────────────────────────────────────

    def on_turn_start(self):
        """Llamar al inicio de cada turno del jugador para regenerar IT."""
        gained = self.regen_per_turn
        self.current_it = min(self.current_it + gained, self.max_it)

    def can_spend(self, cost: float) -> bool:
        """Devuelve True si hay suficiente IT para gastar."""
        return self.current_it >= cost

    def spend(self, cost: float, action_name: str = "") -> bool:
        """
        Gasta IT si hay suficiente.
        Devuelve True si la acción fue exitosa, False si no hay IT suficiente.
        """
        if not self.can_spend(cost):
            return False
        self.current_it -= cost
        if action_name:
            self.action_log.append(action_name)
        return True

    def add_it(self, amount: float):
        """Añade IT directamente (para eventos especiales, recompensas, etc.)."""
        self.current_it = min(self.current_it + amount, self.max_it)

    def reset(self):
        """Reinicia el sistema al comenzar una nueva partida."""
        self.current_it = 0
        self._bonifiers.clear()
        self.action_log.clear()

    # ── Gestión de bonificadores ──────────────────────────────────────────────

    def add_bonifier(self, name: str, multiplier: float, source: str = ""):
        """
        Registra un bonificador de generación de IT.
        
        Ejemplo de uso futuro:
            ti_system.add_bonifier("Rogue League", 1.5, "class")
        """
        self._bonifiers.append({
            "name": name,
            "multiplier": multiplier,
            "source": source
        })

    def remove_bonifier(self, name: str):
        """Elimina un bonificador por nombre."""
        self._bonifiers = [b for b in self._bonifiers if b["name"] != name]

    def get_bonifiers(self) -> list:
        """Devuelve la lista de bonificadores activos (solo lectura)."""
        return list(self._bonifiers)

    # ── Renderizado ───────────────────────────────────────────────────────────

    def draw(self, screen, font, x: int, y: int, width: int = 180, height: int = 18):
        """
        Dibuja la barra de IT en pantalla.
        
        Args:
            screen: superficie pygame
            font:   fuente pygame para el texto
            x, y:   posición superior izquierda
            width:  ancho de la barra
            height: alto de la barra
        """
        # Fondo
        pygame.draw.rect(screen, IT_COLOR_BG, (x, y, width, height), border_radius=4)

        # Relleno proporcional
        fill_w = int(width * self.fill_ratio)
        if fill_w > 0:
            # Gradiente simple: más brillante en el extremo derecho
            pygame.draw.rect(screen, IT_COLOR_FILL,
                             (x, y, fill_w, height), border_radius=4)

        # Borde
        pygame.draw.rect(screen, IT_COLOR_BORDER,
                         (x, y, width, height), 2, border_radius=4)

        # Texto: "IT  123 / 200"
        label = font.render(
            f"IT  {int(self.current_it)} / {int(self.max_it)}", True, IT_COLOR_LABEL
        )
        screen.blit(label, (x + width + 8, y + height // 2 - label.get_height() // 2))

        # Indicador de regeneración por turno
        regen_text = font.render(
            f"+{int(self.regen_per_turn)}/turno", True, (100, 200, 255)
        )
        screen.blit(regen_text, (x, y + height + 3))


# ─────────────────────────────────────────────────────────────────────────────
#  Torre de Comunicaciones
# ─────────────────────────────────────────────────────────────────────────────

class CommunicationTower:
    """
    Torre de Comunicaciones — fuente de IT del jugador.
    
    Está posicionada fuera del campo de batalla (no ocupa un hexágono).
    Cada turno del jugador genera IT y la transfiere al TacticalInfoSystem.
    
    Puede ser destruida por el enemigo (si se implementa en el futuro),
    reduciendo o eliminando la generación de IT.
    """

    def __init__(self, ti_system: TacticalInfoSystem):
        self.ti_system   = ti_system
        self.is_active   = True       # Si está destruida, no genera IT
        self.max_health = 1000
        self.health = 1000
        self._anim_time  = 0.0
        self.x           = 0
        self.y           = 0

    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y

    def on_turn_start(self):
        """Genera IT al inicio del turno del jugador."""
        if self.is_active:
            self.ti_system.on_turn_start()

    def take_damage(self, damage: float):
        self.health -= damage
        if self.health <= 0:
            health = 1000
            self.is_active = False

    def is_alive(self) -> bool:
        return self.health > 0

    def update(self, dt: float):
        self._anim_time += dt

    def draw(self, screen, font_small):
        """Dibuja la torre de comunicaciones en su posición (fuera del grid)."""
        if not self.is_alive():
            return

        x, y = self.x, self.y
        t = self._anim_time

        # Base de la torre
        pygame.draw.rect(screen, (40, 60, 80), (x - 14, y + 10, 28, 20), border_radius=3)
        pygame.draw.rect(screen, (60, 100, 130), (x - 14, y + 10, 28, 20), 2, border_radius=3)

        # Mástil
        pygame.draw.line(screen, (80, 140, 180), (x, y + 10), (x, y - 30), 3)

        # Antena pulsante
        pulse = abs(math.sin(t * 3)) * 6
        pygame.draw.line(screen, (0, 200, 255), (x, y - 30), (x - 12, y - 20), 2)
        pygame.draw.line(screen, (0, 200, 255), (x, y - 30), (x + 12, y - 20), 2)

        # Señal animada (círculos concéntricos)
        for i in range(1, 3):
            radius = int(10 + i * 8 + pulse)
            alpha_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            alpha = max(0, 120 - i * 40)
            pygame.draw.circle(alpha_surf, (0, 200, 255, alpha),
                               (radius, radius), radius, 1)
            screen.blit(alpha_surf, (x - radius, y - 30 - radius))

        # Etiqueta
        label = font_small.render("COM", True, (0, 200, 255))
        screen.blit(label, (x - label.get_width() // 2, y + 32))

        # Barra de salud (si está dañada)
        if self.health < self.max_health:
            bar_w = 28
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, (80, 0, 0), (x - bar_w // 2, y + 55, bar_w, 4))
            pygame.draw.rect(screen, (0, 200, 80),
                             (x - bar_w // 2, y + 55, int(bar_w * ratio), 4))
