"""
Music Fixed - Silencio al final ELIMINADO
==========================================
El problema: El archivo tenía 4s de música + 4s de silencio.
Solución: Detectar y recortar el silencio automáticamente.
"""
import numpy as np
import pygame
import soundfile as sf
import os


def generate_tutururu_fixed():
    """
    Genera la melodía y recorta el silencio al final.
    """
    sr = 44100
    
    # Generar en duración extendida
    max_duration = 10.0
    samples = int(sr * max_duration)
    
    bpm = 120
    beat = 60 / bpm
    spb = int(sr * beat)
    
    wave = np.zeros(samples, dtype=float)
    
    def note(freq, start_beat, dur_beats, vol=0.5):
        start = int(start_beat * spb)
        end = int((start_beat + dur_beats) * spb)
        end = min(end, samples)
        if start >= samples or freq <= 0:
            return
        
        length = end - start
        t = np.linspace(0, dur_beats * beat, length, False)
        sq = np.where((t * freq) % 1.0 < 0.5, 1.0, -1.0)
        si = np.sin(2 * np.pi * freq * t)
        tone = sq * 0.6 + si * 0.4
        
        attack = min(int(0.02 * sr), length // 10)
        env = np.ones(length)
        env[:attack] = np.linspace(0, 1, attack)
        
        wave[start:end] += tone * env * vol
    
    # "tu tu ruuu" (0-2s)
    note(659.25, 0, 0.25, 0.4)      # E5
    note(659.25, 0.5, 0.25, 0.4)    # E5
    note(523.25, 1.0, 0.75, 0.5)    # C5
    
    # "tu-tu ru-ru" (2-4s)
    note(440, 2.0, 0.25, 0.4)       # A4
    note(440, 2.5, 0.25, 0.4)       # A4
    note(523.25, 3.0, 0.25, 0.4)    # C5
    note(523.25, 3.5, 0.25, 0.4)    # C5
    
    # "tutururu" (4-6s)
    note(659.25, 4.0, 0.25, 0.4)    # E5
    note(659.25, 4.5, 0.25, 0.4)    # E5
    note(523.25, 5.0, 0.25, 0.4)    # C5
    note(523.25, 5.5, 0.25, 0.4)    # C5
    
    # "ruuu" en A (6-8s) - NOTA FINAL SOSTENIDA HASTA EL FINAL
    note(440, 6.0, 0.5, 0.5)        # A4
    note(440, 6.5, 0.5, 0.4)        # A4
    note(440, 7.0, 1.0, 0.35)       # A4 - sostenida hasta 8s
    
    # Bajo
    note(110, 0, 2, 0.35)           # A2
    note(87.31, 2, 2, 0.3)          # F2
    note(98, 4, 2, 0.3)             # G2
    note(110, 6, 2, 0.35)           # A2
    
    # Normalizar
    peak = np.max(np.abs(wave))
    if peak > 0:
        wave = wave / peak * 0.9
    
    # RECORTAR SILENCIO AL FINAL
    threshold = 0.001
    last_sample = len(wave)
    
    for i in range(len(wave) - 1, -1, -1):
        if np.abs(wave[i]) > threshold:
            last_sample = i + 1  # +1 para incluir esta muestra
            break
    
    wave_trimmed = wave[:last_sample]
    
    print(f"[MUSIC] Original: {len(wave)/sr:.2f}s")
    print(f"[MUSIC] Recortado: {len(wave_trimmed)/sr:.2f}s")
    print(f"[MUSIC] Silencio eliminado: {(len(wave)-len(wave_trimmed))/sr:.2f}s")
    
    return wave_trimmed


def start_music(volume=0.5):
    """Inicia música con loop perfecto (silencio recortado)."""
    
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    
    # Regenerar siempre para asegurar que está recortado
    print("[MUSIC] Generando audio corregido...")
    wave = generate_tutururu_fixed()
    
    # Guardar como OGG
    sf.write('bg_music_fixed.ogg', wave, 44100, format='OGG')
    print("[MUSIC] Guardado bg_music_fixed.ogg")
    
    # Reproducir con loop nativo
    pygame.mixer.music.load('bg_music_fixed.ogg')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
    
    print(f"[MUSIC] OK - Loop infinito (vol: {volume})")


def stop_music():
    pygame.mixer.music.stop()


def set_volume(vol):
    pygame.mixer.music.set_volume(vol)


def is_playing():
    return pygame.mixer.music.get_busy()


if __name__ == "__main__":
    import time
    pygame.init()
    
    print("=" * 50)
    print("TEST: Audio con silencio recortado")
    print("=" * 50)
    
    start_music(0.5)
    
    print("\nEscuchando 16 segundos...")
    for i in range(16):
        time.sleep(1)
    
    stop_music()
    print("\n¿Ahora funciona el loop continuo?")
