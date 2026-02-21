"""
Music External - Carga música desde archivo externo
====================================================
En lugar de generar proceduralmente, carga un archivo de música.
Esto permite usar música profesional o generada por otras herramientas.

Instrucciones para agregar tu propia música:
1. Coloca tu archivo de música en la carpeta del juego como 'bg_music_long.ogg'
2. El archivo debe ser:
   - Formato: OGG (recomendado) o MP3/WAV
   - Duración: 2-3 minutos
   - Loop perfecto: que el final conecte con el inicio

Si no existe el archivo, se usa el generado anteriormente.
"""
import pygame
import os


def start_music(volume=0.5):
    """
    Inicia la música de fondo.
    Busca archivos en orden de prioridad.
    """
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    
    # Buscar archivos de música en orden de preferencia
    music_files = [
        'epic_song_3min.ogg',      # Canción de 3 minutos generada
        'epic_song_3min.wav',      # Versión WAV
        'bg_music_fixed.ogg',      # Versión anterior
        'bg_music.ogg',            # Versión básica
    ]
    
    music_file = None
    for f in music_files:
        if os.path.exists(f):
            music_file = f
            print(f"[MUSIC] Encontrado: {f}")
            break
    
    if music_file is None:
        print("[MUSIC] ERROR: No se encontró archivo de música")
        print("[MUSIC] Coloca un archivo llamado 'epic_song_3min.ogg' en la carpeta del juego")
        return
    
    # Cargar y reproducir
    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        print(f"[MUSIC] Reproduciendo: {music_file} (vol: {volume})")
    except Exception as e:
        print(f"[MUSIC] Error al cargar: {e}")


def stop_music():
    pygame.mixer.music.stop()


def set_volume(vol):
    pygame.mixer.music.set_volume(vol)


def is_playing():
    return pygame.mixer.music.get_busy()


if __name__ == "__main__":
    import time
    pygame.init()
    
    print("Buscando música...")
    start_music(0.5)
    
    if is_playing():
        print("Reproduciendo... (Ctrl+C para detener)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    stop_music()
    print("Detenido")
