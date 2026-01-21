# project_2.py
import pygame
import sys
import random
import math
from configuracoes import *
from funcionalidades import (
    load_image, detect_ground_y_from_bg, create_ground_surface,
    load_highscore, save_highscore, draw_button, draw_progress_map, draw_boss_hp
)
from entidades import (
    Gato, Projetil, BossProjetil, Tronco, Bird, PowerUp, Boss
)

def main_game(screen, start_level=1):
    """Função principal que executa a lógica do jogo para um nível."""
    global unlocked_levels
    global GROUND_Y

    clock = pygame.time.Clock()
    run = True

    # Carrega background
    bg = load_image("game_bg.png", (WIDTH, HEIGHT))

    # Detecta posição do chão
    if MANUAL_GROUND_Y is not None:
        detected_ground = int(MANUAL_GROUND_Y)
    else:
        detected_ground = detect_ground_y_from_bg(bg)
    GROUND_Y = max(0, detected_ground)

    # Cria superfície verde do chão
    ground_height = 56
    ground_surface = create_ground_surface(bg, GROUND_Y, height=ground_height)

    # Instancia o jogador
    gato = Gato()
    gato.Y_POS = GROUND_Y - gato.rect.height
    gato.y = float(gato.Y_POS)
    gato.rect.topleft = (gato.X_POS, gato.Y_POS)

    # Listas para entidades dinâmicas
    obstacles = []
    bullets = []
    powerups = []
    boss_bullets = []

    # Variáveis de jogo
    score = 0
    speed = 12 + 2 * (start_level - 1)
    level = start_level

    boss = None
    boss_active = False
    paused = False

    highscore = load_highscore()

    bg_x = 0
    bg_speed = 4

    # Temporizadores
    obstacle_spawn_interval = max(26, 64 - (level - 1) * 6)
    obstacle_spawn_timer = obstacle_spawn_interval
    max_obstacles_base = 5

    if level == 5:
        powerup_spawn_interval = 220
    else:
        powerup_spawn_interval = 480
    powerup_spawn_timer = 0

    level_distance = LEVEL_DISTANCES.get(level, 1000)

    # Se é boss level, inicializa o boss
    if math.isinf(level_distance):
        boss = Boss()
        boss_active = True

    # LOOP PRINCIPAL DO NÍVEL
    while run:
        dt = clock.tick(FPS) / 1000.0
        mouse = pygame.mouse.get_pos()
        user_input = pygame.key.get_pressed()

        # ========== EVENTOS ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore(max(score, highscore))
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and gato.can_shoot and not paused:
                    gato.shoot()
                    bullets.append(Projetil(gato.rect.right, gato.rect.centery))
                if event.key == pygame.K_p:
                    paused = not paused

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and paused:
                btn_w, btn_h = 260, 70
                btn_x = WIDTH // 2 - btn_w // 2
                btn_y = HEIGHT // 2 + 50
                menu_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                if menu_rect.collidepoint(event.pos):
                    save_highscore(max(score, highscore))
                    return

        # ========== PAUSA ==========
        if paused:
            screen.fill((0, 0, 0))
            pause_txt = TITLE_FONT.render("PAUSADO", True, WHITE)
            instr_txt = HUD_FONT.render("P: Continuar", True, WHITE)
            screen.blit(pause_txt, (WIDTH // 2 - pause_txt.get_width() // 2, HEIGHT // 2 - 180))
            screen.blit(instr_txt, (WIDTH // 2 - instr_txt.get_width() // 2, HEIGHT // 2 - 110))

            btn_w, btn_h = 260, 70
            btn_x = WIDTH // 2 - btn_w // 2
            btn_y = HEIGHT // 2 + 50
            menu_rect = (btn_x, btn_y, btn_w, btn_h)
            draw_button(screen, menu_rect, "Voltar ao Menu", PRIMARY, PRIMARY_HOVER, mouse)

            pygame.display.update()
            continue

        # ========== ATUALIZAÇÕES ==========
        gato.update(user_input)

        # Verifica se completou o nível
        if not math.isinf(level_distance) and score >= level_distance:
            if level + 1 > unlocked_levels:
                unlocked_levels = level + 1
                from configuracoes import save_unlocked_levels
                save_unlocked_levels()  # SALVA O PROGRESSO
            save_highscore(max(score, highscore))
            
            has_next_level = (level < 5)
            
            from interfaces import level_complete_screen
            escolha = level_complete_screen(screen, level, score, max(score, highscore), has_next_level)
            
            if escolha == "next" and has_next_level:
                main_game(screen, start_level=level + 1)
                return
            else:
                return

        # ========== LÓGICA DO BOSS ==========
        if boss_active and boss:
            boss.update(gato.rect)

            if boss.should_shoot_now():
                on_ground = (boss.rect.bottom >= GROUND_Y - 2)
                offset_y = random.randint(-34, 34)
                bullet_y = boss.rect.centery + offset_y

                if on_ground:
                    vx = -13
                    vy = 0
                else:
                    dy = (gato.rect.centery - boss.rect.centery)
                    vy = max(min(dy * 0.06, 8), -2)
                    vx = -10
                spawn_x = boss.rect.left - 20
                boss_bullets.append(BossProjetil(spawn_x, bullet_y, vx=vx, vy=vy))

            if boss.hp <= 0:
                unlocked_levels = max(unlocked_levels, 5)
                from configuracoes import save_unlocked_levels
                save_unlocked_levels()  # SALVA QUE DESBLOQUEOU O BOSS
                pygame.time.delay(400)
                save_highscore(max(score, highscore))
                from interfaces import victory_screen
                victory_screen(screen, score, max(score, highscore))
                return

            if gato.rect.colliderect(boss.get_collision_rect()):
                pygame.time.delay(300)
                save_highscore(max(score, highscore))
                from interfaces import death_screen
                death_screen(screen, score, max(score, highscore))
                return

        # ========== PROJÉTEIS ==========
        for bullet in bullets[:]:
            bullet.update()

            hit_bullet = False
            for b_b in boss_bullets[:]:
                if bullet.rect.colliderect(b_b.rect):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if b_b in boss_bullets:
                        boss_bullets.remove(b_b)
                    hit_bullet = True
                    break
            if hit_bullet:
                continue

            if boss_active and boss and bullet.rect.colliderect(boss.get_collision_rect()):
                boss.take_hit(from_state=boss.state)
                if bullet in bullets:
                    bullets.remove(bullet)
                continue

            hit = False
            for obstacle in obstacles[:]:
                if bullet.rect.colliderect(obstacle.rect):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if obstacle in obstacles:
                        obstacles.remove(obstacle)
                    hit = True
                    break
            if hit:
                continue

            if bullet.rect.x > WIDTH + 200 and bullet in bullets:
                bullets.remove(bullet)

        for b_bullet in boss_bullets[:]:
            b_bullet.update()
            if b_bullet.rect.colliderect(gato.rect):
                pygame.time.delay(200)
                save_highscore(max(score, highscore))
                from interfaces import death_screen
                death_screen(screen, score, max(score, highscore))
                return
            if b_bullet.rect.right < -50 or b_bullet.rect.top > HEIGHT + 200 or b_bullet.rect.bottom < -200:
                if b_bullet in boss_bullets:
                    boss_bullets.remove(b_bullet)

        # ========== OBSTÁCULOS ==========
        if not boss_active:
            obstacle_spawn_timer -= 1
            if obstacle_spawn_timer <= 0:
                max_obstacles = max_obstacles_base + level
                min_spacing = int(WIDTH * max(0.18, 0.35 - 0.03 * (level - 1)))
                rightmost = max((obs.rect.right for obs in obstacles), default=-9999)
                if len(obstacles) < max_obstacles and rightmost <= WIDTH - min_spacing:
                    bird_prob = min(0.5, 0.12 + 0.06 * (level - 1))
                    if level >= 3:
                        bird_prob = min(0.45, bird_prob + 0.06)
                    if random.random() < bird_prob:
                        obstacles.append(Bird())
                    else:
                        obstacles.append(Tronco())

                base_interval = max(22, 70 - level * 8)
                obstacle_spawn_interval = base_interval + random.randint(-8, 12)
                obstacle_spawn_interval = max(18, obstacle_spawn_interval - (score // 2000))
                obstacle_spawn_timer = obstacle_spawn_interval

            for obstacle in obstacles[:]:
                obstacle.update(speed)
                if gato.rect.colliderect(obstacle.rect):
                    pygame.time.delay(300)
                    save_highscore(max(score, highscore))
                    from interfaces import death_screen
                    death_screen(screen, score, max(score, highscore))
                    return
                if obstacle.rect.x < -200 and obstacle in obstacles:
                    obstacles.remove(obstacle)

        # ========== POWERUPS ==========
        powerup_spawn_timer -= 1
        if powerup_spawn_timer <= 0 and len(powerups) == 0:
            if math.isinf(level_distance):
                chance = 1
            else:
                chance = 3
            if random.randint(0, chance) == 0:
                powerups.append(PowerUp())
            powerup_spawn_timer = powerup_spawn_interval

        for p in powerups[:]:
            p.update(speed)
            if gato.rect.colliderect(p.rect):
                gato.activate_powerup(10)
                powerups.remove(p)
            elif p.rect.right < -100:
                powerups.remove(p)

        # ========== DESENHO ==========
        bg_x -= bg_speed
        if bg_x <= -WIDTH:
            bg_x = 0

        screen.fill(WHITE)
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + WIDTH, 0))
        screen.blit(ground_surface, (bg_x, GROUND_Y))
        screen.blit(ground_surface, (bg_x + WIDTH, GROUND_Y))

        gato.draw(screen)
        for b in bullets:
            b.draw(screen)
        for b_b in boss_bullets:
            b_b.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        for p in powerups:
            p.draw(screen)
        if boss_active and boss:
            boss.draw(screen)

        score += 1

        # HUD
        score_text = HUD_FONT.render(f"Score: {score}", True, BLACK)
        level_text = HUD_FONT.render(f"Level: {level}", True, BLACK)
        high_text = HUD_FONT.render(f"High: {highscore}", True, BLACK)
        hud_x = WIDTH - 260
        screen.blit(score_text, (hud_x, 20))
        screen.blit(level_text, (hud_x, 55))
        screen.blit(high_text, (hud_x, 90))

        if gato.can_shoot:
            remaining = max(0, gato.shoot_timer_powerup // FPS)
            p_txt = HUD_FONT.render(f"Power-up: {remaining}s", True, (255, 100, 0))
            screen.blit(p_txt, (20, 20))

        draw_progress_map(screen, score, level)

        if boss_active and boss:
            draw_boss_hp(screen, boss)

        pygame.display.update()

# Ponto de entrada principal
if __name__ == "__main__":
    # Inicializa pygame
    pygame.init()
    
    # Cria a janela em fullscreen
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Super Cat Runner")
    
    # Importa e inicia o menu
    from interfaces import menu
    menu(screen)
