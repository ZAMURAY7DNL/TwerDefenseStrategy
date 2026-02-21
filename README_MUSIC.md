# Música del Juego

## Canción de 3 Minutos

Para generar la canción épica de 3 minutos:

```bash
python generate_song_fast.py
```

Esto creará `epic_song_3min.wav` (3 minutos de música).

### Estructura de la Canción

- **0:00-0:15** - Intro
- **0:15-0:45** - Verso 1 (Am)
- **0:45-1:15** - Puente
- **1:15-1:45** - Coro (Cm)
- **1:45-2:15** - Verso 2 (Am)
- **2:15-2:45** - Coro Final (Cm)
- **2:45-3:00** - Outro

### Características

- Cambios de tonalidad: Am → Cm
- Ritmo pegajoso con batería electrónica
- Sin silencio al final para bucle limpio
- Si el juego dura más de 3 minutos, la música se reinicia automáticamente

## Solución de Problemas

### Si no suena la música de 3 minutos

1. Verifica que `epic_song_3min.wav` existe
2. Si no existe, ejecútalo:
   ```bash
   python generate_song_fast.py
   ```

### Si hay corte al final del bucle

La canción está diseñada para durar 3 minutos. Si el juego dura menos, no hay problema. Si dura más, se reiniciará el audio (puede haber un micro-corte de ~50ms que es normal en pygame).

### Si el audio se queda zombie (suena sin el juego)

1. Mata todos los procesos Python:
   ```bash
   taskkill /F /IM python.exe
   ```
2. O reinicia la computadora

## Formato

- **WAV** recomendado para mejor calidad de bucle
- **OGG** también soportado (más pequeño pero puede tener gaps)

El juego busca archivos en este orden:
1. `epic_song_3min.wav`
2. `epic_song_3min.ogg`
3. `bg_music_fixed.ogg` (respaldo)
