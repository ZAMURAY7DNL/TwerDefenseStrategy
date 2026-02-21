"""
Sistema de Turnos (Turn System)
==============================
Sistema de turnos uno a uno como Day R Survival.
- Cada unidad actúa individualmente
- No hay fase de "combate" donde todos atacan al mismo tiempo
- El jugador selecciona acciones para cada unidad UNA A UNA
- El enemigo también actúa uno a uno
"""
from config.constants import *


class TurnSystem:
    """
    Sistema de turnos individuales - como Day R Survival.
    Cada unidad actúa por separado, no hay fase de combate colectivo.
    """
    
    def __init__(self):
        # Estado del turno
        self.phase = PHASE_PLAYER_TURN  # player_turn, enemy_turn
        self.turn_number = 1
        
        # Índice de la unidad activa (para ejecución uno a uno)
        self.player_unit_index = 0
        self.enemy_unit_index = 0
        
        # Unidad que está actuando actualmente
        self.active_unit = None
        self.active_unit_type = None  # "player" o "enemy"
        
        # Cola de acciones pendientes
        self.action_queue = []
        
        # Flags de estado
        self.waiting_for_action = False  # Esperando que el jugador seleccione acción
        self.unit_acted_this_turn = {}   # track which units have acted
    
    def start_player_turn(self):
        """Inicia el turno del jugador."""
        self.phase = PHASE_PLAYER_TURN
        self.player_unit_index = 0
        self.unit_acted_this_turn = {}
        self._prepare_next_unit()
    
    def start_enemy_turn(self):
        """Inicia el turno del enemigo."""
        self.phase = PHASE_ENEMY_TURN
        self.enemy_unit_index = 0
        self._prepare_next_enemy()
    
    def _prepare_next_unit(self):
        """Prepara la siguiente unidad del jugador para actuar."""
        # Por ahora, simplificado: cualquier unidad puede actuar
        self.waiting_for_action = True
        self.active_unit_type = "player"
    
    def _prepare_next_enemy(self):
        """Prepara la siguiente unidad enemiga para actuar."""
        self.waiting_for_action = True
        self.active_unit_type = "enemy"
    
    def has_units_to_act(self, unit_list, unit_index):
        """Verifica si hay unidades que pueden actuar."""
        return unit_index < len(unit_list)
    
    def get_current_unit(self, player_units, enemy_units):
        """Retorna la unidad que debe actuar ahora."""
        if self.phase == PHASE_PLAYER_TURN:
            if self.player_unit_index < len(player_units):
                return player_units[self.player_unit_index]
        elif self.phase == PHASE_ENEMY_TURN:
            if self.enemy_unit_index < len(enemy_units):
                return enemy_units[self.enemy_unit_index]
        return None
    
    def unit_finished_action(self):
        """Marca la unidad actual como terminada y pasa a la siguiente."""
        if self.phase == PHASE_PLAYER_TURN:
            self.player_unit_index += 1
            if self.player_unit_index >= len(self.player_units_list):
                # Todas las unidades del jugador han actuado
                self.waiting_for_action = False
        elif self.phase == PHASE_ENEMY_TURN:
            self.enemy_unit_index += 1
            if self.enemy_unit_index >= len(self.enemy_units_list):
                # Todas las unidades enemigas han actuado
                self.waiting_for_action = False
    
    def set_unit_lists(self, player_units, enemy_units):
        """Establece las listas de unidades para el turno."""
        self.player_units_list = player_units
        self.enemy_units_list = enemy_units
    
    def all_player_units_acted(self):
        """Verifica si todas las unidades del jugador han actuado."""
        return self.player_unit_index >= len(self.player_units_list)
    
    def all_enemy_units_acted(self):
        """Verifica si todas las unidades enemigas han actuado."""
        return self.enemy_unit_index >= len(self.enemy_units_list)
    
    def get_status_text(self):
        """Retorna texto de estado para UI."""
        if self.phase == PHASE_PLAYER_TURN:
            if self.waiting_for_action:
                return f"Turno {self.turn_number} - TU TURNO"
            else:
                return f"Turno {self.turn_number} - ESPERANDO ENEMIGO"
        elif self.phase == PHASE_ENEMY_TURN:
            return f"Turno {self.turn_number} - TURNO ENEMIGO"
        return ""
    
    def is_player_turn(self):
        return self.phase == PHASE_PLAYER_TURN
    
    def is_enemy_turn(self):
        return self.phase == PHASE_ENEMY_TURN
    
    def reset(self):
        """Reinicia el sistema de turnos."""
        self.phase = PHASE_PLAYER_TURN
        self.turn_number = 1
        self.player_unit_index = 0
        self.enemy_unit_index = 0
        self.waiting_for_action = False
        self.unit_acted_this_turn = {}
