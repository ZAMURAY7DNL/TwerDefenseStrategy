"""
Sistema de Menú de Acciones
===========================
Módulo modular para mostrar el menú de acciones cuando se selecciona una unidad.
Cada acción se ejecuta INMEDIATAMENTE al ser seleccionada.
"""
import pygame


class ActionMenuSystem:
    """
    Sistema de menú de acciones para unidades.
    Aparece a la izquierda cuando se selecciona una unidad.
    """
    
    def __init__(self):
        self.visible = False
        self.options = []
        self.selected_unit = None
        self.action_rects = []  # Para detectar clicks
    
    def show_for_unit(self, unit):
        """Muestra el menú para una unidad específica."""
        self.visible = True
        self.selected_unit = unit
        
        # Opciones según tipo de unidad
        if unit.unit_type == "berserker":
            self.options = [
                {"id": "move", "name": "Mover", "color": (40, 100, 40), "border": (100, 200, 100)},
                {"id": "charge", "name": "Carga", "color": (100, 40, 40), "border": (200, 100, 100)},
                {"id": "fury", "name": "Furia", "color": (100, 40, 40), "border": (200, 100, 100)},
            ]
        elif unit.unit_type == "assault":
            self.options = [
                {"id": "move", "name": "Mover", "color": (40, 100, 40), "border": (100, 200, 100)},
                {"id": "suppress", "name": "Suprimir", "color": (100, 40, 40), "border": (200, 100, 100)},
                {"id": "reinforce", "name": "Refuerzo", "color": (100, 40, 40), "border": (200, 100, 100)},
            ]
        elif unit.unit_type == "ranger":
            self.options = [
                {"id": "move", "name": "Mover", "color": (40, 100, 40), "border": (100, 200, 100)},
                {"id": "area", "name": "Disparo Área", "color": (100, 40, 40), "border": (200, 100, 100)},
                {"id": "trap", "name": "Trampa", "color": (100, 40, 40), "border": (200, 100, 100)},
            ]
        elif unit.unit_type == "sniper":
            self.options = [
                {"id": "move", "name": "Mover", "color": (40, 100, 40), "border": (100, 200, 100)},
                {"id": "long", "name": "Disparo Largo", "color": (100, 40, 40), "border": (200, 100, 100)},
                {"id": "mark", "name": "Marca", "color": (100, 40, 40), "border": (200, 100, 100)},
            ]
        else:
            self.options = [
                {"id": "move", "name": "Mover", "color": (40, 100, 40), "border": (100, 200, 100)},
                {"id": "attack1", "name": "Ataque 1", "color": (100, 40, 40), "border": (200, 100, 100)},
                {"id": "attack2", "name": "Ataque 2", "color": (100, 40, 40), "border": (200, 100, 100)},
            ]
        
        # Agregar botón de terminar turno
        self.options.append(
            {"id": "end_turn", "name": "Terminar Turno", "color": (40, 40, 100), "border": (100, 100, 200)}
        )
    
    def hide(self):
        """Oculta el menú."""
        self.visible = False
        self.options = []
        self.selected_unit = None
        self.action_rects = []
    
    def handle_click(self, mouse_pos):
        """
        Maneja el clic en el menú.
        Retorna el ID de la acción seleccionada o None.
        """
        if not self.visible:
            return None
        
        for i, rect in enumerate(self.action_rects):
            if rect.collidepoint(mouse_pos):
                return self.options[i]["id"]
        
        return None
    
    def draw(self, screen, font_small, x=20, y=120, width=140, height=35):
        """Dibuja el menú de acciones."""
        if not self.visible or not self.options:
            return
        
        self.action_rects = []
        
        for i, option in enumerate(self.options):
            rect = pygame.Rect(x, y + i * 40, width, height)
            self.action_rects.append(rect)
            
            pygame.draw.rect(screen, option["color"], rect, border_radius=4)
            pygame.draw.rect(screen, option["border"], rect, 2, border_radius=4)
            
            text = font_small.render(option["name"], True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
    
    def get_option_count(self):
        """Retorna el número de opciones en el menú."""
        return len(self.options)
