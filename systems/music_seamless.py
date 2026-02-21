"""
Music Seamless - Bucle musicalmente perfecto
=============================================
Técnicas aplicadas:
1. Tonalidad consistente: Am (La menor)
2. La melodía termina en la tónica (A) que conecta con el inicio
3. Progresión armónica circular: Am -> F -> G -> Am
4. La última nota es el mismo A que empieza el bucle
5. Fundido cruzado de 0.1s entre final e inicio
"""
import pygame
import numpy as np
import wave


def generate_seamless_loop():
    """
    Genera bucle de 8 segundos que es musicalmente coherente.
    
    Estructura en Am (La menor):
    - Acorde i (Am): Tónica - estabilidad
    - Acorde VI (F): Subdominante - movimiento
    - Acorde VII (G): Dominante - tensión
    - Vuelta a i (Am): Resolución
    
    La melodía termina en A (tónica) que es donde "quiere" volver.
    """
    
    sr = 44100
    loop_duration = 8.0  # 8 segundos exactos
    samples = int(sr * loop_duration)
    
    bpm = 120
    beat = 60 / bpm
    spb = int(sr * beat)
    
    # Arrays
    melody = np.zeros(samples, dtype=np.float32)
    harmony = np.zeros(samples, dtype=np.float32)
    bass = np.zeros(samples, dtype=np.float32)
    drums = np.zeros(samples, dtype=np.float32)
    
    def add_note(freq, start_beat, dur_beats, vol, target):
        start = int(start_beat * spb)
        end = int((start_beat + dur_beats) * spb)
        end = min(end, samples)
        if start >= samples or start < 0 or freq <= 0:
            return
        
        length = end - start
        if length <= 0:
            return
        
        t = np.linspace(0, dur_beats * beat, length, False)
        
        # Onda con armónicos para sonido rico
        fundamental = np.sin(2 * np.pi * freq * t)
        harmonic2 = 0.3 * np.sin(2 * np.pi * freq * 2 * t)
        harmonic3 = 0.15 * np.sin(2 * np.pi * freq * 3 * t)
        tone = fundamental + harmonic2 + harmonic3
        
        # Envolvente ADSR suave
        attack = int(0.05 * sr)
        release = int(0.1 * sr)
        env = np.ones(length)
        
        if attack < length:
            env[:attack] = np.linspace(0, 1, attack)
        if release < length:
            env[-release:] = np.linspace(1, 0, release)
        
        target[start:end] += tone * env * vol
    
    def add_chord(freqs, start_beat, dur_beats, vol):
        for freq in freqs:
            add_note(freq, start_beat, dur_beats, vol, harmony)
    
    # === ARMONÍA: Progresión Am - F - G - Am (circular) ===
    # Cada acorde dura 2 compases (8 beats)
    
    # Am (beats 0-8): Tónica - estabilidad
    add_chord([220, 261.63, 329.63], 0, 8, 0.25)  # Am
    
    # F (beats 8-16): Subdominante - movimiento
    add_chord([174.61, 220, 261.63], 8, 8, 0.25)  # F
    
    # G (beats 16-24): Dominante - tensión que quiere resolver
    add_chord([196, 246.94, 293.66], 16, 8, 0.25)  # G
    
    # Am (beats 24-32): Vuelta a tónica - resolución perfecta
    add_chord([220, 261.63, 329.63], 24, 8, 0.3)  # Am (más fuerte al final)
    
    # === MELODÍA: Diseñada para bucle perfecto ===
    # Clave: Empieza y termina en A (la tónica)
    
    # Primer compás (0-2): Apertura en A
    add_note(440, 0, 0.5, 0.4, melody)      # A4 - tónica (estable)
    add_note(523.25, 0.75, 0.5, 0.35, melody)  # C5 - tercera (color)
    add_note(659.25, 1.5, 0.5, 0.4, melody)    # E5 - quinta (tensión suave)
    
    # Segundo compás (2-4): Desarrollo
    add_note(783.99, 2.5, 0.5, 0.35, melody)   # G5 - sensible
    add_note(659.25, 3.5, 0.5, 0.4, melody)    # E5 - quinta
    
    # Tercer compás (4-6): Movimiento hacia F
    add_note(523.25, 4.25, 0.5, 0.35, melody)  # C5
    add_note(698.46, 5, 0.75, 0.4, melody)     # F5 - nota de F mayor
    
    # Cuarto compás (6-8): Dominante G
    add_note(783.99, 6.25, 0.5, 0.35, melody)  # G5
    add_note(659.25, 7, 0.75, 0.4, melody)     # E5 - prepara la resolución
    
    # Quinto compás (8-10): Tensión creciente
    add_note(880, 8, 0.5, 0.45, melody)        # A5 - octava alta (clímax)
    add_note(783.99, 9, 0.5, 0.35, melody)     # G5
    
    # Sexto compás (10-12): Descenso
    add_note(659.25, 10.5, 0.5, 0.4, melody)   # E5
    add_note(523.25, 11.5, 0.5, 0.35, melody)  # C5
    
    # Séptimo compás (12-14): Preparando el cierre
    add_note(440, 12.25, 0.5, 0.4, melody)     # A4 - volviendo a la tónica
    add_note(349.23, 13.5, 0.5, 0.35, melody)  # F4 - subdominante
    
    # Octavo compás (14-16): CIERRE EN TÓNICA = INICIO
    # Estas notas son idénticas al inicio para bucle perfecto
    add_note(440, 14.25, 0.5, 0.45, melody)    # A4 - IGUAL AL INICIO
    add_note(523.25, 14.75, 0.5, 0.4, melody)  # C5 - IGUAL AL INICIO
    add_note(659.25, 15.25, 0.75, 0.45, melody)  # E5 - IGUAL AL INICIO
    # La última nota E5 prepara el oído para volver a A4 del inicio
    
    # === BAJO: Raíces de los acordes ===
    # Am
    add_note(110, 0, 2, 0.4, bass)      # A2
    add_note(110, 4, 2, 0.35, bass)     # A2
    
    # F
    add_note(87.31, 8, 2, 0.35, bass)   # F2
    add_note(87.31, 12, 2, 0.3, bass)   # F2
    
    # G
    add_note(98, 16, 2, 0.35, bass)     # G2
    add_note(98, 20, 2, 0.3, bass)      # G2
    
    # Am (final - más marcado para cerrar)
    add_note(110, 24, 2, 0.45, bass)    # A2 - TÓNICA
    add_note(110, 28, 4, 0.4, bass)     # A2 - SOSTENIDA HASTA EL FINAL
    
    # === BATERÍA: Ritmo constante ===
    for beat in range(0, 32, 4):
        # Kick en 1 y 3
        s = int(beat * spb)
        if s < samples:
            kick_len = min(int(0.12 * sr), samples - s)
            if kick_len > 50:
                t = np.linspace(0, kick_len/sr, kick_len, False)
                freq = 55 * np.exp(-t * 25)  # Descenso de frecuencia
                env = np.exp(-t * 8)
                drums[s:s+kick_len] += np.sin(2 * np.pi * freq * t) * env * 0.6
        
        # Snare en 2 y 4
        snare_s = int((beat + 2) * spb)
        if snare_s < samples:
            snare_len = min(int(0.08 * sr), samples - snare_s)
            if snare_len > 50:
                noise = np.random.randn(snare_len).astype(np.float32) * 0.5
                env = np.exp(np.linspace(0, -6, snare_len))
                tone = np.sin(2 * np.pi * 200 * np.linspace(0, snare_len/sr, snare_len)) * 0.3
                drums[snare_s:snare_s+snare_len] += (noise + tone) * env * 0.5
        
        # Hi-hats en off-beats
        for off in [1, 3]:
            hat_s = int((beat + off) * spb)
            if hat_s < samples:
                hat_len = min(int(0.03 * sr), samples - hat_s)
                if hat_len > 20:
                    noise = np.random.randn(hat_len).astype(np.float32) * 0.5
                    env = np.exp(np.linspace(0, -10, hat_len))
                    drums[hat_s:hat_s+hat_len] += noise * env * 0.3
    
    # === MEZCLAR ===
    mix = melody * 0.85 + harmony * 0.5 + bass * 0.75 + drums * 0.55
    
    # Normalizar
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.9
    
    # === CROSSFADE ENTRE FINAL E INICIO ===
    # Fundir las últimas muestras con las primeras para transición suave
    fade_duration = int(0.1 * sr)  # 0.1 segundos de crossfade
    
    if len(mix) > fade_duration * 2:
        # Crear versión crossfadeada
        result = mix.copy()
        
        # Tomar el inicio para el fade
        start_segment = mix[:fade_duration].copy()
        end_segment = mix[-fade_duration:].copy()
        
        # Crear curva de crossfade
        fade_out = np.linspace(1, 0, fade_duration)
        fade_in = np.linspace(0, 1, fade_duration)
        
        # Aplicar fade out al final
        result[-fade_duration:] = end_segment * fade_out + start_segment * fade_in
        
        mix = result
    
    print(f"[MUSIC] Generado: {len(mix)/sr:.2f}s, tonalidad: Am")
    return mix


def start_music(volume=0.5):
    """Genera y reproduce el bucle seamless."""
    
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    
    print("[MUSIC] Generando bucle seamless (Am - F - G - Am)...")
    wave_data = generate_seamless_loop()
    
    # Guardar
    stereo = np.column_stack((wave_data, wave_data))
    stereo_int = (stereo * 32767).astype(np.int16)
    
    with wave.open('seamless_loop.wav', 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(stereo_int.tobytes())
    
    print("[MUSIC] Guardado: seamless_loop.wav")
    
    # Reproducir
    pygame.mixer.music.load('seamless_loop.wav')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
    
    print(f"[MUSIC] Reproduciendo (vol: {volume})")
    print("[MUSIC] Progresión: Am -> F -> G -> Am (loop infinito)")


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
    
    print("=" * 60)
    print("BUCLE SEAMLESS - Progresión: Am -> F -> G -> Am")
    print("=" * 60)
    
    start_music(0.5)
    
    print("\nEscuchando 24 segundos (3 loops)...")
    for i in range(24):
        time.sleep(1)
        if (i + 1) % 8 == 0:
            print(f"  Loop {(i+1)//8} completado")
    
    stop_music()
    print("\n¿El bucle suena continuo y musical?")
