# TACTICAL DEFENSE - Contexto del Proyecto

> **ARCHIVO DE REFERENCIA PARA RECUPERAR CONTEXTO**
> Fecha: Febrero 2026
> Versión del código: Modular v2.0

---

## 📋 DESCRIPCIÓN GENERAL

**Tactical Defense** es un juego de estrategia táctica por turnos con elementos de Tower Defense, inspirado en:
- Into the Breach (sistema de turnos, grid hexagonal)
- Kingdom Rush (torres y unidades)
- XCOM/Day R (sistema de AP - Action Points)

**Stack Tecnológico:**
- Lenguaje: Python 3.13+
- Motor: Pygame 2.6+
- Arquitectura: Modular, orientada a sistemas

---

## 🗂️ ESTRUCTURA DE ARCHIVOS

```
liko/
├── main.py                          # Punto de entrada
├── PROJECT_CONTEXT.md               # ESTE ARCHIVO
├── SUGERENCIAS_MEJORAS.txt          # Investigación de mercado (295 líneas)
├── GDD.md                           # Game Design Document
│
├── dev_tools/                       # HERRAMIENTAS DE DESARROLLO
│   ├── inspector.py                 # UI principal (tkinter) - EDITAR VALORES
│   ├── parser.py                    # Parser de Python usando AST
│   ├── file_monitor.py              # Monitoreo de archivos
│   ├── test_parser.py               # Tests de la herramienta
│   ├── sound_demo.py                # Demo interactiva de sonidos
│   ├── run_inspector.bat            # Launcher Windows
│   └── README.md                    # Documentación de la herramienta
│
├── config/
│   ├── __init__.py
│   ├── constants.py                 # Colores, tamaños, constantes del juego
│   └── settings.py                  # Configuraciones ajustables
│
├── core/                            # NÚCLEO DEL JUEGO
│   ├── __init__.py
│   ├── game.py                      # Loop principal, input, coordinación (~500 líneas)
│   ├── grid_manager.py              # Gestión del grid hexagonal
│   ├── unit_manager.py              # Creación y gestión de unidades
│   ├── combat_handler.py            # Ataques, proyectiles, daño
│   ├── animation_manager.py         # Animaciones de ataque
│   └── renderer.py                  # Renderizado de UI y elementos
│
├── entities/                        # ENTIDADES DEL JUEGO
│   ├── __init__.py
│   ├── hero.py                      # Héroe con sistema AP
│   ├── geometric_hero.py            # Personalización visual del héroe
│   ├── unit.py                      # Unidades básicas (UltraUnit)
│   ├── tower.py                     # Torres (UltraTower)
│   └── projectile.py                # Proyectiles (TracerProjectile)
│
├── systems/                         # SISTEMAS DEL JUEGO
│   ├── __init__.py
│   ├── alternating_turn_system.py   # Sistema de turnos alternados estrictos
│   ├── enemy_ai.py                  # IA enemiga completa
│   ├── sound_generator.py           # 🎵 Generador de sonidos procedural
│   ├── combat_dayr/                 # Sistema de combate Day R
│   │   ├── __init__.py
│   │   ├── action_points.py         # Sistema de AP
│   │   ├── action_types.py          # Tipos de acciones
│   │   ├── combat_manager.py        # Gestor de combate
│   │   ├── damage_system.py         # Sistema de daño
│   │   ├── targeting_system.py      # Selección de objetivos
│   │   └── turn_queue.py            # Cola de turnos
│   ├── ai.py                        # IA básica (legacy)
│   ├── combat.py                    # Combate básico (legacy)
│   ├── geometry.py                  # Utilidades geométricas
│   ├── grid.py                      # HoneycombTile (grid hexagonal)
│   ├── grass.py                     # Sistema de pasto decorativo
│   ├── particles.py                 # Sistema de partículas
│   ├── tactical_info.py             # Información táctica
│   ├── turn_system.py               # Sistema de turnos (legacy)
│   ├── action_menu.py               # Menú de acciones
│   └── input.py                     # Manejo de input (legacy)
│
├── ui/                              # INTERFAZ DE USUARIO
│   ├── __init__.py
│   └── buttons.py                   # OracleOfKimi, PersistentMenu, botones
│
└── utils/                           # UTILIDADES
    └── __init__.py
```

