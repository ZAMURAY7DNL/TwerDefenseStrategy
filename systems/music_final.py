"""
Music Final - Sistema definitivo de música
============================================
Usa el archivo de 3 minutos generado.
"""
import pygame
import os


def start_music(volume=0.5):
    """Inicia la música de 3 minutos."""
    
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    # Buscar archivo de música
    music_file = None
    
    # Primero intentar el de 3 minutos
    if os.path.exists('epic_song_3min.wav'):
        music_file = 'epic_song_3min.wav'
        print(f"[MUSIC] Cargando canción de 3 minutos: {music_file}")
    elif os.path.exists('epic_song_3min.ogg'):
        music_file = 'epic_song_3min.ogg'
        print(f"[MUSIC] Cargando canción de 3 minutos: {music_file}")
    else:
        print("[MUSIC] ERROR: No se encontró archivo de música")
        print("[MUSIC] Ejecuta: python generate_song_fast.py")
        return
    
    # Cargar y reproducir
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        print(f"[MUSIC] Reproduciendo (vol: {volume})")
    except Exception as e:
        print(f"[MUSIC] Error: {e}")


def stop_music():
    """Detiene la música."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()


def set_volume(vol):
    """Cambia volumen."""
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(vol)


def is_playing():
    """Retorna True si está sonando."""
    return pygame.mixer.music.get_busy()
