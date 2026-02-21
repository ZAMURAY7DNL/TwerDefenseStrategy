"""
Music Player - Sistema de Música Seamless
==========================================
Sistema de doble buffer con crossfade para loops perfectos.
Elimina completamente el gap de silencio entre repeticiones.
"""
import pygame
import numpy as np
import threading
import time
from typing import Optional, Tuple


class SeamlessMusicPlayer:
    """
    Reproductor de música con crossfade entre loops.
    
    Características:
    - Doble buffer: Dos copias del sonido se alternan
    - Crossfade: 1 segundo de fundido entre loops
    - Nunca hay silencio: Una copia empieza antes de que termine la otra
    - Loop perfecto: Transiciones imperceptibles
    """
    
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Dos canales para crossfade
        pygame.mixer.set_reserved(2)
        self._channel_a = pygame.mixer.Channel(0)
        self._channel_b = pygame.mixer.Channel(1)
        
        self._sound_a: Optional[pygame.mixer.Sound] = None
        self._sound_b: Optional[pygame.mixer.Sound] = None
        self._is_playing = False
        self._duration = 0.0
        self._crossfade_duration = 1.0  # Segundos de crossfade
        
        # Control de loop
        self._current_channel = 'A'  # 'A' o 'B'
        self._start_time = 0.0
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = False
        self._volume = 0.6
        
    def load_and_play(self, generate_func, duration: float = 16.0, volume: float = 0.6):
        """Carga música y comienza reproducción seamless."""
        self.stop()
        self._duration = duration
        self._volume = volume
        
        print(f"[MUSIC] Generando música seamless ({duration}s)...")
        
        try:
            # Generar dos copias idénticas para alternar
            samples = int(44100 * duration)
            t = np.linspace(0, duration, samples, False)
            
            wave = generate_func(t, samples, duration)
            
            if np.max(np.abs(wave)) > 0:
                wave = wave / np.max(np.abs(wave)) * 0.8
            
            # Crear dos sonidos idénticos
            stereo = np.column_stack((wave, wave)).astype(np.int16)
            
            self._sound_a = pygame.mixer.Sound(buffer=stereo.tobytes())
            self._sound_b = pygame.mixer.Sound(buffer=stereo.tobytes())
            
            self._sound_a.set_volume(volume)
            self._sound_b.set_volume(0)  # Empieza muteado
            
            # Iniciar primera reproducción
            self._channel_a.play(self._sound_a)
            self._is_playing = True
            self._current_channel = 'A'
            self._start_time = time.time()
            
            print("[MUSIC] Música iniciada - Crossfade activo")
            
            # Iniciar monitor
            self._stop_monitor = False
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            
        except Exception as e:
            print(f"[MUSIC ERROR] {e}")
    
    def _monitor_loop(self):
        """Thread que maneja el crossfade entre loops."""
        while not self._stop_monitor:
            if not self._is_playing:
                time.sleep(0.1)
                continue
            
            elapsed = time.time() - self._start_time
            loop_point = self._duration - self._crossfade_duration
            
            # Si estamos en el punto de crossfade
            if elapsed >= loop_point and elapsed < self._duration:
                # Calcular progreso del crossfade (0 a 1)
                fade_progress = (elapsed - loop_point) / self._crossfade_duration
                
                if self._current_channel == 'A':
                    # Fade out A, Fade in B
                    if not self._channel_b.get_busy():
                        self._channel_b.play(self._sound_b)
                    
                    self._channel_a.set_volume(self._volume * (1 - fade_progress))
                    self._channel_b.set_volume(self._volume * fade_progress)
                    
                    if fade_progress >= 0.95:
                        self._current_channel = 'B'
                        self._start_time = time.time()
                        self._channel_a.stop()
                        
                else:  # channel B
                    # Fade out B, Fade in A
                    if not self._channel_a.get_busy():
                        self._channel_a.play(self._sound_a)
                    
                    self._channel_b.set_volume(self._volume * (1 - fade_progress))
                    self._channel_a.set_volume(self._volume * fade_progress)
                    
                    if fade_progress >= 0.95:
                        self._current_channel = 'A'
                        self._start_time = time.time()
                        self._channel_b.stop()
            
            # Si por alguna razón ambos canales están vacíos, reiniciar
            elif elapsed >= self._duration:
                print("[MUSIC] Reinicio de emergencia...")
                self._channel_a.play(self._sound_a)
                self._current_channel = 'A'
                self._start_time = time.time()
            
            time.sleep(0.05)  # 50ms para crossfade suave
    
    def stop(self):
        """Detiene la música."""
        self._is_playing = False
        self._stop_monitor = True
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        self._channel_a.stop()
        self._channel_b.stop()
        self._sound_a = None
        self._sound_b = None
        print("[MUSIC] Detenido")