---

## 🎮 MECÁNICAS ACTUALES

### Sistema de Turnos (AlternatingTurnSystem)
```
Patrón: Héroe → Enemigo → Tropa1 → Enemigo → Tropa2 → Enemigo → ...
```

| Fase | Descripción |
|------|-------------|
| **PLAYER_HERO** | Controlas al héroe (tiene AP) |
| **PLAYER_TROOP** | Controlas una tropa (sin AP, movimiento libre) |
| **ENEMY** | IA enemiga actúa |
| **ENDED** | Combate terminado |

### Sistema de AP (Action Points)
- **Solo el héroe tiene AP**
- AP máximo: 6
- Recuperación: 4 por turno
- Movimiento: GRATIS (no consume AP)
- Ataques y poderes: consumen AP

### Poderes del Héroe (8 disponibles)

| Poder | AP | Efecto |
|-------|-----|--------|
| **Corte Rápido** (slash) | 2 | Ataque básico, daño x1.0 |
| **Golpe Poderoso** (power_strike) | 4 | Daño x2.0 |
| **Torbellino** (whirlwind) | 5 | Ataque en área, daño x0.8 |
| **Disparo Preciso** (snipe) | 4 | Rango 4, daño x1.5 |
| **Autocuración** (heal) | 3 | Recupera 30 HP |
| **Golpe de Escudo** (shield_bash) | 3 | Daño x0.7 + stun |
| **Furia** (berserk) | 3 | Buff de daño, reduce defensa |
| **Teletransporte** (teleport) | 4 | Movimiento instantáneo |

### Tipos de Unidades

| Unidad | HP | ATK | Rango | Velocidad | Especial |
|--------|-----|-----|-------|-----------|----------|
| **Berserker** | 100 | 25 | 1 | 4 | Carga |
| **Assault** | 80 | 20 | 2 | 3 | Supresión |
| **Ranger** | 60 | 15 | 3 | 5 | Disparo área |
| **Sniper** | 50 | 35 | 4 | 2 | Disparo largo |

### Grid Hexagonal
- **Dimensiones:** 8 columnas x 6 filas (por zona)
- **Total:** 96 hexágonos (48 jugador + 48 enemigo)
- **Radio:** 42 píxeles
- **Zonas:** Jugador (abajo), Enemigo (arriba), Neutral (centro)

### IA Enemiga
- Selección de objetivos basada en:
  - HP restante (prefiere débiles)
  - Distancia (prefiere cercanos)
  - Prioridad al héroe (+30 puntos)
  - Penalización por defensa (-20 puntos)
- Movimiento táctico hacia el jugador
- Puede moverse Y atacar en el mismo turno si queda a rango

---

## 🎯 FEATURES IMPLEMENTADOS

### Core Gameplay ✅
- [x] Grid hexagonal funcional
- [x] Sistema de turnos alternados
- [x] Héroe con sistema de AP
- [x] 4 tipos de unidades + héroes
- [x] Torres para ambos bandos
- [x] Proyectiles con trayectoria
- [x] Sistema de partículas
- [x] IA enemiga táctica

### UI ✅
- [x] Menú persistente con botones
- [x] Oracle of Kimi (asistente táctico)
- [x] Panel de información de unidades
- [x] Indicador de AP
- [x] Pantallas de victoria/derrota
- [x] Textos de ayuda contextual

### Sistemas Avanzados ✅
- [x] Sistema de combate Day R (AP, daño, etc.)
- [x] Animaciones de ataque
- [x] Efectos visuales (partículas, sombras)
- [x] Pasto decorativo animado

---

## 🔄 CÓMO FLUYE EL JUEGO

```
1. INICIO
   └── Crear grid → Crear unidades → Setup turnos

2. TURNO DEL JUGADOR
   ├── FASE HÉROE:
   │   └── Click en héroe → Mover (gratis) o Atacar (AP)
   │   └── Terminar → Pasa a enemigo
   │
   └── FASE TROPA:
       └── Click en tropa → Mover o Atacar → Terminar → Pasa a enemigo

3. TURNO ENEMIGO
   └── IA selecciona objetivo → Mueve → Ataca (si a rango)

4. REPETIR hasta victoria/derrota
```

