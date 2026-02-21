"""
Music Dopamine - Canción diseñada para activar dopamina
========================================================
Elementos neurocientíficos para engagement máximo:

1. HOOK MEMORABLE - Frase de 4 notas que se repite
2. BPM 128 - Ritmo bailable óptimo
3. BUILD + DROP - Anticipación → Recompensa
4. CONTRASTE Dinámico - Suave vs Explosivo
5. SÍNCOPLA - Groove que hace mover la cabeza
6. PROGRESIÓN: Em → C → G → D (épica, usada en éxitos pop)

Estructura:
0:00-0:04  - Intro (ambiente)
0:04-0:08  - Build Up (tensión creciente)
0:08-0:16  - DROP/Coro (explosión de energía)
0:16-0:24  - Break (calma)
0:24-0:28  - Build Up 2
0:28-0:32  - DROP Final (máxima energía)
"""
import pygame
import numpy as np
import wave


def generate_dopamine_loop():
    """
    Genera bucle de 32 segundos diseñado para máxima dopamina.
    """
    
    sr = 44100
    loop_duration = 32.0  # 32 segundos para más desarrollo
    samples = int(sr * loop_duration)
    
    bpm = 128  # Ritmo bailable óptimo
    beat = 60 / bpm
    spb = int(sr * beat)
    
    # Arrays
    melody = np.zeros(samples, dtype=np.float32)
    harmony = np.zeros(samples, dtype=np.float32)
    bass = np.zeros(samples, dtype=np.float32)
    drums = np.zeros(samples, dtype=np.float32)
    fx = np.zeros(samples, dtype=np.float32)  # Efectos especiales
    
    def add_note(freq, start_beat, dur_beats, vol, target, waveform='rich'):
        start = int(start_beat * spb)
        end = int((start_beat + dur_beats) * spb)
        end = min(end, samples)
        if start >= samples or start < 0 or freq <= 0:
            return
        
        length = end - start
        if length <= 0:
            return
        
        t = np.linspace(0, dur_beats * beat, length, False)
        
        # Onda rica con múltiples armónicos
        if waveform == 'rich':
            tone = np.sin(2 * np.pi * freq * t)
            tone += 0.5 * np.sin(2 * np.pi * freq * 2 * t)
            tone += 0.25 * np.sin(2 * np.pi * freq * 3 * t)
            tone += 0.125 * np.sin(2 * np.pi * freq * 4 * t)
        elif waveform == 'bass':
            tone = np.sin(2 * np.pi * freq * t)
            tone += 0.3 * np.sin(2 * np.pi * freq * 0.5 * t)  # Sub
        else:
            tone = np.sin(2 * np.pi * freq * t)
        
        # Envolvente expresiva
        attack = int(0.02 * sr)
        release = int(0.15 * sr)
        env = np.ones(length)
        
        if attack < length:
            env[:attack] = np.linspace(0, 1, attack) ** 0.5  # Curva suave
        if release < length:
            env[-release:] = np.linspace(1, 0, release) ** 2
        
        target[start:end] += tone * env * vol
    
    def add_chord(freqs, start_beat, dur_beats, vol):
        for freq in freqs:
            add_note(freq, start_beat, dur_beats, vol, harmony)
    
    # === ARMONÍA: Progresión épica Em → C → G → D ===
    # Esta progresión está en TODOS los éxitos pop/rock épicos
    
    # Em (beats 0-8) - Oscuro, épico
    add_chord([164.81, 196, 246.94], 0, 8, 0.2)
    # C (beats 8-16) - Brillante, elevación
    add_chord([261.63, 329.63, 392], 8, 8, 0.25)
    # G (beats 16-24) - Potente, dominante
    add_chord([196, 246.94, 293.66], 16, 8, 0.25)
    # D (beats 24-32) - Tensión que resuelve a Em
    add_chord([293.66, 369.99, 440], 24, 8, 0.3)
    
    # === MELODÍA: EL HOOK (lo que hace pegajosa la canción) ===
    # Patrón: E5-D5-E5-B4 (memorable, fácil de tararear)
    
    # INTRO SUAVE (beats 0-2)
    add_note(329.63, 0.5, 0.5, 0.3, melody)   # E4
    add_note(392, 1.5, 0.5, 0.35, melody)     # G4
    
    # BUILD UP - Tensión creciente (beats 2-8)
    for i in range(6):  # 6 notas ascendentes
        note_beat = 2 + i * 0.5
        vol = 0.3 + i * 0.03  # Creciente
        pitch = 329.63 + i * 50  # Ascendente
        add_note(pitch, note_beat, 0.25, vol, melody)
    
    # === DROP/CORO - EXPLOSIÓN DE ENERGÍA (beats 8-16) ===
    # El HOOK principal: E5-D5-E5-B4 (¡PEGADIZO!)
    
    # Primera frase del hook (8-10)
    add_note(659.25, 8, 0.5, 0.6, melody)     # E5 - FUERTE
    add_note(587.33, 8.5, 0.25, 0.5, melody)  # D5
    add_note(659.25, 8.75, 0.5, 0.6, melody)  # E5
    add_note(493.88, 9.25, 0.75, 0.55, melody) # B4
    
    # Variación (10-12)
    add_note(659.25, 10.5, 0.5, 0.6, melody)
    add_note(783.99, 11, 0.5, 0.55, melody)   # G5
    add_note(880, 11.5, 0.5, 0.65, melody)    # A5 - CLIMAX
    
    # Respuesta del hook (12-16)
    add_note(659.25, 12.5, 0.5, 0.6, melody)
    add_note(587.33, 13, 0.25, 0.5, melody)
    add_note(659.25, 13.25, 0.5, 0.6, melody)
    add_note(493.88, 13.75, 1.25, 0.55, melody)
    
    # BREAK - Calma (beats 16-20)
    add_note(329.63, 17, 1, 0.3, melody)      # E4 - bajo
    add_note(392, 18, 1, 0.35, melody)        # G4
    add_note(329.63, 19, 1, 0.3, melody)
    
    # BUILD UP 2 (beats 20-24)
    for i in range(8):
        note_beat = 20 + i * 0.25
        vol = 0.25 + i * 0.04
        add_note(493.88 + i * 30, note_beat, 0.2, vol, melody)
    
    # DROP FINAL - Máxima energía (beats 24-32)
    # Hook en octava alta + acordes completos
    add_note(1318.51, 24.5, 0.5, 0.5, melody)  # E6 - ¡AGUDO!
    add_note(1174.66, 25, 0.25, 0.45, melody)  # D6
    add_note(1318.51, 25.25, 0.5, 0.5, melody) # E6
    add_note(987.77, 25.75, 0.75, 0.45, melody) # B5
    
    # Power chords finales
    add_note(659.25, 27, 1, 0.55, melody)
    add_note(783.99, 28, 1, 0.5, melody)
    add_note(880, 29, 1, 0.55, melody)
    add_note(659.25, 30, 2, 0.5, melody)       # Sostenido final
    
    # === BAJO - Groove pegajoso ===
    # Patrón que hace mover la cabeza: bom-bom-clap
    
    for section in range(4):  # 4 secciones de 8 beats
        base = section * 8
        
        # Raíz del acorde según la sección
        if section == 0:  # Em
            root, fifth = 82.41, 123.47  # E2, B2
        elif section == 1:  # C
            root, fifth = 65.41, 98.00   # C2, G2
        elif section == 2:  # G
            root, fifth = 98.00, 146.83  # G2, D3
        else:  # D
            root, fifth = 73.42, 110.00  # D2, A2
        
        # Groove: Kick en 1 y 3, + octavas
        add_note(root, base, 0.5, 0.5, bass, 'bass')
        add_note(root, base + 2, 0.5, 0.45, bass, 'bass')
        add_note(root, base + 4, 0.5, 0.5, bass, 'bass')
        add_note(fifth, base + 6, 0.5, 0.4, bass, 'bass')
        
        # En el drop, más intenso
        if section in [1, 3]:  # Coros
            add_note(root * 2, base + 1, 0.25, 0.35, bass, 'bass')
            add_note(root * 2, base + 3, 0.25, 0.35, bass, 'bass')
            add_note(root * 2, base + 5, 0.25, 0.35, bass, 'bass')
    
    # === BATERÍA - Ritmo "four-on-the-floor" bailable ===
    for beat in range(0, 128, 4):  # Todo el loop
        # Kick en cada tiempo (four-on-the-floor)
        for kick_beat in [0, 2]:  # 1 y 3
            s = int((beat + kick_beat) * spb / 4)
            if s < samples:
                kick_len = min(int(0.15 * sr), samples - s)
                if kick_len > 100:
                    t = np.linspace(0, kick_len/sr, kick_len, False)
                    freq = 50 * np.exp(-t * 20)  # Kick profundo
                    env = np.exp(-t * 6)
                    drums[s:s+kick_len] += np.sin(2 * np.pi * freq * t) * env * 0.7
        
        # Snare en 2 y 4 (más fuerte en drops)
        for snare_offset in [1, 3]:
            snare_s = int((beat + snare_offset) * spb / 4)
            if snare_s < samples:
                # Detectar si es drop (beats 8-16 o 24-32)
                is_drop = (beat >= 32 and beat < 64) or (beat >= 96)
                snare_vol = 0.6 if is_drop else 0.45
                
                snare_len = min(int(0.08 * sr), samples - snare_s)
                if snare_len > 50:
                    noise = np.random.randn(snare_len).astype(np.float32) * 0.6
                    env = np.exp(np.linspace(0, -8, snare_len))
                    tone = np.sin(2 * np.pi * 180 * np.linspace(0, snare_len/sr, snare_len)) * 0.4
                    drums[snare_s:snare_s+snare_len] += (noise + tone) * env * snare_vol
        
        # Hi-hats en cada corchea
        for hat_offset in [0.5, 1.5, 2.5, 3.5]:
            hat_s = int((beat + hat_offset) * spb / 4)
            if hat_s < samples:
                hat_len = min(int(0.02 * sr), samples - hat_s)
                if hat_len > 20:
                    noise = np.random.randn(hat_len).astype(np.float32) * 0.5
                    env = np.exp(np.linspace(0, -12, hat_len))
                    drums[hat_s:hat_s+hat_len] += noise * env * 0.35
    
    # === FX - Efectos especiales para momentos clave ===
    
    # Riser antes del primer drop (beats 6-8)
    riser_start = int(6 * spb)
    riser_end = int(8 * spb)
    if riser_end > riser_start and riser_end < samples:
        riser_len = riser_end - riser_start
        t = np.linspace(0, 2 * beat, riser_len, False)
        freq = 200 + t * 400  # Sweep ascendente
        riser = np.sin(2 * np.pi * freq * t) * np.linspace(0, 0.3, riser_len)
        fx[riser_start:riser_end] += riser
    
    # Impact en el drop (beat 8)
    impact_s = int(8 * spb)
    impact_len = min(int(0.3 * sr), samples - impact_s)
    if impact_len > 100:
        noise = np.random.randn(impact_len).astype(np.float32)
        env = np.exp(np.linspace(0, -3, impact_len))
        fx[impact_s:impact_s+impact_len] += noise * env * 0.5
    
    # Riser antes del segundo drop (beats 22-24)
    riser2_start = int(22 * spb)
    riser2_end = int(24 * spb)
    if riser2_end > riser2_start and riser2_end < samples:
        riser2_len = riser2_end - riser2_start
        t = np.linspace(0, 2 * beat, riser2_len, False)
        freq = 200 + t * 500
        riser2 = np.sin(2 * np.pi * freq * t) * np.linspace(0, 0.35, riser2_len)
        fx[riser2_start:riser2_end] += riser2
    
    # === MEZCLA FINAL ===
    mix = (melody * 0.9 + harmony * 0.55 + bass * 0.8 + drums * 0.65 + fx * 0.7)
    
    # Compresión suave (limitador)
    threshold = 0.8
    mix = np.where(mix > threshold, threshold + (mix - threshold) * 0.3, mix)
    mix = np.where(mix < -threshold, -threshold + (mix + threshold) * 0.3, mix)
    
    # Normalizar final
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.95
    
    # Crossfade seamless
    fade_samples = int(0.08 * sr)
    if len(mix) > fade_samples * 2:
        start_seg = mix[:fade_samples].copy()
        end_seg = mix[-fade_samples:].copy()
        fade_out = np.linspace(1, 0, fade_samples)
        fade_in = np.linspace(0, 1, fade_samples)
        mix[-fade_samples:] = end_seg * fade_out + start_seg * fade_in
    
    print(f"[MUSIC] Generado: {len(mix)/sr:.1f}s de pura dopamina")
    return mix


def start_music(volume=0.5):
    """Genera y reproduce la canción dopaminérgica."""
    
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    
    print("[MUSIC] Generando canción dopaminérgica...")
    print("[MUSIC] BPM: 128 | Tonalidad: Em | Estructura: Intro->Build->Drop")
    
    wave_data = generate_dopamine_loop()
    
    # Guardar
    stereo = np.column_stack((wave_data, wave_data))
    stereo_int = (stereo * 32767).astype(np.int16)
    
    with wave.open('dopamine_loop.wav', 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(stereo_int.tobytes())
    
    print("[MUSIC] Guardado: dopamine_loop.wav")
    
    # Reproducir
    pygame.mixer.music.load('dopamine_loop.wav')
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)
    
    print(f"[MUSIC] DISFRUTA! (vol: {volume})")


def stop_music():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def set_volume(vol):
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(vol)


def is_playing():
    return pygame.mixer.music.get_busy()