# =============================================================================
# GENERADOR DE MÚSICA - LOOP PERFECTO
# =============================================================================

def generate_seamless_loop(t: np.ndarray, samples: int, duration: float) -> np.ndarray:
    """
    Genera una música que buclea perfectamente.
    
    La clave es que:
    1. Empieza y termina en la misma nota (A4)
    2. La armonía es consistente inicio-fin
    3. NO hay fade-out global al final
    4. El crossfade se maneja en el player, no en el audio
    """
    wave = np.zeros(samples, dtype=float)
    
    bpm = 100  # Ligeramente más lento para ambientación
    beat_duration = 60 / bpm
    samples_per_beat = int(44100 * beat_duration)
    
    # Estructura: 16 beats exactos para loop perfecto
    # Beat 0-4: Intro sobre A
    # Beat 4-8: Desarrollo
    # Beat 8-12: Variación
    # Beat 12-16: Resolución en A (conecta con intro)
    
    def add_tone(freq: float, start_beat: float, duration_beats: float, 
                 volume: float = 0.4, waveform: str = 'mixed'):
        """Agrega un tono con waveform seleccionable."""
        start_idx = int(start_beat * samples_per_beat)
        end_idx = int((start_beat + duration_beats) * samples_per_beat)
        end_idx = min(end_idx, samples)
        
        if start_idx >= samples:
            return
        
        note_samples = end_idx - start_idx
        t_note = np.linspace(0, duration_beats * beat_duration, note_samples, False)
        
        # Generar waveform
        if waveform == 'sine':
            tone = np.sin(2 * np.pi * freq * t_note)
        elif waveform == 'square':
            tone = np.where((t_note * freq) % 1.0 < 0.5, 1.0, -1.0)
        elif waveform == 'triangle':
            tri_phase = (t_note * freq) % 1.0
            tone = 2 * np.abs(2 * tri_phase - 1) - 1
        else:  # mixed
            square = np.where((t_note * freq) % 1.0 < 0.5, 1.0, -1.0) * 0.5
            sine = np.sin(2 * np.pi * freq * t_note) * 0.5
            tone = square + sine
        
        # Envolvente: Attack rápido, sustain, NO release al final
        # Para permitir crossfade externo
        attack_samples = min(int(0.02 * 44100), note_samples // 8)
        env = np.ones(note_samples)
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
        # NO fade-out al final - dejamos que el crossfade lo maneje
        
        wave[start_idx:end_idx] += tone * env * volume
    
    # === CAPA 1: BAJO (sostiene todo) ===
    # Patrón de bajo que empieza y termina en A
    bass_pattern = [
        (110.00, 0, 2),   # A2 - beats 0-2
        (110.00, 2, 2),   # A2 - beats 2-4
        (87.31, 4, 2),    # F2 - beats 4-6
        (87.31, 6, 2),    # F2 - beats 6-8
        (98.00, 8, 2),    # G2 - beats 8-10
        (98.00, 10, 2),   # G2 - beats 10-12
        (110.00, 12, 4),  # A2 - beats 12-16 (resolución)
    ]
    
    for freq, start, dur in bass_pattern:
        add_tone(freq, start, dur, volume=0.35, waveform='triangle')
    
    # === CAPA 2: ARPEGIO RÍTMICO ===
    # Figura que da movimiento, siempre vuelve a A
    arpeggio = [
        # Primer compás - A menor
        (440.00, 0, 0.5, 0.25),    # A4
        (523.25, 0.5, 0.5, 0.2),   # C5
        (659.25, 1.0, 0.5, 0.25),  # E5
        (440.00, 1.5, 0.5, 0.2),   # A4
        
        # Segundo compás - desarrollo
        (523.25, 2, 0.5, 0.2),     # C5
        (659.25, 2.5, 0.5, 0.25),  # E5
        (783.99, 3, 0.5, 0.3),     # G5 (tensión)
        (440.00, 3.5, 0.5, 0.2),   # A4 (resolución)
        
        # Tercer compás - F mayor
        (349.23, 4, 0.5, 0.2),     # F4
        (440.00, 4.5, 0.5, 0.2),   # A4
        (523.25, 5, 0.5, 0.25),    # C5
        (349.23, 5.5, 0.5, 0.2),   # F4
        
        # Cuarto compás - G mayor
        (392.00, 6, 0.5, 0.2),     # G4
        (493.88, 6.5, 0.5, 0.25),  # B4
        (587.33, 7, 0.5, 0.3),     # D5
        (392.00, 7.5, 0.5, 0.2),   # G4
        
        # Quinto compás - variación
        (440.00, 8, 0.5, 0.25),    # A4
        (523.25, 8.5, 0.5, 0.2),   # C5
        (659.25, 9, 1.0, 0.3),     # E5 largo
        (440.00, 10, 1.0, 0.25),   # A4 largo
        
        # Sexto compás - cierre preparatorio
        (349.23, 11, 0.5, 0.2),    # F4
        (392.00, 11.5, 0.5, 0.2),  # G4
        
        # Séptimo y octavo - vuelta a A con energía
        (440.00, 12, 1.0, 0.35),   # A4 (tónica fuerte)
        (523.25, 13, 0.5, 0.25),   # C5
        (659.25, 13.5, 0.5, 0.25), # E5
        (880.00, 14, 0.5, 0.3),    # A5 (octava alta)
        (440.00, 14.5, 0.5, 0.3),  # A4
        (440.00, 15, 1.0, 0.35),   # A4 sostenida al final
    ]
    
    for freq, start, dur, vol in arpeggio:
        add_tone(freq, start, dur, volume=vol, waveform='mixed')
    
    # === CAPA 3: PADS ARMÓNICOS (sustained) ===
    # Acordes que duran todo el loop, empiezan y terminan en Am
    chord_progression = [
        ([220, 261.63, 329.63], 0, 4, 0.15),    # Am - beats 0-4
        ([174.61, 220, 261.63], 4, 4, 0.15),   # F - beats 4-8
        ([196, 246.94, 293.66], 8, 4, 0.15),   # G - beats 8-12
        ([220, 261.63, 329.63], 12, 4, 0.15),  # Am - beats 12-16
    ]
    
    for freqs, start, dur, vol in chord_progression:
        start_idx = int(start * samples_per_beat)
        end_idx = int((start + dur) * samples_per_beat)
        end_idx = min(end_idx, samples)
        
        if start_idx >= samples:
            continue
        
        chord_samples = end_idx - start_idx
        t_chord = np.linspace(0, dur * beat_duration, chord_samples, False)
        
        chord_wave = np.zeros(chord_samples)
        for freq in freqs:
            chord_wave += np.sin(2 * np.pi * freq * t_chord) * 0.3
        
        # Envolvente muy suave, sin fade-out brusco
        fade_samples = min(int(0.3 * 44100), chord_samples // 4)
        env = np.ones(chord_samples)
        env[:fade_samples] = np.linspace(0, 1, fade_samples)
        # Fade-out muy suave al final para que no corte
        if chord_samples > fade_samples:
            env[-fade_samples:] = np.linspace(1, 0.7, fade_samples)
        
        wave[start_idx:end_idx] += chord_wave * env * vol
    
    # === CAPA 4: TEXTURA AMBIENTAL ===
    # Una nota alta sostenida que da "aire" - octava alta de A
    # Usa solo volumen muy bajo para no competir
    ambient_start = int(0)
    ambient_end = min(int(16 * samples_per_beat), samples)
    t_ambient = np.linspace(0, 16 * beat_duration, ambient_end - ambient_start, False)
    
    # Vibrato lento
    vibrato = np.sin(2 * np.pi * 3 * t_ambient) * 2  # 3Hz de vibrato
    ambient_freq = 880 + vibrato  # A5 con vibrato
    ambient = np.sin(2 * np.pi * ambient_freq * t_ambient) * 0.05
    
    # Envolvente muy suave
    ambient_env = np.ones(len(ambient))
    ambient_env[:int(0.5*44100)] = np.linspace(0, 1, int(0.5*44100))
    ambient_env[-int(0.5*44100):] = np.linspace(1, 0.8, int(0.5*44100))
    
    wave[ambient_start:ambient_end] += ambient * ambient_env
    
    # Normalizar
    max_val = np.max(np.abs(wave))
    if max_val > 0:
        wave = wave / max_val * 0.9
    
    return wave


# =============================================================================
# API PÚBLICA
# =============================================================================

_player_instance: Optional[SeamlessMusicPlayer] = None


def get_player() -> SeamlessMusicPlayer:
    """Obtiene instancia global del reproductor."""
    global _player_instance
    if _player_instance is None:
        _player_instance = SeamlessMusicPlayer()
    return _player_instance


def start_epic_music(volume: float = 0.6):
    """Inicia música épica con loop seamless."""
    player = get_player()
    player.load_and_play(generate_seamless_loop, duration=16.0, volume=volume)


def stop_music():
    """Detiene la música."""
    global _player_instance
    if _player_instance:
        _player_instance.stop()


def set_volume(volume: float):
    """Cambia volumen (0.0 a 1.0)."""
    player = get_player()
    player._volume = volume
    if player._current_channel == 'A':
        player._channel_a.set_volume(volume)
    else:
        player._channel_b.set_volume(volume)