---

## 🛠️ PATRONES DE DISEÑO

### Separación de Responsabilidades
```
game.py          → Coordina, NO implementa
grid_manager     → Todo lo relacionado con grid
unit_manager     → Todo lo relacionado con unidades
combat_handler   → Todo lo relacionado con combate
enemy_ai         → Todo lo relacionado con IA
renderer         → Todo lo relacionado con dibujado
```

### Comunicación entre Módulos
```
Game (coordinador)
    ├── GridManager (consultas)
    ├── UnitManager (datos de unidades)
    ├── CombatHandler (ejecutar ataques)
    ├── EnemyAI (procesar turno enemigo)
    ├── AnimationManager (efectos visuales)
    └── Renderer (dibujar todo)
```

---

## 📦 DEPENDENCIAS ENTRE MÓDULOS

```
config/          → Constantes, settings (sin dependencias)
utils/           → Utilidades genéricas
systems/         → Depende de config/
entities/        → Depende de systems/combat_dayr/
ui/              → Depende de entities/ y systems/
core/            → Depende de TODOS los anteriores
main.py          → Solo importa core/
```

---

## 🐛 NOTAS DE IMPLEMENTACIÓN

### Sistema de Turnos
- El héroe SIEMPRE actúa primero
- Cada unidad actúa UNA vez antes de que actúe el siguiente enemigo
- Las tropas no tienen AP (sistema simplificado)
- El enemigo puede moverse Y atacar si queda a rango tras moverse

### Movimiento
- Es gratuito para todas las unidades
- Solo 1 movimiento por turno
- Solo a hexágonos adyacentes vacíos
- Las tropas del jugador solo se mueven en zona jugador
- Los enemigos solo se mueven en zona enemiga

### Ataques
- Héroe: consume AP, puede usar poderes especiales
- Tropas: ataque básico gratuito (1 por turno)
- Enemigos: ataque básico (héroe enemigo puede usar AP)

### Proyectiles
- Todos los ataques usan proyectiles visuales
- Los proyectiles tienen velocidad y trayectoria
- El daño se aplica al llegar el proyectil

---

## 🔧 CONFIGURACIONES CLAVE (constants.py)

```python
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

HEX_RADIUS = 42
GRID_COLS = 8
GRID_ROWS = 6

COMBAT_DURATION = 4.0
AI_MOVE_DELAY = 0.5
```

---

## 🚀 CÓMO EXTENDER

### Agregar una Nueva Unidad
1. Agregar stats en `unit_manager.py` → `_create_player_troops()`
2. Agregar tipo en `entities/unit.py` → `UltraUnit`
3. Agregar habilidad especial en `combat_handler.py`

### Agregar un Nuevo Poder de Héroe
1. Agregar en `entities/hero.py` → `HeroPowers.POWERS`
2. Agregar botón en `core/game.py` → `_show_hero_menu()`
3. Implementar efecto en `combat_handler.py`

### Agregar Nueva IA
1. Modificar `systems/enemy_ai.py`
2. Implementar comportamiento en `process_turn()`
3. O crear nueva clase que herede de `EnemyAI`

---

## 📝 HISTORIAL DE CAMBIOS RECIENTES

### Refactorización Modular (Feb 2026)
- ✅ Separado `game.py` en 6 módulos especializados
- ✅ Creado `GridManager` para gestión de grid
- ✅ Creado `UnitManager` para gestión de unidades
- ✅ Creado `CombatHandler` para lógica de combate
- ✅ Creado `EnemyAI` para inteligencia enemiga
- ✅ Creado `AnimationManager` para efectos visuales
- ✅ Creado `Renderer` para todo el dibujado
- ✅ Actualizados `__init__.py` con exports

---

## 🔍 QUÉ BUSCAR SI HAY PROBLEMAS

| Problema | Dónde Buscar |
|----------|--------------|
| Unidad no aparece | `unit_manager.py` → `_setup_units()` |
| Movimiento no funciona | `grid_manager.py` → `update_valid_moves()` |
| Ataque no hace daño | `combat_handler.py` → `execute_*_attack()` |
| IA no actúa | `enemy_ai.py` → `process_turn()` |
| Proyectil no vuela | `entities/projectile.py` |
| Menú no aparece | `ui/buttons.py` → `PersistentMenu` |
| Turnos desincronizados | `alternating_turn_system.py` |

