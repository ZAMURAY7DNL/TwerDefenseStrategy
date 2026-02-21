"""
Demo Interactivo de Sonidos - Tactical Defense
===============================================
Prueba todos los sonidos generados proceduralmente.
Controles:
    1-9 : Sonidos de gameplay
    Q-R : UI y poderes
    A,S,D : Pasos en diferentes superficies
    M : Iniciar/Detener música ambient
    ESC : Salir
"""
import sys
import pygame
sys.path.insert(0, str(__file__).replace('dev_tools\\sound_demo.py', ''))

from systems.sound_generator import SoundGenerator, get_sound_generator


def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("🎵 Demo de Sonidos - Tactical Defense")
    
    font = pygame.font.SysFont("consolas", 24)
    font_small = pygame.font.SysFont("consolas", 16)
    font_title = pygame.font.SysFont("consolas", 28, bold=True)
    
    # Inicializar generador
    print("[INFO] Generando sonidos... (puede tomar unos segundos)")
    sound_gen = get_sound_generator()
    
    # Precargar sonidos
    sounds = {
        # Gameplay
        pygame.K_1: ("1 - Coin", sound_gen.coin_collect('high')),
        pygame.K_2: ("2 - Power Up", sound_gen.power_up()),
        pygame.K_3: ("3 - Hit", sound_gen.hit_impact('medium')),
        pygame.K_4: ("4 - Victory", sound_gen.victory_jingle()),
        pygame.K_5: ("5 - Defeat", sound_gen.defeat_sound()),
        
        # UI  
        pygame.K_q: ("Q - Button Hover", sound_gen.button_hover()),
        pygame.K_w: ("W - Button Click", sound_gen.button_click()),
        pygame.K_e: ("E - Button Back", sound_gen.button_back()),
        
        # Pasos
        pygame.K_a: ("A - Step Grass", sound_gen.footstep('grass', 'normal')),
        pygame.K_s: ("S - Step Stone", sound_gen.footstep('stone', 'normal')),
    }
    
    print(f"[OK] {len(sounds)} sonidos cargados!")
    
    running = True
    last_played = "Presiona una tecla..."
    music_playing = False
    
    clock = pygame.time.Clock()
    
    # Iniciar música automáticamente al principio
    sound_gen.play_main_theme()
    music_playing = True
    
    while running:
        screen.fill((20, 25, 35))
        
        # Título
        title = font_title.render("🎵 GENERADOR DE SONIDOS PROCEDURAL", True, (255, 215, 0))
        screen.blit(title, (50, 30))
        
        # Subtítulo
        subtitle = font_small.render("MELODÍA PRINCIPAL ÉPICA - 32 segundos - Tema que vuelve constantemente", True, (255, 215, 0))
        screen.blit(subtitle, (50, 65))
        
        # Sección: Gameplay
        y = 110
        section = font.render("GAMEPLAY", True, (100, 200, 255))
        screen.blit(section, (50, y))
        y += 35
        
        for key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, 
                    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
            if key in sounds:
                desc, _ = sounds[key]
                text = font_small.render(desc, True, (200, 220, 255))
                screen.blit(text, (50, y))
                y += 25
        
        # Sección: UI y Pasos
        y = 110
        section = font.render("UI & PASOS", True, (100, 255, 150))
        screen.blit(section, (450, y))
        y += 35
        
        for key in [pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r,
                    pygame.K_a, pygame.K_s, pygame.K_d]:
            if key in sounds:
                desc, _ = sounds[key]
                text = font_small.render(desc, True, (200, 220, 255))
                screen.blit(text, (450, y))
                y += 25
        
        # Sección: Música
        y = 320
        section = font.render("MÚSICA", True, (255, 150, 200))
        screen.blit(section, (450, y))
        y += 35
        
        music_text = "M - MELODÍA PRINCIPAL: " + ("🎵 ON (32 seg bucle)" if music_playing else "🔇 OFF")
        text = font_small.render(music_text, True, (255, 215, 0))
        screen.blit(text, (450, y))
        y += 25
        
        style_text = "Tema épico dominante | Vuelve 2 veces por bucle | Transiciones suaves"
        text = font_small.render(style_text, True, (180, 180, 180))
        screen.blit(text, (450, y))
        
        # Instrucciones extra
        y += 40
        text = font_small.render("F - Reproducir secuencia de pasos", True, (180, 180, 180))
        screen.blit(text, (450, y))
        
        # Separador
        pygame.draw.line(screen, (80, 80, 80), (50, 480), (850, 480), 2)
        
        # Información técnica
        info_y = 500
        info_lines = [
            "CARACTERÍSTICAS TÉCNICAS:",
            "• Frecuencias 1-4kHz (rango auditivo óptimo)",
            "• Ataque <10ms (respuesta inmediata)",
            "• Decay exponencial (satisfacción auditiva)",
            "• Pitch ascendente = Recompensa (programado en cerebro)",
            "",
            "TIPOS DE ONDAS: Sine, Square, Sawtooth, Triangle, Noise",
            "EFECTOS: Vibrato, Detune, Panning estéreo, Envolventes ADSR",
        ]
        
        for line in info_lines:
            color = (255, 215, 0) if line.endswith(':') else (150, 150, 150)
            text = font_small.render(line, True, color)
            screen.blit(text, (50, info_y))
            info_y += 22
        
        # Último sonido reproducido
        status_color = (100, 255, 100) if last_played != "Presiona una tecla..." else (150, 150, 150)
        status = font.render(f"Último: {last_played}", True, status_color)
        screen.blit(status, (50, 660))
        
        # Ayuda
        help_text = font_small.render("ESC: Salir", True, (100, 100, 100))
        screen.blit(help_text, (750, 665))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key in sounds:
                    desc, sound = sounds[event.key]
                    sound.play()
                    last_played = desc
                    print(f"[PLAY] {desc}")
                
                elif event.key == pygame.K_m:
                    if music_playing:
                        sound_gen.stop_music()
                        music_playing = False
                        last_played = "Melodía detenida"
                    else:
                        sound_gen.play_main_theme()
                        music_playing = True
                        last_played = "Melodía principal iniciada"
                
                elif event.key == pygame.K_f:
                    # Secuencia de pasos
                    last_played = "Secuencia de pasos"
                    print("[PLAY] Secuencia de 4 pasos")
                    import threading
                    def play_steps():
                        for i in range(4):
                            sound_gen.footstep('grass', 'normal').play()
                            pygame.time.delay(300)
                    threading.Thread(target=play_steps, daemon=True).start()
        
        clock.tick(60)
    
    # Detener música al salir
    sound_gen.stop_ambient_music()
    pygame.quit()
    print("[INFO] Demo terminado")


if __name__ == "__main__":
    main()
