"""
Sistema de Input - Manejo de clics y teclas
"""


class InputSystem:
    """Sistema de manejo de inputs"""
    
    def __init__(self):
        self.selected_tile = None
    
    def handle_keydown(self, event, game):
        """Maneja teclas presionadas"""
        from config.constants import PHASE_PLAYER_TURN, PHASE_VICTORY, PHASE_DEFEAT
        
        if event.key == 27:  # ESC
            if game.selected_tile:
                game.selected_tile.selected = False
                game.selected_tile = None
                game.update_valid_moves()
        
        elif event.key == 32:  # ESPACIO
            if game.phase == PHASE_PLAYER_TURN:
                game._end_player_turn()
        
        elif event.key == 114:  # R
            if game.phase in [PHASE_VICTORY, PHASE_DEFEAT]:
                game.reset_game()
    
    def handle_click(self, mouse_pos, game):
        """Maneja clics del mouse"""
        from config.constants import PHASE_PLAYER_TURN
        
        if game.phase != PHASE_PLAYER_TURN:
            return
        
        # Buscar tile clickeado
        tile = game.find_tile(mouse_pos)
        if not tile:
            return
        
        # Si no hay unidad seleccionada, intentar seleccionar
        if not game.selected_tile:
            if tile.unit and tile.unit.owner == "player" and not tile.unit.has_moved:
                self._select_unit(tile, game)
            return
        
        # Ya hay una unidad seleccionada
        current = game.selected_tile
        
        # Mover a tile válido
        if tile.valid_move and tile.is_empty():
            self._move_unit(current, tile, game)
            return
        
        # Click en el mismo tile - deseleccionar
        if current == tile:
            self._deselect_unit(game)
            return
        
        # Cambiar selección a otra unidad propia
        if tile.unit and tile.unit.owner == "player" and not tile.unit.has_moved:
            self._deselect_unit(game)
            self._select_unit(tile, game)
            return
        
        # Cualquier otro click - deseleccionar
        self._deselect_unit(game)
    
    def _select_unit(self, tile, game):
        """Selecciona una unidad"""
        game.selected_tile = tile
        tile.selected = True
        game.update_valid_moves()
        
        # Análisis del oráculo
        if hasattr(game, 'oracle'):
            game.oracle.analyze_battlefield(
                tile.unit, tile, game.grid,
                game.player_units, game.enemy_units
            )
    
    def _deselect_unit(self, game):
        """Deselecciona la unidad actual"""
        if game.selected_tile:
            game.selected_tile.selected = False
        
        game.selected_tile = None
        game.update_valid_moves()
        
        # Limpiar recomendación del oráculo
        if hasattr(game, 'oracle'):
            game.oracle.clear_recommendation(game.grid)
    
    def _move_unit(self, from_tile, to_tile, game):
        """Mueve la unidad"""
        # Efectos de partículas
        game.particles.spawn_dust(from_tile.x, from_tile.y)
        
        # Mover unidad
        unit = from_tile.unit
        to_tile.unit = unit
        from_tile.unit = None
        unit.move_to(to_tile.x, to_tile.y)
        
        game.particles.spawn_dust(to_tile.x, to_tile.y)
        
        # Limpiar selección
        from_tile.selected = False
        game.selected_tile = None
        game.oracle.clear_recommendation(game.grid)
        game.update_valid_moves()
    
    def update_buttons(self, buttons, mouse_pos):
        """Actualiza estado de botones"""
        for btn in buttons:
            btn.update(mouse_pos)
    
    def handle_button_click(self, buttons, mouse_pos, game):
        """Maneja clics en botones"""
        for btn in buttons:
            if btn.handle_click(mouse_pos):
                return True
        return False