---

## 📞 PALABRAS CLAVE PARA BÚSQUEDA RÁPIDA

**Si necesitas modificar... busca:**
- "HP de unidades" → `unit_manager.py` líneas con `max_health`
- "Daño de ataques" → `combat_handler.py` líneas con `damage`
- "Velocidad del juego" → `constants.py` → `FPS`
- "Colores" → `constants.py` → `COLOR_*`
- "Mensajes UI" → `renderer.py` o `game.py` → `_draw_ui()`
- "Comportamiento enemigo" → `enemy_ai.py` → `select_target()`

---

## 🎯 PRÓXIMAS TAREAS (PENDIENTES)

Ver `SUGERENCIAS_MEJORAS.txt` para lista completa investigada.

**Prioridad Alta:**
- Indicadores de ataques telegráficos (flechas rojas)
- Números de daño flotantes
- Tooltips con información
- Sistema de XP básico

**Prioridad Media:**
- Efectos de terreno (bosque, colina, agua)
- Sistema de recursos/oro
- Modo roguelite (mejoras al final de turno)
- Más tipos de unidades

**Largo Plazo:**
- Campaña con narrativa
- Facciones con estilos distintos
- Modo co-op o PvP
- Construcción de torres durante turno

---

## 🛠️ HERRAMIENTAS DE DESARROLLO (dev_tools/)

### Inspector de Valores
Herramienta gráfica para editar valores del juego sin tocar código.

**Ubicación:** `dev_tools/inspector.py`

**Cómo usar:**
```bash
# Windows (doble click)
dev_tools/run_inspector.bat

# O consola
python dev_tools/inspector.py
```

**Qué edita:**
- Stats de unidades (HP, ATK, Rango, Velocidad)
- Stats del héroe (AP, poderes)
- Constantes del juego (FPS, tamaños)

**Características:**
- ✅ UI con tkinter (nativo, no dependencias)
- ✅ Auto-refresh cada 5 segundos (detecta cambios externos)
- ✅ Backup automático antes de guardar (`.backup`)
- ✅ Parser AST (no ejecuta código, solo lo lee)

**Limitaciones:**
- ❌ No hot-reload (debes reiniciar el juego)
- ❌ Solo valores numéricos simples
- ❌ No edita lógica compleja

### Archivos del Dev Tools
```
dev_tools/
├── inspector.py          # UI principal (tkinter)
├── parser.py             # Parser Python AST
├── file_monitor.py       # Monitoreo de archivos
├── test_parser.py        # Tests
├── run_inspector.bat     # Launcher Windows
└── README.md             # Documentación
```

### Tests
```bash
python dev_tools/test_parser.py
```

---

## 🎵 SISTEMA DE SONIDO (`systems/sound_generator.py`)

### Generador Procedural
Genera sonidos de videojuego usando matemáticas (ondas senoidales), sin archivos externos.

**Principios psicoacústicos aplicados:**
- **Frecuencias 1-4kHz**: Rango donde el oído es más sensible
- **Ataque rápido (<10ms)**: Sensación de respuesta inmediata
- **Decay exponencial**: Satisfacción al escuchar
- **Modulación de pitch ascendente**: Asociado a recompensa/positivo

### Tipos de Sonidos

| Sonido | Función | Frecuencia/Tipo |
|--------|---------|-----------------|
| **Botones** |||
| `button_hover` | Hover botón | 3kHz, 40ms, muy sutil |
| `button_click` | Click confirmar | Click mecánico + 1.2kHz + 600Hz |
| `button_back` | Volver/Cancelar | Descendente 800Hz |
| **Pasos** |||
| `footstep()` | Caminar | Ruido + thump 80-300Hz según superficie |
| **Recompensa** |||
| `coin_collect` | Recolectar item | 1.8kHz + quinta justa |
| `power_up` | Mejora/Nivel up | Sweep ascendente 400→1200Hz |
| `combo_success` | Combo x3, x4 | Secuencia ascendente rápida |
| **Acción** |||
| `hit_impact` | Golpe recibido | Descendente + ruido |
| `shoot_projectile` | Disparo | Silbido descendente |
| **Música** |||
| `generate_ambient_music` | Fondo tranquilo | Drone A2+E3, panning lento estéreo |
| `systems/music_player.py` | **🎵 NUEVO Sistema de Música Robusto** | Canal dedicado, thread de monitoreo, bucle manual, reinicio instantáneo, nunca se corta |
| **Estado** |||
| `victory_jingle` | Ganar partida | Acorde mayor C-E-G |
| `defeat_sound` | Perder partida | Descendente grave 400→100Hz |

