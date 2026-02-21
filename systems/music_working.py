"""
Music Working - Sistema que funciona con respaldo
==================================================
Intenta cargar el archivo de 3 minutos, si falla genera uno simple.
"""
import pygame
import os
import numpy as np
import wave


def generate_simple_loop():
    """Genera un loop simple de 16 segundos que suena bien."""
    print("[MUSIC] Generando loop simple...")
    
    sr = 44100
    duration = 16.0
    samples = int(sr * duration)
    bpm = 120
    beat = 60 / bpm
    spb = int(sr * beat)
    
    wave_data = np.zeros(samples, dtype=np.float32)
    
    def note(freq, start_beat, dur_beats, vol=0.5):
        start = int(start_beat * spb)
        end = int((start_beat + dur_beats) * spb)
        end = min(end, samples)
        if start >= samples or freq <= 0:
            return
        
        length = end - start
        if length <= 0:
            return
            
        t = np.linspace(0, dur_beats * beat, length, False)
        # Onda simple
        tone = np.sin(2 * np.pi * freq * t)
        if freq > 300:
            tone += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        
        # Envolvente
        attack = min(int(0.02 * sr), length // 8)
        env = np.ones(length)
        env[:attack] = np.linspace(0, 1, attack)
        
        wave_data[start:end] += tone * env * vol
    
    # Melodía "tutururu" simple
    # "tu tu ruuu"
    note(659.25, 0, 0.25, 0.4)      # E5
    note(659.25, 0.5, 0.25, 0.4)    # E5
    note(523.25, 1.0, 0.75, 0.5)    # C5
    
    # "tu-tu ru-ru"
    note(440, 2.0, 0.25, 0.4)       # A4
    note(440, 2.5, 0.25, 0.4)       # A4
    note(523.25, 3.0, 0.25, 0.4)    # C5
    note(523.25, 3.5, 0.25, 0.4)    # C5
    
    # "tutururu"
    note(659.25, 4.0, 0.25, 0.4)    # E5
    note(659.25, 4.5, 0.25, 0.4)    # E5
    note(523.25, 5.0, 0.25, 0.4)    # C5
    note(523.25, 5.5, 0.25, 0.4)    # C5
    
    # "ruuu" en A
    note(440, 6.0, 0.5, 0.5)        # A4
    note(440, 6.5, 0.5, 0.4)        # A4
    note(440, 7.0, 1.0, 0.35)       # A4 (sostenida)
    
    # Bajo
    note(110, 0, 2, 0.35)           # A2
    note(87.31, 2, 2, 0.3)          # F2
    note(98, 4, 2, 0.3)             # G2
    note(110, 6, 2, 0.35)           # A2
    
    # Batería simple
    for beat in range(0, 16, 4):
        s = int(beat * spb)
        if s < samples:
            # Kick
            kick_len = min(int(0.1 * sr), samples - s)
            if kick_len > 100:
                t = np.linspace(0, kick_len/sr, kick_len, False)
                f = 60 * np.exp(-t * 30)
                wave_data[s:s+kick_len] += np.sin(2 * np.pi * f * t) * np.exp(-t * 10) * 0.5
        
        # Snare
        snare_s = int((beat + 2) * spb)
        if snare_s < samples:
            snare_len = min(int(0.08 * sr), samples - snare_s)
            if snare_len > 100:
                noise = np.random.randn(snare_len).astype(np.float32) * 0.3
                env = np.exp(np.linspace(0, -5, snare_len))
                wave_data[snare_s:snare_s+snare_len] += noise * env * 0.4
    
    # Normalizar
    peak = np.max(np.abs(wave_data))
    if peak > 0:
        wave_data = wave_data / peak * 0.9
    
    # Guardar como WAV
    stereo = np.column_stack((wave_data, wave_data))
    stereo_int = (stereo * 32767).astype(np.int16)
    
    with wave.open('simple_loop.wav', 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(stereo_int.tobytes())
    
    print("[MUSIC] Guardado: simple_loop.wav")
    return 'simple_loop.wav'


def start_music(volume=0.5):
    """Inicia música con respaldo."""
    
    # Inicializar mixer
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        except Exception as e:
            print(f"[MUSIC ERROR] No se pudo inicializar mixer: {e}")
            return
    
    music_file = None
    
    # Intentar archivo de 3 minutos
    if os.path.exists('epic_song_3min.wav'):
        try:
            # Verificar que se puede cargar
            pygame.mixer.music.load('epic_song_3min.wav')
            music_file = 'epic_song_3min.wav'
            print(f"[MUSIC] Usando canción de 3 minutos")
        except Exception as e:
            print(f"[MUSIC] No se pudo cargar canción larga: {e}")
    
    # Si falló, intentar loop simple
    if music_file is None:
        if not os.path.exists('simple_loop.wav'):
            generate_simple_loop()
        
        if os.path.exists('simple_loop.wav'):
            try:
                pygame.mixer.music.load('simple_loop.wav')
                music_file = 'simple_loop.wav'
                print(f"[MUSIC] Usando loop simple")
            except Exception as e:
                print(f"[MUSIC ERROR] {e}")
                return
    
    if music_file:
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        print(f"[MUSIC] Reproduciendo (vol: {volume})")
    else:
        print("[MUSIC ERROR] No se pudo cargar ningún archivo")


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
    start_music(0.5)
    time.sleep(5)
    stop_music()
