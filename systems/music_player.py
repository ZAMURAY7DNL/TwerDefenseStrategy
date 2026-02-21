"""
Music Player - Sistema de Música Robusto
=========================================
Sistema simplificado y confiable para música de fondo.
Maneja bucles manualmente para máxima confiabilidad.
"""
import pygame
import numpy as np
import threading
import time
from typing import Optional


class MusicPlayer:
    """
    Reproductor de música dedicado y robusto.
    
    Características:
    - Canal dedicado (0) que nadie más usa
    - Bucle manual (no depende de pygame loops=-1)
    - Verificación constante en thread separado
    - Reinicio inmediato si se detiene
    """
    
    def __init__(self):
        # Asegurar que el mixer esté inicializado
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Reservar canal 0 exclusivamente
        pygame.mixer.set_reserved(1)
        self._channel = pygame.mixer.Channel(0)
        
        self._current_music: Optional[pygame.mixer.Sound] = None
        self._is_playing = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitor = False
        
    def load_and_play(self, generate_func, duration: float = 32.0, volume: float = 0.7):
        """
        Carga y reproduce música generada proceduralmente.
        
        Args:
            generate_func: Función que genera el array de audio
            duration: Duración del bucle en segundos
            volume: Volumen (0.0 a 1.0)
        """
        # Detener cualquier música anterior
        self.stop()
        
        # Generar música
        print(f"[MUSIC] Generando música ({duration}s)...")
        try:
            samples = int(44100 * duration)
            t = np.linspace(0, duration, samples, False)
            
            # Llamar función generadora
            wave = generate_func(t, samples, duration)
            
            # Normalizar y convertir
            if np.max(np.abs(wave)) > 0:
                wave = wave / np.max(np.abs(wave)) * 0.8
            
            stereo = np.column_stack((wave, wave))
            stereo = (stereo * 32767).astype(np.int16)
            
            self._current_music = pygame.mixer.Sound(buffer=stereo.tobytes())
            self._current_music.set_volume(volume)
            
            # Reproducir
            self._channel.play(self._current_music, loops=-1)
            self._is_playing = True
            
            print("[MUSIC] Música iniciada - Bucle infinito activo")
            
            # Iniciar monitor en thread separado
            self._stop_monitor = False
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            
        except Exception as e:
            print(f"[MUSIC ERROR] {e}")
    
    def _monitor_loop(self):
        """Thread que monitorea la música constantemente."""
        check_interval = 0.3  # Revisar cada 300ms
        
        while not self._stop_monitor:
            if self._is_playing:
                try:
                    # Si el canal no está ocupado, reiniciar
                    if not self._channel.get_busy():
                        print("[MUSIC] Reiniciando (canal vacío)...")
                        if self._current_music:
                            self._channel.play(self._current_music, loops=-1)
                    
                    # Verificar que tengamos el canal correcto
                    if self._channel != pygame.mixer.Channel(0):
                        self._channel = pygame.mixer.Channel(0)
                        
                except Exception as e:
                    print(f"[MUSIC MONITOR ERROR] {e}")
            
            time.sleep(check_interval)
    
    def stop(self):
        """Detiene la música y el monitor."""
        self._is_playing = False
        self._stop_monitor = True
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        
        try:
            self._channel.stop()
        except:
            pass
        
        self._current_music = None
        print("[MUSIC] Música detenida")
    
    def is_playing(self) -> bool:
        """Retorna True si la música está sonando."""
        if not self._is_playing:
            return False
        try:
            return self._channel.get_busy()
        except:
            return False
    
    def set_volume(self, volume: float):
        """Cambia el volumen (0.0 a 1.0)."""
        try:
            self._channel.set_volume(volume)
        except:
            pass


# =============================================================================
# GENERADORES DE MÚSICA
# =============================================================================

