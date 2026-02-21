"""
Music Loop Perfect - Bucle verdaderamente sin gaps
===================================================
Genera audio y recorta TODO el silencio al final.
"""
import pygame
import numpy as np
import wave
import os


def generate_perfect_loop():
    """Genera loop de 8 segundos SIN silencio al final."""
    
    sr = 44100
    max_duration = 10.0  # Generar un poco más para luego recortar
    max_samples = int(sr * max_duration)
    
    bpm = 120
    beat = 60 / bpm
    spb = int(sr * beat)
    
    # Generar en array más grande
    wave_data = np.zeros(max_samples, dtype=np.float32)
    
    def note(freq, start_beat, dur_beats, vol=0.5):
        start = int(start_beat * spb)
        end = int((start_beat + dur_beats) * spb)
        end = min(end, max_samples)
        if start >= max_samples or freq <= 0 or start < 0:
            return
        
        length = end - start
        if length <= 0:
            return
            
        t = np.linspace(0, dur_beats * beat, length, False)
        sq = np.where((t * freq) % 1.0 < 0.5, 1.0, -1.0) * 0.6
        si = np.sin(2 * np.pi * freq * t) * 0.4
        tone = sq + si
        
        attack = min(int(0.02 * sr), length // 10)
        env = np.ones(length)
        env[:attack] = np.linspace(0, 1, attack)
        
        wave_data[start:end] += tone * env * vol
    
    # === MELODÍA DE EXACTAMENTE 8 COMPASES (8 segundos) ===
    
    # Compás 1: "tu tu ruuu"
    note(659.25, 0, 0.25, 0.4)      # E5
    note(659.25, 0.5, 0.25, 0.4)    # E5
    note(523.25, 1.0, 0.75, 0.5)    # C5 - larga
    
    # Compás 2: "tu-tu ru-ru"
    note(440, 2.0, 0.25, 0.4)       # A4
    note(440, 2.5, 0.25, 0.4)       # A4
    note(523.25, 3.0, 0.25, 0.4)    # C5
    note(523.25, 3.5, 0.25, 0.4)    # C5
    
    # Compás 3: "tutururu"
    note(659.25, 4.0, 0.25, 0.4)    # E5
    note(659.25, 4.5, 0.25, 0.4)    # E5
    note(523.25, 5.0, 0.25, 0.4)    # C5
    note(523.25, 5.5, 0.25, 0.4)    # C5
    
    # Compás 4: "ruuu" EN A (nota de apertura del bucle)
    note(440, 6.0, 0.5, 0.5)        # A4
    note(440, 6.5, 0.5, 0.4)        # A4
    # ÚLTIMA NOTA: A4 corta que conecta con E5 del inicio
    note(440, 7.0, 0.75, 0.35)      # A4 - termina justo antes del beat 8
    
    # Bajo (más corto, termina antes)
    note(110, 0, 1.5, 0.35)         # A2
    note(87.31, 2, 1.5, 0.3)        # F2
    note(98, 4, 1.5, 0.3)           # G2
    note(110, 6, 1.5, 0.35)         # A2 - termina en 7.5
    
    # Batería sólo hasta el segundo 7.5
    for beat in range(0, 30, 4):  # Hasta beat 7.5
        s = int(beat / 4 * spb)
        if s < int(7.5 * sr):
            kick_len = min(int(0.1 * sr), max_samples - s)
            if kick_len > 100:
                t = np.linspace(0, kick_len/sr, kick_len, False)
                f = 60 * np.exp(-t * 30)
                wave_data[s:s+kick_len] += np.sin(2 * np.pi * f * t) * np.exp(-t * 10) * 0.5
        
        snare_s = int((beat + 2) / 4 * spb)
        if snare_s < int(7.5 * sr) and snare_s < max_samples:
            snare_len = min(int(0.08 * sr), max_samples - snare_s)
            if snare_len > 100:
                noise = np.random.randn(snare_len).astype(np.float32) * 0.3
                env = np.exp(np.linspace(0, -5, snare_len))
                wave_data[snare_s:snare_s+snare_len] += noise * env * 0.4
    
    # === RECORTAR SILENCIO AL FINAL ===
    
    # Normalizar primero
    peak = np.max(np.abs(wave_data))
    if peak > 0:
        wave_data = wave_data / peak * 0.9
    
    # Buscar último sample significativo
    threshold = 0.001  # Después de normalizar
    last_sample = len(wave_data)
    
    for i in range(len(wave_data) - 1, -1, -1):
        if abs(wave_data[i]) > threshold:
            last_sample = i + 1  # +1 para incluir este sample
            break
    
    # Recortar a múltiplo de samples por beat para bucle perfecto
    target_samples = int(8 * sr)  # Exactamente 8 segundos
    actual_samples = min(last_sample, target_samples)
    
    # Asegurar que termina en cruce por cero para evitar click
    wave_trimmed = wave_data[:actual_samples]
    
    # Suavizar últimas muestras para evitar click
    fade_samples = min(int(0.01 * sr), len(wave_trimmed) // 10)
    if fade_samples > 0:
        wave_trimmed[-fade_samples:] *= np.linspace(1, 0.8, fade_samples)
    
    print(f"[MUSIC] Generado: {len(wave_trimmed)/sr:.2f}s, recortado de {last_sample/sr:.2f}s")
    
    return wave_trimmed, sr


def save_and_play(volume=0.5):
    """Genera, guarda y reproduce el loop perfecto."""
    
    # Inicializar
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    
    print("[MUSIC] Generando loop perfecto (8 segundos)...")
    wave_data, sr = generate_perfect_loop()
    
    # Guardar como WAV
    stereo = np.column_stack((wave_data, wave_data))
    stereo_int = (stereo * 32767).astype(np.int16)
    
    with wave.open('perfect_loop.wav', 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(stereo_int.tobytes())
    
    print("[MUSIC] Guardado: perfect_loop.wav")
    
    # Reproducir
    pygame.mixer.music.load('perfect_loop.wav')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
    
    print(f"[MUSIC] Reproduciendo loop perfecto (vol: {volume})")


def start_music(volume=0.5):
    """Inicia música."""
    
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        except:
            return
    
    # Siempre regenerar para asegurar calidad
    save_and_play(volume)


def stop_music():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def set_volume(vol):
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(vol)


def is_playing():
    return pygame.mixer.music.get_busy()


if __name__ == "__main__":
    import time
    pygame.init()
    
    print("Test de 20 segundos (2.5 loops)...")
    start_music(0.5)
    
    for i in range(20):
        time.sleep(1)
        if (i + 1) % 8 == 0:
            print(f"  Loop {(i+1)//8} completado")
    
    stop_music()
    print("Fin")
