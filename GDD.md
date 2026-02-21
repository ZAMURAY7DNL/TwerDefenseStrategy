# TACTICAL DEFENSE
## Game Design Document (GDD)

> **Versión:** 1.0  
> **Fecha:** Febrero 2026  
> **Género:** Tactical Turn-Based Tower Defense  
> **Plataforma:** PC (Windows/Linux/Mac)  
> **Motor:** Python + Pygame

---

## 1. RESUMEN EJECUTIVO

### 1.1 Concepto del Juego
Tactical Defense es un híbrido entre juego táctico por turnos (como Into the Breach) y Tower Defense clásico (como Kingdom Rush). El jugador controla un **Héroe Comandante** con habilidades únicas y un escuadrón de tropas, enfrentándose a oleadas de enemigos en un grid hexagonal.

### 1.2 Propuesta de Valor Única
- **Sistema de turnos alternados estricto:** Héroe y tropas actúan uno a uno, alternando con el enemigo
- **Sistema de AP (Action Points) solo para el héroe:** El héroe es el centro estratégico, las tropas son apoyo
- **Grid hexagonal táctico:** Movimiento estratégico con líneas de visión y rangos
- **Ataques telegráficos:** (Planeado) El enemigo anuncia sus ataques, permitiendo contramedidas

### 1.3 Inspiraciones
| Juego | Elemento Tomado |
|-------|-----------------|
| Into the Breach | Sistema de turnos, grid hexagonal, ataques telegráficos |
| Kingdom Rush | Variedad de unidades, torres, progresión |
| XCOM | Sistema de AP, cobertura táctica |
| Day R | Sistema de combate por zonas del cuerpo |
| Bloons TD 6 | Progresión, mejoras, rejugabilidad |

---

## 2. GAMEPLAY

### 2.1 Core Loop
```
1. PREPARACIÓN
   └── Ver campo de batalla → Recibir recomendaciones del Oracle

2. FASE DE HÉROE (Jugador)
   └── Mover héroe (gratis) → Usar poderes (AP) → Posicionar tropas

3. FASE ENEMIGA (IA)
   └── Enemigos se mueven → Atacan si están a rango

4. FASE DE TROPAS (Jugador)
   └── Mover cada tropa → Atacar → Pasar al siguiente enemigo

5. REPETIR
   └── Hasta eliminar a todos los enemigos (Victoria) o perder al héroe (Derrota)
```

### 2.2 Sistema de Turnos (Implementado ✅)

**Patrón de Turnos:**
```
Ronda 1:
  1. Héroe (Jugador)
  2. Enemigo 1 (IA)
  3. Tropa 1 (Jugador)
  4. Enemigo 2 (IA)
  5. Tropa 2 (Jugador)
  6. Enemigo 3 (IA)
  ...
```

**Reglas:**
- Cada unidad actúa EXACTAMENTE una vez por ciclo
- No hay "fase de combate" masivo - los ataques son inmediatos
- El héroe SIEMPRE actúa primero en la ronda
- Si el héroe muere → Derrota inmediata

### 2.3 Sistema de AP (Action Points) ✅

**Solo el héroe tiene AP.**

| Estadística | Valor |
|-------------|-------|
| AP Máximo | 6 |
| Recuperación por turno | 4 AP |
| Movimiento | 0 AP (gratis) |
| Ataque básico | 2 AP |
| Poder especial | 3-5 AP |

**Diseño:** El AP obliga al jugador a tomar decisiones tácticas: ¿Ataco fuerte una vez o ataco débil dos veces? ¿Me curo o ataco?

### 2.4 Unidades

#### 2.4.1 Héroe (Comandante) ✅
- Único personaje con AP
- Puede equipar poderes desbloqueables
- Si muere → Game Over
- Movimiento gratuito

