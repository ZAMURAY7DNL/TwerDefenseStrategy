"""
Constantes del juego - Colores, tamaños, configuraciones
"""

# ============================================================
# PANTALLA Y FPS
# ============================================================
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

# ============================================================
# COLORES DEL JUEGO
# ============================================================
COLOR_BG = (15, 20, 25)
COLOR_HONEY_BORDER = (218, 165, 32)
COLOR_HONEY_FILL = (255, 215, 0, 30)
COLOR_HONEY_DARK = (184, 134, 11)

# Colores de zonas
COLOR_PLAYER_ZONE = (40, 70, 100)
COLOR_ENEMY_ZONE = (100, 40, 40)
COLOR_NEUTRAL_ZONE = (50, 50, 50)
COLOR_HOVER = (255, 255, 100)
COLOR_SELECTED = (255, 150, 50)
COLOR_VALID_MOVE = (100, 255, 100)
COLOR_ORACLE = (255, 215, 0)

# Colores de unidades
COLOR_UNIT_PLAYER = (100, 200, 100)
COLOR_UNIT_ENEMY = (200, 100, 100)
COLOR_PROJECTILE_PLAYER = (150, 255, 150)
COLOR_PROJECTILE_ENEMY = (255, 100, 100)

# Colores de pasto
GRASS_BASE = (34, 85, 51)
GRASS_LIGHT = (50, 120, 70)
GRASS_DARK = (20, 60, 30)
GRASS_WAVE = (60, 140, 80)

# Efectos de luz
GLOW_INTENSITY = 1.5
SHADOW_ALPHA = 120

# ============================================================
# GRID PANAL (HEXÁGONOS)
# ============================================================
HEX_RADIUS = 42
HEX_WIDTH = HEX_RADIUS * 2
HEX_HEIGHT = int(HEX_RADIUS * 1.732)
HEX_MARGIN = 0

GRID_COLS = 8
GRID_ROWS = 6

ZONE_PLAYER_Y = 520
ZONE_ENEMY_Y = 80

# ============================================================
# FASES DEL JUEGO
# ============================================================
PHASE_PLAYER_TURN = "player_turn"
PHASE_ENEMY_TURN = "enemy_turn"
PHASE_COMBAT = "combat"
PHASE_VICTORY = "victory"
PHASE_DEFEAT = "defeat"

# ============================================================
# CONFIGURACIÓN DE COMBATE
# ============================================================
COMBAT_DURATION = 4.0  # Duración del combate en segundos
AI_MOVE_DELAY = 0.5    # Delay entre movimientos de la IA
