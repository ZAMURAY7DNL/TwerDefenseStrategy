#!/usr/bin/env python3
"""
Generador de canción épica de 3 minutos
=======================================
Ejecutar: python generate_epic_song.py

Este script genera una canción de 3 minutos con:
- Estructura: Intro-Verso-Puente-Coro-Verso-Coro-Outro
- Cambios de tonalidad: Am -> Cm -> Am -> Cm
- Ritmo pegajoso con groove latino/electrónico
- Formato OGG (listo para el juego)

El proceso toma unos minutos. El resultado se guarda como 'epic_song_3min.ogg'
"""

import numpy as np
import soundfile as sf
import sys

print("=" * 60)
print("GENERADOR DE CANCIÓN ÉPICA - 3 MINUTOS")
print("=" * 60)
print()

# Configuración
sr = 44100
bpm = 128
beat = 60 / bpm
spb = int(sr * beat)
total_beats = 384  # 3 minutos a 128 BPM
total_samples = int(sr * 180)

print(f"Configuración:")
print(f"  Sample rate: {sr} Hz")
print(f"  BPM: {bpm}")
print(f"  Duración: 3 minutos ({total_beats} beats)")
print(f"  Total samples: {total_samples:,}")
print()

# Generar en bloques de 32 beats para ahorrar memoria
block_beats = 32
num_blocks = (total_beats + block_beats - 1) // block_beats

