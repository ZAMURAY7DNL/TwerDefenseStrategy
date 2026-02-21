"""
Generador de Sonidos Procedural - Estilo Único Épico
=====================================================
Música original que mezcla chiptune con elementos orquestales.
Bucles perfectos con transiciones suaves.
"""
import numpy as np
import pygame
from typing import Optional, Tuple, List
import math
import random


class SoundGenerator:
    """Genera sonidos y música original procedural."""
    
    SAMPLE_RATE = 44100
    CHANNELS = 2
    
    def __init__(self):
        # Solo inicializar si no está listo
        if not pygame.mixer.get_init():
            pygame.mixer.init(
                frequency=self.SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=512
            )
        # Reservar canal 0 para música del SoundGenerator
        pygame.mixer.set_reserved(1)
        
        self._cache = {}
        self._music_playing = False
        self._music_channel = None
        self._music_sound = None
        self._loop_transition_active = False
    
    def _square_wave(self, t: np.ndarray, freq: float, duty: float = 0.5) -> np.ndarray:
        """Onda cuadrada."""
        return np.where((t * freq) % 1.0 < duty, 1.0, -1.0)
    
    def _triangle_wave(self, t: np.ndarray, freq: float) -> np.ndarray:
        """Onda triangular."""
        return 2 * np.abs(2 * ((t * freq) % 1.0) - 1) - 1
    
    def _saw_wave(self, t: np.ndarray, freq: float) -> np.ndarray:
        """Onda sierra."""
        return 2 * ((t * freq) % 1.0) - 1
    
    def _make_sound(self, wave: np.ndarray) -> pygame.mixer.Sound:
        """Convierte array a objeto Sound."""
        if len(wave.shape) == 1:
            wave = np.column_stack((wave, wave))
        wave = np.clip(wave, -1, 1)
        wave = (wave * 32767).astype(np.int16)
        return pygame.mixer.Sound(buffer=wave.tobytes())
    
    # ========================================================================
    # 🎵 SISTEMA DE MÚSICA ROBUSTO (Anti-cortes)
    # ========================================================================
    # - Canal 0 reservado exclusivamente para música
    # - Verificación constante ensure_music_playing()
    # - Auto-reinicio si se detiene
    # ========================================================================
    
    def generate_epic_battle_loop(self, loop_duration: float = 16.0) -> pygame.mixer.Sound:
        """
        🎮 Música de batalla épica con bucle perfecto.
        
        Características:
        - Estilo único (mezcla chiptune + orquestal)
        - Buclea perfectamente sin cortes
        - Estructura A-B-A-C (variedad sin repetición obvia)
        - BPM 128 (energético pero no frenético)
        """
        cache_key = f'epic_battle_loop_{loop_duration}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        samples = int(self.SAMPLE_RATE * loop_duration)
        t = np.linspace(0, loop_duration, samples, False)
        
        # Tempo
        bpm = 128
        beat_duration = 60 / bpm
        
        # Arrays para capas
        melody = np.zeros(samples, dtype=float)
        harmony = np.zeros(samples, dtype=float)
        bass = np.zeros(samples, dtype=float)
        rhythm = np.zeros(samples, dtype=float)
        
        # === ARMONÍA DE FONDO (Pads atmosféricos) ===
        # Progresión que buclea bien: Am - F - C - G - Em - Am - Dm - E
        chord_sequence = [
            (220.00, 261.63, 329.63),    # Am
            (174.61, 220.00, 261.63),    # F
            (130.81, 164.81, 196.00),    # C (baja)
            (196.00, 246.94, 293.66),    # G
            (164.81, 196.00, 246.94),    # Em
            (220.00, 261.63, 329.63),    # Am
            (146.83, 174.61, 220.00),    # Dm
            (164.81, 207.65, 246.94),    # E
        ]
        
        chord_duration = loop_duration / len(chord_sequence)
        
        for chord_idx, freqs in enumerate(chord_sequence):
            start = int(chord_idx * chord_duration * self.SAMPLE_RATE)
            end = int((chord_idx + 1) * chord_duration * self.SAMPLE_RATE)
            if start >= samples:
                break
            
            t_chord = np.linspace(0, chord_duration, end - start, False)
            
            # Pad suave con vibrato lento
            pad_wave = np.zeros(len(t_chord))
            for freq in freqs:
                vibrato = 1 + 0.01 * np.sin(2 * np.pi * 2 * t_chord)
                pad_wave += np.sin(2 * np.pi * freq * t_chord * vibrato) * 0.15
            
            # Envolvente que se funde perfectamente al inicio y final
            fade = int(0.3 * self.SAMPLE_RATE)
            env = np.ones(len(t_chord))
            if len(t_chord) > 2 * fade:
                env[:fade] = np.linspace(0, 1, fade) ** 2
                env[-fade:] = np.linspace(1, 0, fade) ** 2
            
            harmony[start:end] = pad_wave * env * 0.3
        
        # === MELODÍA ÉPICA (Lead) ===
        # Melodía que termina donde empezó (para bucle perfecto)
        # Notas en escala menor de La
        note_freqs = {
            'A3': 220, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66,
            'E4': 329.63, 'F4': 349.23, 'G4': 392, 'A4': 440,
            'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25,
            'rest': 0
        }
        
        # Patrón melódico que resuelve al inicio (bucle perfecto)
        # Termina en A, empieza en A
        melody_pattern = [
            ('A4', 0.5), ('E4', 0.5), ('A4', 0.5), ('B4', 0.25), ('C5', 0.25),
            ('B4', 0.5), ('A4', 0.5), ('G4', 0.5), ('E4', 0.5),
            ('C5', 0.75), ('B4', 0.25), ('A4', 0.5), ('G4', 0.5),
            ('F4', 0.5), ('E4', 0.5), ('D4', 0.5), ('E4', 0.5),
            ('A4', 1.0),  # Resolución en A para bucle perfecto
        ]
        
        current_beat = 0
        for note_name, note_beats in melody_pattern:
            if note_name == 'rest':
                current_beat += note_beats
                continue
            
            freq = note_freqs[note_name]
            start_sample = int(current_beat * beat_duration * self.SAMPLE_RATE)
            duration_samples = int(note_beats * beat_duration * self.SAMPLE_RATE)
            end_sample = min(start_sample + duration_samples, samples)
            
            if start_sample >= samples:
                break
            
            t_note = np.linspace(0, note_beats * beat_duration, end_sample - start_sample, False)
            
            # Lead: mezcla de onda cuadrada y senoidal (único)
            square = self._square_wave(t_note, freq, duty=0.4) * 0.6
            sine = np.sin(2 * np.pi * freq * t_note) * 0.4
            note_wave = square + sine
            
            # Vibrato sutil
            vibrato = 1 + 0.015 * np.sin(2 * np.pi * 6 * t_note)
            note_wave *= vibrato
            
            # Envolvente suave
            attack = min(int(0.03 * self.SAMPLE_RATE), len(t_note) // 4)
            decay = min(int(0.15 * self.SAMPLE_RATE), len(t_note) // 2)
            sustain = 0.7
            
            env = np.ones(len(t_note)) * sustain
            env[:attack] = np.linspace(0, 1, attack)
            if attack + decay < len(t_note):
                env[attack:attack+decay] = np.linspace(1, sustain, decay)
            
            melody[start_sample:end_sample] += note_wave * env * 0.25
            current_beat += note_beats
        
        # === BAJO CON GROOVE ===
        # Patrón que complementa la melodía
        bass_pattern = [
            ('A2', 0.75), ('A2', 0.25), ('C3', 0.5), ('E2', 0.5),
            ('F2', 0.75), ('A2', 0.25), ('G2', 0.5), ('B2', 0.5),
            ('C3', 1.0), ('G2', 1.0),
            ('D3', 0.5), ('C3', 0.5), ('B2', 0.5), ('A2', 0.5),
        ]
        
        current_beat = 0
        for note_name, note_beats in bass_pattern:
            if note_name == 'rest':
                current_beat += note_beats
                continue
            
            freq = note_freqs.get(note_name, 110)
            start_sample = int(current_beat * beat_duration * self.SAMPLE_RATE)
            duration_samples = int(note_beats * beat_duration * self.SAMPLE_RATE)
            end_sample = min(start_sample + duration_samples, samples)
            
            if start_sample >= samples:
                break
            
            t_note = np.linspace(0, note_beats * beat_duration, end_sample - start_sample, False)
            
            # Bajo: onda triangular con subgrave
            tri = self._triangle_wave(t_note, freq) * 0.6
            sub = np.sin(2 * np.pi * freq * 0.5 * t_note) * 0.4
            note_wave = tri + sub
            
            # Groove: envolvente que "respira"
            env = np.exp(-t_note * 4) * 0.8 + 0.2
            
            bass[start_sample:end_sample] += note_wave * env * 0.3
            current_beat += note_beats
        
        # === RITMO (Percusión épica pero no dominante) ===
        # Kick en 1 y 3, snare en 2 y 4
        total_beats = int(loop_duration / beat_duration)
        
        for beat in range(total_beats):
            beat_start = int(beat * beat_duration * self.SAMPLE_RATE)
            
            # Kick (beats 1, 3, 5, 7...)
            if beat % 4 == 0 or beat % 4 == 2:
                kick_duration = 0.1
                kick_end = min(beat_start + int(kick_duration * self.SAMPLE_RATE), samples)
                if beat_start < samples:
                    t_kick = np.linspace(0, kick_duration, kick_end - beat_start, False)
                    freq_sweep = 120 * np.exp(-t_kick * 15)
                    phase = 2 * np.pi * np.cumsum(freq_sweep) / self.SAMPLE_RATE
                    kick_wave = np.sin(phase) * np.exp(-t_kick * 10) * 0.4
                    rhythm[beat_start:kick_end] += kick_wave
            
            # Snare (beats 2, 6...)
            if beat % 4 == 1:
                snare_duration = 0.08
                snare_end = min(beat_start + int(snare_duration * self.SAMPLE_RATE), samples)
                if beat_start < samples:
                    t_snare = np.linspace(0, snare_duration, snare_end - beat_start, False)
                    noise = np.random.uniform(-0.5, 0.5, len(t_snare))
                    tone = np.sin(2 * np.pi * 180 * t_snare) * 0.3
                    snare_wave = (noise + tone) * np.exp(-t_snare * 20) * 0.25
                    rhythm[beat_start:snare_end] += snare_wave
            
            # Hi-hat suave (off-beats)
            if beat % 2 == 1:
                hat_start = beat_start + int(beat_duration * 0.5 * self.SAMPLE_RATE)
                hat_duration = 0.03
                hat_end = min(hat_start + int(hat_duration * self.SAMPLE_RATE), samples)
                if hat_start < samples and hat_end <= samples:
                    t_hat = np.linspace(0, hat_duration, hat_end - hat_start, False)
                    hat_noise = np.random.uniform(-0.3, 0.3, len(t_hat))
                    hat_wave = hat_noise * np.exp(-t_hat * 40) * 0.15
                    rhythm[hat_start:hat_end] += hat_wave
        
        # === COMBINAR TODO ===
        # Volumen balanceado
        final_mix = (
            harmony * 0.8 +
            melody * 1.0 +
            bass * 0.9 +
            rhythm * 0.7
        )
        
        # Compresión suave
        final_mix = np.tanh(final_mix * 0.7)
        
        # Estéreo: panorámica dinámica
        stereo_wave = np.zeros((samples, 2))
        for i in range(samples):
            # Panning que cambia lentamente durante el loop
            pan = 0.2 * np.sin(2 * np.pi * i / samples * 2)  # Va de izq a der 2 veces
            stereo_wave[i, 0] = final_mix[i] * (0.7 + pan)
            stereo_wave[i, 1] = final_mix[i] * (0.7 - pan)
        
        # Asegurar que empiece y termine en cero (transición suave)
        fade_samples = int(0.05 * self.SAMPLE_RATE)
        stereo_wave[:fade_samples, 0] *= np.linspace(0, 1, fade_samples)
        stereo_wave[:fade_samples, 1] *= np.linspace(0, 1, fade_samples)
        stereo_wave[-fade_samples:, 0] *= np.linspace(1, 0, fade_samples)
        stereo_wave[-fade_samples:, 1] *= np.linspace(1, 0, fade_samples)
        
        stereo_wave = np.clip(stereo_wave, -1, 1)
        stereo_wave = (stereo_wave * 32767).astype(np.int16)
        
        sound = pygame.mixer.Sound(buffer=stereo_wave.tobytes())
        self._cache[cache_key] = sound
        return sound
    
    def play_battle_music(self, loops: int = -1, fade_ms: int = 3000):
        """Inicia música de batalla con bucle perfecto."""
        if self._music_playing:
            self.stop_music()
        
        print("[AUDIO] Generando música épica (bucle perfecto)...")
        music = self.generate_epic_battle_loop(loop_duration=16.0)
        
        channel = pygame.mixer.find_channel()
        if channel:
            channel.play(music, loops=loops, fade_ms=fade_ms)
            self._music_channel = channel
            self._music_playing = True
            print("[AUDIO] Música iniciada - ¡Bucle épico infinito!")
    
    def stop_music(self, fade_ms: int = 1500):
        """Detiene la música con fade out."""
        if self._music_channel and self._music_playing:
            try:
                self._music_channel.fadeout(fade_ms)
            except:
                pass
            self._music_playing = False
            print("[AUDIO] Música detenida")
    
    def is_music_playing(self) -> bool:
        """Retorna True si la música está sonando."""
        if not self._music_playing or not self._music_channel:
            return False
        try:
            return self._music_channel.get_busy()
        except:
            return False
    
    def ensure_music_playing(self):
        """Verifica que la música siga sonando, reinicia inmediatamente si se detuvo."""
        if not self._music_playing:
            return
        
        try:
            is_busy = self._music_channel and self._music_channel.get_busy()
        except:
            is_busy = False
        
        if not is_busy:
            print("[AUDIO] Música no suena, reiniciando ahora...")
            if self._music_sound:
                try:
                    # Forzar reinicio inmediato sin fade
                    self._music_channel = pygame.mixer.Channel(0)
                    self._music_channel.play(self._music_sound, loops=-1, fade_ms=0)
                    print("[AUDIO] Música reiniciada")
                except Exception as e:
                    print(f"[AUDIO ERROR] {e}")
    
    # ========================================================================
    # 🎵 NUEVA MÚSICA: MELODÍA PRINCIPAL ÉPICA (Bucle Largo)
    # ========================================================================
    
    def generate_main_theme_loop(self, duration: float = 32.0) -> pygame.mixer.Sound:
        """
        🎺 MELODÍA PRINCIPAL ÉPICA - Bucle largo perfecto.
        
        Esta es LA MELODÍA que se escucha al inicio y sigue todo el tiempo.
        Más larga, más desarrollada, y con variaciones que vuelven al tema principal.
        """
        cache_key = f'main_theme_{duration}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        samples = int(self.SAMPLE_RATE * duration)
        t_total = np.linspace(0, duration, samples, False)
        
        bpm = 120
        beat_duration = 60 / bpm
        total_beats = int(duration / beat_duration)
        
        # Arrays
        main_melody = np.zeros(samples, dtype=float)
        harmony = np.zeros(samples, dtype=float)
        bass_line = np.zeros(samples, dtype=float)
        drums = np.zeros(samples, dtype=float)
        
        # === LA MELODÍA PRINCIPAL ÉPICA ===
        # Tema A (aparece al inicio y vuelve varias veces)
        # Escala: La menor (emocional y épica)
        
        def add_note(target_array, freq, start_beat, duration_beats, volume=0.3, vibrato=True):
            """Helper para agregar notas."""
            start_sample = int(start_beat * beat_duration * self.SAMPLE_RATE)
            end_sample = int((start_beat + duration_beats) * beat_duration * self.SAMPLE_RATE)
            end_sample = min(end_sample, samples)
            
            if start_sample >= samples:
                return
            
            t_note = np.linspace(0, duration_beats * beat_duration, end_sample - start_sample, False)
            
            # Onda mixta (cuadrada + senoidal) - sonido único y rico
            square = self._square_wave(t_note, freq, duty=0.45) * 0.6
            sine = np.sin(2 * np.pi * freq * t_note) * 0.4
            note = square + sine
            
            # Vibrato expresivo
            if vibrato and duration_beats > 0.5:
                vib = 1 + 0.02 * np.sin(2 * np.pi * 5 * t_note)
                note = note.astype(float) * vib
            
            # Envolvente suave con ataque y sustain
            attack = min(int(0.05 * self.SAMPLE_RATE), len(t_note) // 3)
            decay = min(int(0.15 * self.SAMPLE_RATE), len(t_note) // 2)
            sustain = 0.75
            
            env = np.ones(len(t_note)) * sustain
            if attack > 0:
                env[:attack] = np.linspace(0, 1, attack)
            if attack + decay < len(t_note):
                env[attack:attack+decay] = np.linspace(1, sustain, decay)
            if len(t_note) > 10:
                env[-5:] = np.linspace(sustain, 0, 5)
            
            target_array[start_sample:end_sample] += note * env * volume
        
        # === TEMA PRINCIPAL A (La melodía que te gustó) ===
        # Se repite 2 veces durante el bucle, con variaciones
        
        def play_theme_a(start_beat, variation=0):
            """El tema principal épico."""
            b = start_beat
            v = 0.35 if variation == 0 else 0.3  # Primera vez más fuerte
            
            # Frase 1: Introducción ascendente épica
            add_note(main_melody, 440, b, 1.0, v)      # A4
            add_note(main_melody, 523.25, b+1, 0.5, v) # C5
            add_note(main_melody, 659.25, b+1.5, 0.5, v) # E5
            add_note(main_melody, 783.99, b+2, 1.0, v) # G5
            add_note(main_melody, 880, b+3, 1.0, v)    # A5 - CLIMAX
            
            # Frase 2: Respuesta descendente
            add_note(main_melody, 880, b+4, 0.5, v)
            add_note(main_melody, 783.99, b+4.5, 0.5, v)
            add_note(main_melody, 659.25, b+5, 0.5, v)
            add_note(main_melody, 587.33, b+5.5, 0.5, v) # D5
            add_note(main_melody, 523.25, b+6, 1.0, v)   # C5
            add_note(main_melody, 440, b+7, 1.0, v)      # A4 - Vuelta
            
            # Frase 3: Variación rítmica
            if variation == 0:
                add_note(main_melody, 523.25, b+8, 0.75, v)
                add_note(main_melody, 587.33, b+8.75, 0.25, v)
                add_note(main_melody, 659.25, b+9, 0.75, v)
                add_note(main_melody, 523.25, b+9.75, 0.25, v)
                add_note(main_melody, 440, b+10, 2.0, v)  # Sostenida
            else:
                # Variación: notas más cortas, más energía
                add_note(main_melody, 659.25, b+8, 0.5, v)
                add_note(main_melody, 783.99, b+8.5, 0.5, v)
                add_note(main_melody, 880, b+9, 1.0, v)
                add_note(main_melody, 783.99, b+10, 0.5, v)
                add_note(main_melody, 659.25, b+10.5, 0.5, v)
                add_note(main_melody, 523.25, b+11, 1.0, v)
        
        # === SECCIÓN B (Contrastante pero conectada) ===
        def play_section_b(start_beat):
            """Sección más tranquila que prepara el regreso."""
            b = start_beat
            v = 0.25
            
            # Más espaciada, notas largas
            add_note(main_melody, 392, b, 2.0, v)      # G4
            add_note(main_melody, 440, b+2, 2.0, v)    # A4
            add_note(main_melody, 349.23, b+4, 1.5, v) # F4
            add_note(main_melody, 392, b+5.5, 2.5, v)  # G4
            
            # Subida de tensión
            add_note(main_melody, 523.25, b+8, 0.5, 0.3)
            add_note(main_melody, 587.33, b+8.5, 0.5, 0.3)
            add_note(main_melody, 659.25, b+9, 2.5, 0.35)
        
        # === ARMONÍA (Acordes de fondo) ===
        def add_chord(start_beat, duration, freqs, volume=0.2):
            """Agrega un acorde."""
            start_s = int(start_beat * beat_duration * self.SAMPLE_RATE)
            end_s = int((start_beat + duration) * beat_duration * self.SAMPLE_RATE)
            end_s = min(end_s, samples)
            
            if start_s >= samples:
                return
            
            t_chord = np.linspace(0, duration * beat_duration, end_s - start_s, False)
            chord_wave = np.zeros(len(t_chord))
            
            for freq in freqs:
                # Pad suave
                note = np.sin(2 * np.pi * freq * t_chord) * 0.3
                note += np.sin(2 * np.pi * (freq + 0.5) * t_chord) * 0.15  # Detune
                chord_wave += note
            
            # Envolvente muy suave
            fade = int(0.4 * self.SAMPLE_RATE)
            env = np.ones(len(t_chord))
            if len(t_chord) > 2 * fade:
                env[:fade] = np.linspace(0, 1, fade) ** 2
                env[-fade:] = np.linspace(1, 0, fade) ** 2
            
            harmony[start_s:end_s] += chord_wave * env * volume
        
        # Progresión de acordes que acompaña la melodía
        chord_prog = [
            ([220, 261.63, 329.63], 8),    # Am
            ([174.61, 220, 261.63], 8),    # F
            ([196, 246.94, 293.66], 8),    # G
            ([220, 261.63, 329.63], 8),    # Am
        ]
        
        beat = 0
        for freqs, dur in chord_prog:
            add_chord(beat, dur, freqs, 0.25)
            beat += dur
        
        # === BAJO (Groove estable) ===
        def add_bass_note(start_beat, freq, duration, volume=0.25):
            start_s = int(start_beat * beat_duration * self.SAMPLE_RATE)
            end_s = int((start_beat + duration) * beat_duration * self.SAMPLE_RATE)
            end_s = min(end_s, samples)
            
            if start_s >= samples:
                return
            
            t_note = np.linspace(0, duration * beat_duration, end_s - start_s, False)
            
            # Triangular con subgrave
            tri = self._triangle_wave(t_note, freq) * 0.5
            sub = np.sin(2 * np.pi * freq * 0.5 * t_note) * 0.4
            note = tri + sub
            
            # Envolvente de "respiración"
            env = np.exp(-t_note * 3) * 0.7 + 0.3
            
            bass_line[start_s:end_s] += note * env * volume
        
        # Patrón de bajo que sigue la progresión
        bass_pattern = [
            (110, 2), (110, 2), (130.81, 2), (110, 2),  # Am
            (87.31, 2), (87.31, 2), (110, 2), (87.31, 2), # F
            (98, 2), (98, 2), (123.47, 2), (98, 2),      # G
            (110, 2), (110, 2), (130.81, 2), (110, 2),   # Am
        ]
        
        beat = 0
        for freq, dur in bass_pattern:
            add_bass_note(beat, freq, dur, 0.28)
            beat += dur
        
        # === PERCUSIÓN SUTIL ===
        for beat in range(0, total_beats, 2):
            beat_start = int(beat * beat_duration * self.SAMPLE_RATE)
            
            # Kick en 1 de cada 4 compases
            if beat % 8 == 0:
                kick_dur = 0.1
                kick_end = min(beat_start + int(kick_dur * self.SAMPLE_RATE), samples)
                if beat_start < samples:
                    t_kick = np.linspace(0, kick_dur, kick_end - beat_start, False)
                    freq = 100 * np.exp(-t_kick * 10)
                    phase = 2 * np.pi * np.cumsum(freq) / self.SAMPLE_RATE
                    kick = np.sin(phase) * np.exp(-t_kick * 8) * 0.35
                    drums[beat_start:kick_end] += kick
            
            # Snare suave
            if beat % 8 == 4:
                snare_dur = 0.08
                snare_end = min(beat_start + int(snare_dur * self.SAMPLE_RATE), samples)
                if beat_start < samples:
                    t_snare = np.linspace(0, snare_dur, snare_end - beat_start, False)
                    noise = np.random.uniform(-0.3, 0.3, len(t_snare))
                    snare = noise * np.exp(-t_snare * 15) * 0.2
                    drums[beat_start:snare_end] += snare
        
        # === ESTRUCTURA COMPLETA ===
        # 0-12:    Tema A (la melodía épica)
        # 12-20:   Sección B (tranquila, prepara regreso)
        # 20-28:   Tema A variación (vuelve la melodía)
        # 28-32:   Cierre que conecta al inicio (bucle perfecto)
        
        play_theme_a(0, variation=0)      # Tema A original
        play_section_b(12)                 # Sección B
        play_theme_a(20, variation=1)      # Tema A vuelve
        
        # Cierre especial para bucle perfecto
        # Termina exactamente como empieza (A4)
        add_note(main_melody, 440, 28, 2.0, 0.3)   # A4 sostenida
        add_note(main_melody, 440, 30, 2.0, 0.25)  # A4 para transición suave
        
        # === COMBINAR TODO ===
        final_mix = (
            main_melody * 1.0 +    # Melodía PRINCIPAL (protagonista)
            harmony * 0.6 +        # Acordes de apoyo
            bass_line * 0.7 +      # Bajo estable
            drums * 0.5            # Ritmo sutil
        )
        
        # Compresión suave
        final_mix = np.tanh(final_mix * 0.8) * 0.9
        
        # Estéreo con la melodía ligeramente a la derecha
        stereo_wave = np.zeros((samples, 2))
        for i in range(samples):
            # Panning lento
            pan = 0.15 * np.sin(2 * np.pi * i / samples * 1.5)
            stereo_wave[i, 0] = final_mix[i] * (0.75 + pan)  # Left
            stereo_wave[i, 1] = final_mix[i] * (0.85 - pan)  # Right (melodía)
        
        # BUCLE PERFECTO: El final debe conectar suavemente con el inicio
        # Solo fade in al principio, el final debe ser igual al inicio
        fade_samples = int(0.05 * self.SAMPLE_RATE)
        
        # Fade in suave al inicio
        stereo_wave[:fade_samples, 0] *= np.linspace(0, 1, fade_samples)
        stereo_wave[:fade_samples, 1] *= np.linspace(0, 1, fade_samples)
        
        # Para bucle perfecto: el final debe ser igual al inicio
        # Copiar el inicio (después del fade in) al final
        stereo_wave[-fade_samples:, 0] = stereo_wave[fade_samples:2*fade_samples, 0]
        stereo_wave[-fade_samples:, 1] = stereo_wave[fade_samples:2*fade_samples, 1]
        
        stereo_wave = np.clip(stereo_wave, -1, 1)
        stereo_wave = (stereo_wave * 32767).astype(np.int16)
        
        sound = pygame.mixer.Sound(buffer=stereo_wave.tobytes())
        self._cache[cache_key] = sound
        return sound
    
    def play_main_theme(self, loops: int = -1, fade_ms: int = 500):
        """Inicia la melodía principal épica (bucle largo)."""
        if self._music_playing:
            self.stop_music()
        
        print("[AUDIO] Generando MELODÍA PRINCIPAL ÉPICA (32 segundos)...")
        self._music_sound = self.generate_main_theme_loop(duration=32.0)
        
        # Usar canal 0 (reservado para música)
        channel = pygame.mixer.Channel(0)
        if channel:
            channel.play(self._music_sound, loops=loops, fade_ms=fade_ms)
            self._music_channel = channel
            self._music_playing = True
            print("[AUDIO] ¡Melodía épica iniciada! (Canal dedicado, nunca se interrumpe)")
    
    # ========================================================================
    # SONIDOS DE BOTONES
    # ========================================================================
    
    def button_hover(self) -> pygame.mixer.Sound:
        """Hover sutil."""
        cache_key = 'btn_hover'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        duration = 0.04
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        freq = 2500
        wave = self._square_wave(t, freq, duty=0.3) * 0.08
        wave *= np.exp(-t * 100)
        
        wave = (wave * 32767).astype(np.int16)
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    def button_click(self) -> pygame.mixer.Sound:
        """Click satisfactorio."""
        cache_key = 'btn_click'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        duration = 0.1
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        wave1 = self._square_wave(t, 1300, duty=0.5) * np.exp(-t * 30) * 0.25
        wave2 = self._square_wave(t, 650, duty=0.5) * np.exp(-t * 15) * 0.2
        
        wave = wave1 + wave2
        wave = (wave * 32767).astype(np.int16)
        
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    def button_back(self) -> pygame.mixer.Sound:
        """Sonido de volver."""
        cache_key = 'btn_back'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        duration = 0.1
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        freq = 700 * np.exp(-t * 12)
        phase = 2 * np.pi * np.cumsum(freq) / self.SAMPLE_RATE
        wave = np.sin(phase)
        wave = np.where(wave > 0, 1, -1)
        wave *= np.exp(-t * 12) * 0.3
        
        wave = (wave * 32767).astype(np.int16)
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    # ========================================================================
    # SONIDOS DE PASOS
    # ========================================================================
    
    def footstep(self, surface: str = 'grass', intensity: str = 'normal') -> pygame.mixer.Sound:
        """Pasos."""
        cache_key = f'step_{surface}_{intensity}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        duration = 0.08
        samples = int(self.SAMPLE_RATE * duration)
        
        if surface == 'grass':
            noise = np.random.uniform(-0.5, 0.5, samples)
            noise = np.convolve(noise, np.ones(3)/3, mode='same')
            t = np.linspace(0, duration, samples, False)
            wave = noise * np.exp(-t * 25) * 0.25
        elif surface == 'stone':
            t = np.linspace(0, duration, samples, False)
            wave = self._square_wave(t, 180, duty=0.2) * np.exp(-t * 35) * 0.15
            wave += np.random.uniform(-0.15, 0.15, samples) * np.exp(-t * 40)
        else:
            t = np.linspace(0, duration, samples, False)
            wave = self._triangle_wave(t, 140) * np.exp(-t * 30) * 0.2
        
        wave = (wave * 32767).astype(np.int16)
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    # ========================================================================
    # SONIDOS DE RECOMPENSA
    # ========================================================================
    
    def coin_collect(self, pitch: str = 'high') -> pygame.mixer.Sound:
        """Moneda."""
        cache_key = f'coin_{pitch}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        freqs = {'high': 1200, 'mid': 900, 'low': 600}
        base_freq = freqs[pitch]
        
        duration = 0.15
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        note1 = self._square_wave(t, base_freq, duty=0.5) * np.exp(-t * 35)
        note2 = self._square_wave(t, base_freq * 1.5, duty=0.5) * np.exp(-t * 25) * 0.5
        
        wave = (note1 + note2) * 0.3
        wave = (wave * 32767).astype(np.int16)
        
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    def power_up(self, duration: float = 0.5) -> pygame.mixer.Sound:
        """Power-up."""
        cache_key = f'powerup_{duration}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        start_freq = 200
        end_freq = 800
        freq = start_freq * (end_freq / start_freq) ** (t / duration)
        
        phase = 2 * np.pi * np.cumsum(freq) / self.SAMPLE_RATE
        wave = np.sin(phase)
        wave = np.where(wave > 0, 1, -1)
        wave *= np.exp(-t * 3) * 0.35
        
        harm = self._square_wave(t, freq * 0.5, duty=0.5) * 0.15
        wave = (wave + harm) * 0.5
        wave = (wave * 32767).astype(np.int16)
        
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    def hit_impact(self, intensity: str = 'medium') -> pygame.mixer.Sound:
        """Golpe."""
        cache_key = f'hit_{intensity}'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        duration = {'light': 0.08, 'medium': 0.12, 'heavy': 0.2}[intensity]
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        noise = np.random.uniform(-1, 1, samples)
        tone = self._square_wave(t, 140, duty=0.5)
        
        wave = noise * 0.4 + tone * 0.25
        wave *= np.exp(-t * 25) * {'light': 0.3, 'medium': 0.4, 'heavy': 0.5}[intensity]
        
        wave = (wave * 32767).astype(np.int16)
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    # ========================================================================
    # SONIDOS ESPECIALES
    # ========================================================================
    
    def hero_power_use(self, power_type: str = 'slash') -> pygame.mixer.Sound:
        """Poder del héroe."""
        if power_type == 'slash':
            return self.hit_impact('medium')
        elif power_type == 'power_strike':
            return self.hit_impact('heavy')
        elif power_type == 'heal':
            return self.power_up(duration=0.3)
        else:
            return self.coin_collect('mid')
    
    def victory_jingle(self) -> pygame.mixer.Sound:
        """Victoria."""
        cache_key = 'victory'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        notes = [220, 261.63, 329.63, 440, 523.25, 659.25]
        note_duration = 0.08
        total_duration = len(notes) * note_duration
        samples = int(self.SAMPLE_RATE * total_duration)
        
        wave = np.zeros(samples)
        
        for i, freq in enumerate(notes):
            start = int(i * note_duration * self.SAMPLE_RATE)
            end = int((i + 1) * note_duration * self.SAMPLE_RATE)
            t_note = np.linspace(0, note_duration, end - start, False)
            
            note = self._square_wave(t_note, freq, duty=0.5)
            note *= np.exp(-t_note * 12) * (0.3 + i * 0.04)
            
            wave[start:end] += note
        
        wave = (wave * 32767).astype(np.int16)
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound
    
    def defeat_sound(self) -> pygame.mixer.Sound:
        """Derrota."""
        cache_key = 'defeat'
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        duration = 0.6
        samples = int(self.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, samples, False)
        
        freq = 300 * np.exp(-t * 3)
        phase = 2 * np.pi * np.cumsum(freq) / self.SAMPLE_RATE
        wave = np.sin(phase)
        wave = np.where(wave > 0, 1, -1)
        wave *= np.exp(-t * 4) * 0.35
        
        wave = (wave * 32767).astype(np.int16)
        sound = self._make_sound(wave)
        self._cache[cache_key] = sound
        return sound


# Instancia global
_sound_gen: Optional[SoundGenerator] = None


def get_sound_generator() -> SoundGenerator:
    """Obtiene la instancia global."""
    global _sound_gen
    if _sound_gen is None:
        _sound_gen = SoundGenerator()
    return _sound_gen


def play_ui_click():
    get_sound_generator().button_click().play()


def play_coin():
    get_sound_generator().coin_collect('high').play()


def play_victory():
    get_sound_generator().victory_jingle().play()


def start_battle_music():
    get_sound_generator().play_battle_music()


def stop_music():
    get_sound_generator().stop_music()
