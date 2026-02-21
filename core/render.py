"""
Sistema de Renderizado
"""


class RenderSystem:
    """Sistema de renderizado del juego"""
    
    def __init__(self):
        pass
    
    def draw(self, game):
        """Dibuja todo el juego"""
        # Fondo
        game.screen.fill(game.COLOR_BG)
        
        # Pasto
        game.grass.draw(game.screen)
        
        # Fondo de zonas
        self._draw_zones(game)
        
        # Grid y tiles
        self._draw_grid(game)
        
        # Unidades y torres
        self._draw_entities(game)
        
        # Proyectiles
        self._draw_projectiles(game)
        
        # Partículas
        game.particles.draw(game.screen)
        
        # UI
        game._draw_ui()
        
        # Pantallas de victoria/derrota
        if game.phase == "victory":
            self._draw_victory(game)
        elif game.phase == "defeat":
            self._draw_defeat(game)
        
        game.pygame.display.flip()
    
    def _draw_zones(self, game):
        """Dibuja las zonas del campo de batalla"""
        from config.constants import ZONE_ENEMY_Y, ZONE_PLAYER_Y, GRID_ROWS, HEX_HEIGHT
        
        game.pygame.draw.rect(
            game.screen, 
            (30, 40, 35), 
            (0, ZONE_ENEMY_Y - 30, game.SCREEN_WIDTH, 
             ZONE_PLAYER_Y - ZONE_ENEMY_Y + GRID_ROWS * HEX_HEIGHT + 100)
        )
        
        game.pygame.draw.line(
            game.screen, 
            game.COLOR_HONEY_BORDER, 
            (50, game.neutral_zone_y), 
            (game.SCREEN_WIDTH - 50, game.neutral_zone_y), 
            4
        )
        
        # Labels
        game.screen.blit(
            game.font_medium.render("ZONA ENEMIGA", True, (255, 150, 150)), 
            (game.SCREEN_WIDTH // 2 - 100, ZONE_ENEMY_Y - 45)
        )
        game.screen.blit(
            game.font_medium.render("TU ZONA", True, (150, 255, 150)), 
            (game.SCREEN_WIDTH // 2 - 60, ZONE_PLAYER_Y + GRID_ROWS * HEX_HEIGHT + 25)
        )
    
    def _draw_grid(self, game):
        """Dibuja la grilla de tiles"""
        tiles = sorted(game.grid.values(), key=lambda t: t.y)
        for tile in tiles:
            tile.draw(game.screen)
    
    def _draw_entities(self, game):
        """Dibuja unidades y torres"""
        tiles = sorted(game.grid.values(), key=lambda t: t.y)
        
        # Recolectar todas las entidades
        all_entities = []
        for tile in tiles:
            if tile.unit:
                y_pos = tile.unit.visual_y if tile.unit.is_moving else tile.y
                all_entities.append((y_pos, tile.unit, tile))
            if tile.tower:
                all_entities.append((tile.y, tile.tower, tile))
        
        # Ordenar por Y y dibujar
        for y_pos, obj, tile in sorted(all_entities, key=lambda x: x[0]):
            if hasattr(obj, 'is_moving'):
                if obj.is_moving:
                    obj.draw(game.screen, obj.visual_x, obj.visual_y + tile.wall_height // 2)
                else:
                    obj.draw(game.screen, tile.x, tile.y + tile.wall_height // 2)
            else:
                obj.draw(game.screen, tile.x, tile.y + tile.wall_height // 2)
    
    def _draw_projectiles(self, game):
        """Dibuja los proyectiles"""
        for proj in game.projectiles:
            proj.draw(game.screen)
    
    def _draw_victory(self, game):
        """Dibuja pantalla de victoria"""
        overlay = game.pygame.Surface((game.SCREEN_WIDTH, game.SCREEN_HEIGHT), game.pygame.SRCALPHA)
        game.pygame.draw.rect(overlay, (0, 100, 0, 150), overlay.get_rect())
        game.screen.blit(overlay, (0, 0))
        
        game.screen.blit(
            game.font_large.render("¡VICTORIA!", True, (255, 215, 0)), 
            (game.SCREEN_WIDTH // 2 - 150, game.SCREEN_HEIGHT // 2 - 50)
        )
        
        game.screen.blit(
            game.font_medium.render("Has derrotado a todos los enemigos", True, (255, 255, 200)), 
            (game.SCREEN_WIDTH // 2 - 180, game.SCREEN_HEIGHT // 2 + 10)
        )
        
        game.btn_restart.draw(game.screen, game.font_small)
    
    def _draw_defeat(self, game):
        """Dibuja pantalla de derrota"""
        overlay = game.pygame.Surface((game.SCREEN_WIDTH, game.SCREEN_HEIGHT), game.pygame.SRCALPHA)
        game.pygame.draw.rect(overlay, (100, 0, 0, 150), overlay.get_rect())
        game.screen.blit(overlay, (0, 0))
        
        game.screen.blit(
            game.font_large.render("DERROTA", True, (255, 100, 100)), 
            (game.SCREEN_WIDTH // 2 - 100, game.SCREEN_HEIGHT // 2 - 50)
        )
        
        game.screen.blit(
            game.font_medium.render("Tus fuerzas han caído", True, (255, 200, 200)), 
            (game.SCREEN_WIDTH // 2 - 130, game.SCREEN_HEIGHT // 2 + 30)
        )
        
        game.btn_restart.draw(game.screen, game.font_small)