### Superficies de Pasos
- **grass**: Ruido suave + thump 80Hz
- **stone**: Más "clack", resonancia 150Hz
- **metal**: Metálico resonante 300Hz
- **wood**: Hueco, resonante 120Hz

### Sistema de Música Robusto 🎵
**Nueva implementación: `systems/music_player.py`**

**Problema anterior:**
- La música se cortaba al terminar el bucle
- Conflictos entre canales de efectos y música
- Sistema de reinicio no funcionaba correctamente

**Nueva solución:**
```python
# Sistema completamente separado
music_player.py
├── Canal 0 reservado exclusivamente
├── Thread de monitoreo dedicado (revisa cada 300ms)
├── Bucle manual (no depende de pygame loops=-1)
└── Reinicio instantáneo si se detecta corte
```

**Características del MusicPlayer:**
- **Canal dedicado**: Canal 0 solo para música, nunca usado por efectos
- **Thread monitor**: Verifica constantemente en background
- **Bucle manual**: La música se reproduce con `loops=-1` pero con monitoreo
- **Generación procedural**: Crea el audio matemáticamente cada vez
- **Volumen independiente**: Control separado de música vs efectos

**La Melodía (16 segundos):**
```
Estructura:
0-4s:   Intro épica (A4 → C5 → E5 → G5 → A5)
4-8s:   Desarrollo (descenso y respuesta)
8-12s:  Variación (C5-D5-E5 con rítmica diferente)
12-16s: Resolución (vuelta a A4 para bucle perfecto)

Armonía: Am → F → G → Am
Bajo: A2 → F2 → G2 → A2
```

**Cómo funciona:**
1. `start_epic_music()` genera el audio y lo reproduce
2. Thread `monitor_loop()` revisa cada 300ms si sigue sonando
3. Si detecta que se detuvo, reinicia inmediatamente
4. Efectos de sonido usan otros canales (1-7), nunca interfieren

**Archivos:**
- `systems/music_player.py` - Sistema nuevo y robusto
- `core/game.py` - Usa `start_epic_music()` al iniciar

### Demo Interactivo
```bash
python dev_tools/sound_demo.py
```
**Controles:**
- `1-9`: Sonidos de gameplay
- `Q,W,E,R`: Sonidos de UI
- `A,S,D`: Pasos en diferentes superficies
- `M`: Toggle música ambient
- `F`: Secuencia de pasos
- `ESC`: Salir

### Uso en el Juego
```python
from systems.sound_generator import get_sound_generator
from systems.music_player import start_epic_music, stop_music

sounds = get_sound_generator()

# Efectos
sounds.button_click().play()            # Click botón
sounds.footstep('grass').play()         # Paso en hierba
sounds.coin_collect('high').play()      # Moneda

# Música (nueva API)
start_epic_music()                      # Música épica con monitoreo
stop_music()                            # Detener música
```

### Integración Actual
- ✅ Sonido al usar poder del héroe
- ✅ Sonido de victoria/derrota
- ✅ **Sonido de pasos al mover unidades**
- ✅ **Sonido de click en botones**
- ✅ **Botón de reinicio funcional**
- ✅ **NUEVO: Sistema de música robusto con music_player.py**
- ✅ **Canal dedicado para música (anti-cortes)**
- 🔲 Sonido de proyectiles lanzados
- 🔲 Sonido de daño al enemigo

---

**Última actualización:** Febrero 2026
**Responsable:** Claude (Kimi Code)
**Estado:** Jugable, modular, listo para expansión