def generate_block(block_idx, block_beats, spb, sr, beat):
    """Genera un bloque de música."""
    start_beat = block_idx * block_beats
    end_beat = min(start_beat + block_beats, total_beats)
    actual_beats = end_beat - start_beat
    
    samples = actual_beats * spb
    melody = np.zeros(samples, dtype=np.float32)
    harmony = np.zeros(samples, dtype=np.float32)
    bass = np.zeros(samples, dtype=np.float32)
    drums = np.zeros(samples, dtype=np.float32)
    
    def add_note(freq, rel_beat, dur, vol, target):
        s = int(rel_beat * spb)
        e = int((rel_beat + dur) * spb)
        e = min(e, samples)
        if s >= samples or e <= 0 or freq <= 0:
            return
        s = max(0, s)
        
        length = e - s
        t = np.linspace(0, dur * beat, length, False)
        sq = np.where((t * freq) % 1.0 < 0.5, 1.0, -1.0) * 0.6
        si = np.sin(2 * np.pi * freq * t) * 0.4
        tone = sq + si
        
        attack = min(int(0.03 * sr), length // 8)
        env = np.ones(length)
        env[:attack] = np.linspace(0, 1, attack)
        
        target[s:e] += tone * env * vol
    
    # Generar contenido según la sección
    section = start_beat // 64
    local_start = start_beat % 64
    
    for beat_in_block in range(0, actual_beats, 4):
        abs_beat = start_beat + beat_in_block
        local_beat = beat_in_block
        
        # Determinar sección
        if abs_beat < 32:  # Intro
            if local_beat % 16 == 0:
                add_note(440, local_beat, 4, 0.3, melody)
                add_note(110, local_beat, 8, 0.3, bass)
        
        elif abs_beat < 96:  # Verso 1 (Am)
            pattern = (local_beat // 4) % 4
            if pattern == 0:
                add_note(440, local_beat, 1, 0.4, melody)
                add_note(110, local_beat, 2, 0.35, bass)
            elif pattern == 1:
                add_note(523.25, local_beat, 1, 0.45, melody)
            elif pattern == 2:
                add_note(659.25, local_beat, 1, 0.5, melody)
            else:
                add_note(440, local_beat, 1, 0.4, melody)
        
        elif abs_beat < 160:  # Puente
            if local_beat % 8 == 0:
                add_note(880, local_beat, 2, 0.35, melody)
            add_note(220, local_beat, 4, 0.3, bass)
        
        elif abs_beat < 224:  # Coro 1 (Cm)
            pattern = (local_beat // 4) % 4
            if pattern == 0:
                add_note(523.25, local_beat, 2, 0.5, melody)
                add_note(130.81, local_beat, 4, 0.4, bass)
            elif pattern == 1:
                add_note(622.25, local_beat, 2, 0.55, melody)
            elif pattern == 2:
                add_note(783.99, local_beat, 2, 0.6, melody)
            else:
                add_note(1046.5, local_beat, 2, 0.55, melody)
        
        elif abs_beat < 288:  # Verso 2 (Am)
            if local_beat % 2 == 0:
                add_note(440 + (local_beat % 8) * 50, local_beat, 0.5, 0.4, melody)
            add_note(110, local_beat, 4, 0.35, bass)
        
        elif abs_beat < 352:  # Coro 2 (Cm)
            add_note(523.25, local_beat, 1, 0.5, melody)
            add_note(622.25, local_beat + 1, 1, 0.55, melody)
            add_note(130.81, local_beat, 8, 0.45, bass)
        
        else:  # Outro
            fade = max(0.1, 0.4 - (abs_beat - 352) / 32 * 0.3)
            add_note(440, local_beat, 4, fade, melody)
            add_note(220, local_beat, 4, fade * 0.8, bass)
        
        # Batería en todas las secciones
        if local_beat % 4 == 0:
            # Kick
            kick_len = min(int(0.1 * sr), samples - int(local_beat * spb))
            if kick_len > 0 and int(local_beat * spb) < samples:
                t = np.linspace(0, kick_len/sr, kick_len, False)
                f = 60 * np.exp(-t * 30)
                kick = np.sin(2 * np.pi * f * t) * np.exp(-t * 10) * 0.5
                drums[int(local_beat * spb):int(local_beat * spb)+kick_len] += kick
        
        # Snare en contratiempo
        if local_beat % 4 == 2:
            snare_pos = int(local_beat * spb)
            if snare_pos < samples:
                snare_len = min(int(0.08 * sr), samples - snare_pos)
                if snare_len > 0:
                    noise = np.random.randn(snare_len).astype(np.float32) * 0.5
                    env = np.exp(np.linspace(0, -5, snare_len))
                    drums[snare_pos:snare_pos+snare_len] += noise * env * 0.4
    
    # Mezclar
    mix = melody * 0.8 + harmony * 0.6 + bass * 0.7 + drums * 0.5
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.9
    
    return mix


# Generar y escribir en bloques
print("Generando canción en bloques...")
print(f"Total de bloques: {num_blocks}")
print()

# Crear archivo
output_file = 'epic_song_3min.ogg'

# Generar todo primero (más rápido que escribir en streaming para OGG)
print("Generando bloques:")
all_audio = []

for i in range(num_blocks):
    percent = int(i / num_blocks * 100)
    print(f"  Bloque {i+1}/{num_blocks} ({percent}%)...", end='\r')
    
    block = generate_block(i, block_beats, spb, sr, beat)
    all_audio.append(block)

print(f"  Bloque {num_blocks}/{num_blocks} (100%)...")
print()

# Concatenar
print("Concatenando audio...")
full_wave = np.concatenate(all_audio)

# Asegurar duración exacta
target_samples = int(sr * 180)  # 3 minutos exactos
if len(full_wave) > target_samples:
    full_wave = full_wave[:target_samples]
elif len(full_wave) < target_samples:
    full_wave = np.pad(full_wave, (0, target_samples - len(full_wave)), 'constant')

print(f"Duración final: {len(full_wave)/sr:.1f} segundos")
print()

# Guardar
print(f"Guardando como '{output_file}'...")
sf.write(output_file, full_wave, sr, format='OGG')

print()
print("=" * 60)
print("¡CANCIÓN GENERADA EXITOSAMENTE!")
print("=" * 60)
print(f"Archivo: {output_file}")
print(f"Duración: 3 minutos")
print(f"Tamaño: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
print()
print("La canción está lista para usar en el juego.")
print("Estructura: Intro-Verso-Puente-Coro-Verso-Coro-Outro")
print("Cambios de tonalidad: Am -> Cm")