def generate_epic_theme(t: np.ndarray, samples: int, duration: float) -> np.ndarray:
    """
    Genera el tema épico principal.
    Melodía memorable que buclea perfectamente.
    """
    wave = np.zeros(samples, dtype=float)
    
    bpm = 120
    beat_duration = 60 / bpm
    
    # Helper para agregar notas
    def add_note(freq: float, start_beat: float, duration_beats: float, volume: float = 0.3):
        start_idx = int(start_beat * beat_duration * 44100)
        end_idx = int((start_beat + duration_beats) * beat_duration * 44100)
        end_idx = min(end_idx, samples)
        
        if start_idx >= samples:
            return
        
        note_len = end_idx - start_idx
        t_note = np.linspace(0, duration_beats * beat_duration, note_len, False)
        
        # Mezcla de ondas para sonido rico
        square = np.where((t_note * freq) % 1.0 < 0.5, 1.0, -1.0) * 0.6
        sine = np.sin(2 * np.pi * freq * t_note) * 0.4
        note = square + sine
        
        # Envolvente ADSR
        attack = min(int(0.05 * 44100), note_len // 4)
        env = np.ones(note_len) * 0.7
        env[:attack] = np.linspace(0, 1, attack)
        if note_len > attack:
            env[-attack:] = np.linspace(0.7, 0, attack)
        
        wave[start_idx:end_idx] += note * env * volume
    
    # === MELODÍA PRINCIPAL ===
    # Tema épico en A menor
    
    # Primera frase (0-8 beats)
    add_note(440, 0, 1.0, 0.35)      # A4
    add_note(523.25, 1, 0.5, 0.3)    # C5
    add_note(659.25, 1.5, 0.5, 0.3)  # E5
    add_note(783.99, 2, 1.0, 0.35)   # G5
    add_note(880, 3, 1.0, 0.4)       # A5 (climax)
    
    # Segunda frase (4-8 beats)
    add_note(880, 4, 0.5, 0.35)
    add_note(783.99, 4.5, 0.5, 0.3)
    add_note(659.25, 5, 0.5, 0.3)
    add_note(587.33, 5.5, 0.5, 0.3)  # D5
    add_note(523.25, 6, 1.0, 0.3)    # C5
    add_note(440, 7, 1.0, 0.35)      # A4
    
    # Tercera frase - variación (8-16 beats)
    add_note(523.25, 8, 0.75, 0.3)   # C5
    add_note(587.33, 8.75, 0.25, 0.25)
    add_note(659.25, 9, 0.75, 0.3)   # E5
    add_note(523.25, 9.75, 0.25, 0.25)
    add_note(440, 10, 2.0, 0.35)     # A4 larga
    
    # Cierre que conecta al inicio (14-16 beats)
    add_note(392, 12, 0.5, 0.25)     # G4
    add_note(440, 12.5, 0.5, 0.3)    # A4
    add_note(349.23, 13, 1.0, 0.25)  # F4
    add_note(440, 14, 2.0, 0.35)     # A4 - resolución
    
    # === ARMONÍA (Pads) ===
    chord_duration = 4.0  # 4 beats por acorde
    chords = [
        ([220, 261.63, 329.63], 0),      # Am
        ([174.61, 220, 261.63], 4),      # F
        ([196, 246.94, 293.66], 8),      # G
        ([220, 261.63, 329.63], 12),     # Am
    ]
    
    for freqs, start_beat in chords:
        start_idx = int(start_beat * beat_duration * 44100)
        end_idx = int((start_beat + chord_duration) * beat_duration * 44100)
        end_idx = min(end_idx, samples)
        
        if start_idx >= samples:
            continue
        
        chord_len = end_idx - start_idx
        t_chord = np.linspace(0, chord_duration * beat_duration, chord_len, False)
        
        chord_wave = np.zeros(chord_len)
        for freq in freqs:
            chord_wave += np.sin(2 * np.pi * freq * t_chord) * 0.15
        
        # Envolvente suave
        fade = int(0.5 * 44100)
        env = np.ones(chord_len)
        if chord_len > 2 * fade:
            env[:fade] = np.linspace(0, 1, fade) ** 2
            env[-fade:] = np.linspace(1, 0, fade) ** 2
        
        wave[start_idx:end_idx] += chord_wave * env * 0.4
    
    # === BAJO ===
    bass_notes = [
        (110, 0, 2), (110, 2, 2),      # A2
        (87.31, 4, 2), (87.31, 6, 2),  # F2
        (98, 8, 2), (98, 10, 2),       # G2
        (110, 12, 4),                   # A2 larga
    ]
    
    for freq, start_beat, dur in bass_notes:
        start_idx = int(start_beat * beat_duration * 44100)
        end_idx = int((start_beat + dur) * beat_duration * 44100)
        end_idx = min(end_idx, samples)
        
        if start_idx >= samples:
            continue
        
        note_len = end_idx - start_idx
        t_note = np.linspace(0, dur * beat_duration, note_len, False)
        
        # Onda triangular para bajo
        tri = 2 * np.abs(2 * ((t_note * freq) % 1.0) - 1) - 1
        sub = np.sin(2 * np.pi * freq * 0.5 * t_note)
        note = tri * 0.5 + sub * 0.3
        
        env = np.exp(-t_note * 3) * 0.7 + 0.3
        wave[start_idx:end_idx] += note * env * 0.25
    
    return wave


# Instancia global
_music_player_instance: Optional[MusicPlayer] = None


def get_music_player() -> MusicPlayer:
    """Obtiene la instancia global del reproductor."""
    global _music_player_instance
    if _music_player_instance is None:
        _music_player_instance = MusicPlayer()
    return _music_player_instance


def start_epic_music():
    """Inicia la música épica de batalla."""
    player = get_music_player()
    player.load_and_play(generate_epic_theme, duration=16.0, volume=0.6)


def stop_music():
    """Detiene la música."""
    player = get_music_player()
    player.stop()


def is_music_playing() -> bool:
    """Retorna True si la música está sonando."""
    player = get_music_player()
    return player.is_playing()