**Poderes Implementados:**
| Poder | AP | Daño | Efecto Adicional |
|-------|-----|------|------------------|
| Corte Rápido | 2 | x1.0 | Básico, confiable |
| Golpe Poderoso | 4 | x2.0 | Alto daño |
| Torbellino | 5 | x0.8 | Daño en área (AOE) |
| Disparo Preciso | 4 | x1.5 | Rango 4 |
| Autocuración | 3 | - | Cura 30 HP |
| Golpe de Escudo | 3 | x0.7 | Stun al enemigo |
| Furia | 3 | - | Buff daño, nerf defensa |
| Teletransporte | 4 | - | Movimiento instantáneo |

#### 2.4.2 Tropas (Implementadas ✅)

| Unidad | HP | ATK | Rango | Vel | Rol |
|--------|-----|-----|-------|-----|-----|
| **Berserker** | 100 | 25 | 1 | 4 | Tanque/DPS melee |
| **Assault** | 80 | 20 | 2 | 3 | DPS a distancia |
| **Ranger** | 60 | 15 | 3 | 5 | Scout/DPS rápido |
| **Sniper** | 50 | 35 | 4 | 2 | DPS alto/bajo HP |

**Habilidades Especiales (Propuestas):**
- **Berserker:** Carga (movimiento + ataque en línea recta)
- **Assault:** Supresión (reduce movimiento enemigo)
- **Ranger:** Disparo de área (daño adyacente)
- **Sniper:** Disparo perforante (atraviesa unidades)

#### 2.4.3 Torres (Implementadas ✅)
- No se mueven
- Atacan automáticamente a rango
- Menos HP que unidades
- Pueden ser destruidas

### 2.5 Enemigos

#### 2.5.1 Enemigos Actuales
- Mismos tipos que jugador: Berserker, Assault, Ranger, Sniper
- Héroe Enemigo: "Señor Oscuro" (con AP limitado)

#### 2.5.2 IA Enemiga (Implementada ✅)
**Selección de Objetivos:**
```python
Score = (1 - HP_ratio) * 50    # Prefiere objetivos débiles
        - Distancia * 0.5      # Prefiere cercanos
        + 30 si es héroe       # Prioriza héroe
        - 20 si se defiende    # Evita defensores
```

**Comportamiento:**
1. Seleccionar objetivo con mejor score
2. Si está a rango → ATACAR
3. Si no → Moverse hacia objetivo
4. Si tras moverse queda a rango → ATACAR

---

## 3. MUNDO Y NARRATIVA

### 3.1 Setting (Propuesto)
**Mundo:** Fantasy post-apocalíptico donde las "Máquinas de la Colmena" invaden territorios.

**Facciones Propuestas:**
| Facción | Estilo | Fortalezas | Debilidades |
|---------|--------|------------|-------------|
| **Humanos** | Equilibrado | Torres fuertes, versatile | Sin especialización |
| **Orcos** | Agresivo | Unidades poderosas, carga | Pocas torres, defensa baja |
| **Elfos** | Control | Rango largo, velocidad | HP bajo, melee débil |
| **Máquinas** | Defensivo | Armadura alta, sinergias | Lento, costoso |

### 3.2 Personajes
- **Comandante (Jugador):** Héroe personalizable
- **Oracle of Kimi:** IA asistente que da consejos tácticos
- **Señor Oscuro:** Jefe enemigo principal

### 3.3 Campaña (Propuesta)
**Estructura:**
- 5 Actos x 5 Misiones = 25 misiones
- Cada acto introduce nueva mecánica/unidad
- Misiones con objetivos variados (no solo "matar todo")

**Tipos de Misión:**
1. **Eliminación:** Derrotar a todos los enemigos (actual)
2. **Defensa:** Sobrevivir N turnos
3. **Escolta:** Proteger unidad VIP
4. **Captura:** Tomar y mantener puntos estratégicos
5. **Asesinato:** Eliminar héroe enemigo específico
6. **Saqueo:** Recoger recursos y escapar

---

## 4. SISTEMAS AVANZADOS

### 4.1 Progresión y Metajuego (Propuesto)

#### Árbol de Mejoras del Héroe
```
Nivel 1-10: Desbloquear poderes básicos
Nivel 11-20: Mejorar stats de poderes
Nivel 21-30: Poderes épicos únicos
```

