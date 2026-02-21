#!/usr/bin/env python3
"""
Generador rápido de canción de 3 minutos
=========================================
Versión optimizada que genera en ~30 segundos
"""
import numpy as np
import wave
import struct
import sys

print("Generando canción de 3 minutos...")

# Configuración
sr = 44100
bpm = 128
beat = 60 / bpm
spb = int(sr * beat)
total_beats = 384  # 3 minutos
duration = 180  # segundos

# Crear archivo WAV directamente (más rápido que OGG)
output_file = 'epic_song_3min.wav'

with wave.open(output_file, 'wb') as wav:
    wav.setnchannels(2)  # Stereo
    wav.setsampwidth(2)  # 16-bit
    wav.setframerate(sr)
    
    # Generar en chunks de 16 beats (ahorra memoria)
    chunk_beats = 16
    num_chunks = (total_beats + chunk_beats - 1) // chunk_beats
    
    for chunk_idx in range(num_chunks):
        start_beat = chunk_idx * chunk_beats
        end_beat = min(start_beat + chunk_beats, total_beats)
        actual_beats = end_beat - start_beat
        
        samples = actual_beats * spb
        melody = np.zeros(samples, dtype=np.float32)
        bass = np.zeros(samples, dtype=np.float32)
        drums = np.zeros(samples, dtype=np.float32)
        
        def note(freq, rel_beat, dur, vol, arr):
            s = int(rel_beat * spb)
            e = int((rel_beat + dur) * spb)
            e = min(e, samples)
            if s >= samples or e <= 0 or freq <= 0:
                return
            s = max(0, s)
            
            length = e - s
            if length <= 0:
                return
                
            t = np.linspace(0, dur * beat, length, False)
            # Onda simple pero efectiva
            tone = np.sin(2 * np.pi * freq * t)
            if freq > 200:  # Agregar armónicos a frecuencias altas
                tone += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
            
            # Envolvente simple
            attack = min(100, length // 4)
            env = np.ones(length)
            env[:attack] = np.linspace(0, 1, attack)
            
            arr[s:e] += tone * env * vol
        
        # Generar según sección
        abs_start = start_beat
        
        for beat_in_chunk in range(0, actual_beats, 4):
            abs_beat = abs_start + beat_in_chunk
            local = beat_in_chunk
            
            # Batería base
            if local % 4 == 0:
                # Kick
                s = int(local * spb)
                if s < samples:
                    kick_len = min(int(0.1 * sr), samples - s)
                    if kick_len > 100:
                        t = np.linspace(0, kick_len/sr, kick_len, False)
                        f = 60 * np.exp(-t * 30)
                        drums[s:s+kick_len] += np.sin(2 * np.pi * f * t) * np.exp(-t * 10) * 0.5
            
            if local % 4 == 2:
                # Snare
                s = int(local * spb)
                if s < samples and s + 2000 < samples:
                    noise = np.random.randn(2000).astype(np.float32) * 0.3
                    drums[s:s+2000] += noise * np.exp(np.linspace(0, -5, 2000))
            
            # Melodía según sección
            if abs_beat < 32:  # Intro
                if local % 8 == 0:
                    note(440, local, 4, 0.3, melody)
                    note(220, local, 8, 0.3, bass)
            
            elif abs_beat < 96:  # Verso 1 (Am)
                pattern = (local // 2) % 4
                freqs = [440, 523.25, 659.25, 440]
                note(freqs[pattern], local, 1, 0.4, melody)
                if local % 8 == 0:
                    note(110, local, 8, 0.35, bass)
            
            elif abs_beat < 160:  # Puente
                if local % 4 == 0:
                    note(880, local, 2, 0.35, melody)
                    note(220, local, 4, 0.3, bass)
            
            elif abs_beat < 224:  # Coro 1 (Cm)
                freqs = [523.25, 622.25, 783.99, 1046.5]
                pattern = (local // 2) % 4
                note(freqs[pattern], local, 1, 0.5, melody)
                if local % 8 == 0:
                    note(130.81, local, 8, 0.4, bass)
            
            elif abs_beat < 288:  # Verso 2
                if local % 2 == 0:
                    note(440 + (local % 4) * 50, local, 0.5, 0.4, melody)
                if local % 8 == 0:
                    note(110, local, 8, 0.35, bass)
            
            elif abs_beat < 352:  # Coro 2
                note(523.25, local, 0.5, 0.5, melody)
                note(622.25, local + 0.5, 0.5, 0.55, melody)
                if local % 4 == 0:
                    note(130.81, local, 4, 0.45, bass)
            
            else:  # Outro
                fade = max(0.1, 0.4 - (abs_beat - 352) / 32 * 0.35)
                if local % 4 == 0:
                    note(440, local, 4, fade, melody)
                    note(220, local, 4, fade * 0.8, bass)
        
        # Mezclar
        mix = melody * 0.8 + bass * 0.7 + drums * 0.5
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = mix / peak * 0.9
        
        # Convertir a int16 stereo
        stereo = np.column_stack((mix, mix))
        stereo_int = (stereo * 32767).astype(np.int16)
        wav.writeframes(stereo_int.tobytes())
        
        # Progreso
        percent = int((chunk_idx + 1) / num_chunks * 100)
        print(f"Progreso: {percent}%", end='\r')
    
    print("\n¡Listo!")

print(f"Archivo generado: {output_file}")
print(f"Duración: 3 minutos")