#### Sistema de Equipamiento
- Armas: Afectan daño base
- Armaduras: Afectan HP y defensa
- Accesorios: Bonus especiales (+AP, +movimiento, etc.)

#### Logros y Desafíos
- "Asesino de Jefes": Derrotar 10 jefes
- "Imparable": Ganar sin perder unidades
- "Estratega": Ganar usando solo 50% de AP por turno

### 4.2 Modo Roguelite (Propuesto)

**Estructura de Run:**
```
Inicio → Elección de 3 mejoras → Misión → 
Elección de 3 mejoras → Misión → ... → Jefe Final
```

**Tipos de Mejoras:**
| Tipo | Ejemplo |
|------|---------|
| **Stat Boost** | +20% daño del héroe |
| **Nueva Habilidad** | Desbloquear "Tormenta de Hielo" |
| **Sinergia** | Berserkers adyacentes al héroe hacen +10 daño |
| **Reliquia** | "Amuleto del Tiempo": +1 AP por turno |
| **Mejora de Torre** | Torres curan unidades adyacentes |

### 4.3 Economía (Propuesto)

**Recursos:**
| Recurso | Cómo Obtener | Uso |
|---------|--------------|-----|
| **Oro** | Matar enemigos | Comprar unidades/torres |
| **Hierro** | Destruir torres | Mejorar armadura |
| **Madera** | Misión bosque | Construir torres |
| **Cristal** | Jefes | Poderes mágicos |

**Decisiones Estratégicas:**
- ¿Mejorar unidad existente o comprar nueva?
- ¿Gastar oro en tropas o en torres?
- ¿Guardar cristales para poder épico o usarlos ahora?

### 4.4 Construcción de Torres (Propuesto)

**Durante turno del jugador:**
- Colocar nuevas torres en hexágonos vacíos
- Costo: Oro + Madera
- Límite: Máximo 3 torres por zona

**Sinergias de Torres:**
| Combinación | Efecto |
|-------------|--------|
| Fuego + Viento | Torbellino (daño área) |
| Hielo + Tierra | Avalancha (ralentiza) |
| Rayo + Metal | Sobrecarga (daño crítico) |

---

## 5. NIVELES Y DISEÑO

### 5.1 Grid Hexagonal (Implementado ✅)
- **Tamaño:** 8x6 por zona (96 hexágonos total)
- **Terrenos:** (Propuesto)
  - **Bosque:** +Defensa para ocupante
  - **Colina:** +Rango de ataque
  - **Agua:** Solo unidades voladoras/nadan
  - **Lava:** Daño por turno
  - **Hielo:** Resbaladizo (movimiento aleatorio)

### 5.2 Oleadas (Propuesto)
```
Turno 1-3: Enemigos básicos
Turno 4: Mini-jefe
Turno 5-8: Enemigos + elite
Turno 9: Jefe de Acto
```

### 5.3 Jefes

**Jefe Actual:** Señor Oscuro (Héroe enemigo con AP)

**Jefes Propuestos:**
| Jefe | Habilidad Especial |
|------|-------------------|
| **Colmena Madre** | Spawnea drones cada turno |
| **Titán de Acero** | Inmune primer turno, alto HP |
| **Sombra** | Teletransporte cada 2 turnos |
| **Cataclismo** | Destruye terreno aleatorio |

---

## 6. INTERFAZ DE USUARIO

### 6.1 UI Implementada ✅
- **Panel Superior:** Ronda, fase, unidad activa, AP
- **Panel Derecho:** Contador de unidades vivas
- **Panel Inferior Izquierdo:** Info de unidad seleccionada
- **Menú Lateral:** Acciones disponibles
- **Oracle:** Recomendaciones tácticas

### 6.2 UI Propuesta (Mejoras)
- **Ataques Telegráficos:** Flechas rojas indicando ataques enemigos futuros
- **Números Flotantes:** Daño mostrado al impactar
- **Tooltips:** Información detallada al hacer hover
- **Mini-mapa:** Vista general del campo
- **Historial de Acciones:** Últimos 5 eventos

### 6.3 Controles
| Acción | Tecla/Mouse |
|--------|-------------|
| Seleccionar | Click izquierdo |
| Mover | Click en tile verde |
| Atacar | Click en enemigo |
| Cancelar | ESC |
| Terminar turno | ESPACIO |
| Reiniciar (game over) | R |
| Poderes | Botones del menú |

---

## 7. AUDIO

### 7.1 Música (Propuesta)
- **Menú:** Orquestal épico, lento
- **Preparación:** Tensión creciente, percusión
- **Combate:** Ritmo acelerado, metales
- **Victoria:** Fanfarria triunfal
- **Derrota:** Cuerdas melancólicas

### 7.2 SFX (Propuesta)
| Evento | Sonido |
|--------|--------|
| Seleccionar unidad | Click metálico |
| Mover | Pasos según terreno |
| Ataque melee | Impacto/golpe |
| Ataque ranged | Disparo/flecha |
| Proyectil impacta | Explosión pequeña |
| Héroe usa poder | Efecto mágico |
| Unidad muere | Grito + caída |
| Victoria | Fanfarria |

---

## 8. TECNICALIDADES

### 8.1 Arquitectura Actual ✅
```
Modular - Separación de responsabilidades
├── core/          : Coordinación
├── systems/       : Lógica de juego
├── entities/      : Objetos del juego
├── ui/            : Interfaz
└── config/        : Constantes
```

### 8.2 Rendimiento
- **Target:** 60 FPS en hardware medio
- **Optimizaciones:** Dibujado por capas, culling fuera de pantalla
- **Límite de unidades:** ~20 por bando

### 8.3 Guardado (Propuesto)
- Guardado entre misiones
- Checkpoints durante misión larga
- Historial de victorias (para estadísticas)

---

## 9. ROADMAP

### Fase 1: Core Completo (ACTUAL ✅)
- [x] Sistema de turnos
- [x] Héroe con AP
- [x] 4 tipos de unidades
- [x] IA enemiga
- [x] Proyectiles y partículas

### Fase 2: Profundidad Táctica (Próximo)
- [ ] Ataques telegráficos
- [ ] Números de daño flotantes
- [ ] Tooltips detallados
- [ ] Habilidades especiales por unidad
- [ ] Terreno con efectos

### Fase 3: Progresión (Futuro)
- [ ] Sistema de XP
- [ ] Árbol de habilidades
- [ ] Equipamiento
- [ ] Modo roguelite con mejoras

### Fase 4: Contenido (Futuro)
- [ ] Campaña narrativa
- [ ] Múltiples facciones
- [ ] 20+ misiones
- [ ] Jefes épicos

### Fase 5: Multiplayer (Futuro lejano)
- [ ] Co-op local
- [ ] PvP asíncrono
- [ ] Editor de mapas

---

## 10. APÉNDICE

### 10.1 Historial de Versiones
| Versión | Fecha | Cambios |
|---------|-------|---------|
| 0.1 | Ene 2026 | Prototipo inicial |
| 0.5 | Feb 2026 | Sistema de turnos básico |
| 1.0 | Feb 2026 | Refactorización modular, jugable |
| 1.1 | - | Próxima versión |

### 10.2 Recursos de Referencia
- `SUGERENCIAS_MEJORAS.txt`: Investigación de mercado
- `PROJECT_CONTEXT.md`: Documentación técnica completa

### 10.3 Glosario
| Término | Definición |
|---------|------------|
| **AP** | Action Points - Puntos de acción |
| **AOE** | Area of Effect - Daño en área |
| **Telegráfico** | Ataque anunciado antes de ejecutarse |
| **Roguelite** | Juego con progresión entre runs |
| **Tile/Hex** | Casilla del grid hexagonal |
| **Troop** | Unidad básica (no héroe) |

---

**Documento mantenido por:** Claude (Kimi Code)  
**Última actualización:** Febrero 2026  
**Estado:** Core implementado, listo para expansión
