import pygame
import sys
from configuracoes import *
from funcionalidades import draw_button, load_image, save_highscore, load_highscore

def death_screen(screen, score, highscore):
    """Tela mostrada quando o jogador morre."""
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    auto_return_ms = 1800

    while True:
        elapsed = pygame.time.get_ticks() - start
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return

        screen.fill(WHITE)
        alpha = min(200, int(200 * (elapsed / auto_return_ms))) if auto_return_ms > 0 else 200
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, alpha))
        screen.blit(overlay, (0, 0))

        msg = TITLE_FONT.render("Você Morreu!", True, (255, 230, 230))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, int(HEIGHT * 0.3)))

        scr = HUD_FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(scr, (WIDTH // 2 - scr.get_width() // 2, int(HEIGHT * 0.42)))

        high_txt = HUD_FONT.render(f"Melhor Pontuação: {highscore}", True, WHITE)
        screen.blit(high_txt, (WIDTH // 2 - high_txt.get_width() // 2, int(HEIGHT * 0.48)))

        msg2 = HUD_FONT.render("Voltando ao menu...", True, WHITE)
        screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, int(HEIGHT * 0.55)))

        pygame.display.update()
        clock.tick(FPS)

        if elapsed >= auto_return_ms:
            return

def level_complete_screen(screen, level, score, highscore, has_next_level):
    """Tela mostrada quando um nível é concluído."""
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_d, pygame.K_RIGHT):
                    if has_next_level:
                        return "next"
                if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_a, pygame.K_LEFT):
                    return "menu"

        screen.fill(WHITE)
        msg = TITLE_FONT.render(f"Level {level} Concluído!", True, (20, 160, 60))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, int(HEIGHT * 0.28)))

        scr = HUD_FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(scr, (WIDTH // 2 - scr.get_width() // 2, int(HEIGHT * 0.4)))

        high_txt = HUD_FONT.render(f"High: {highscore}", True, BLACK)
        screen.blit(high_txt, (WIDTH // 2 - high_txt.get_width() // 2, int(HEIGHT * 0.46)))

        if has_next_level:
            instr1 = HUD_FONT.render("ENTER/D → Próximo nível", True, BLACK)
            screen.blit(instr1, (WIDTH // 2 - instr1.get_width() // 2, int(HEIGHT * 0.56)))
        instr2 = HUD_FONT.render("ESC/ESPAÇO/A ← Voltar ao menu", True, BLACK)
        screen.blit(instr2, (WIDTH // 2 - instr2.get_width() // 2, int(HEIGHT * 0.62)))

        pygame.display.update()
        clock.tick(FPS)

def victory_screen(screen, score, highscore):
    """Tela mostrada quando o jogador derrota o boss final."""
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                    return

        screen.fill(WHITE)
        msg = TITLE_FONT.render("Vitória!", True, (20, 160, 60))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, int(HEIGHT * 0.25)))

        scr = HUD_FONT.render(f"Score: {score}", True, BLACK)
        screen.blit(scr, (WIDTH // 2 - scr.get_width() // 2, int(HEIGHT * 0.38)))

        high_txt = HUD_FONT.render(f"High: {highscore}", True, BLACK)
        screen.blit(high_txt, (WIDTH // 2 - high_txt.get_width() // 2, int(HEIGHT * 0.44)))

        frase = HUD_FONT.render("Parabéns agora és um Super Gatão!", True, (0, 120, 0))
        screen.blit(frase, (WIDTH // 2 - frase.get_width() // 2, int(HEIGHT * 0.52)))

        instr = HUD_FONT.render("ENTER / ESC / ESPAÇO → Menu", True, BLACK)
        screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, int(HEIGHT * 0.60)))

        pygame.display.update()
        clock.tick(FPS)

def creditos(screen):
    """Tela de créditos e comandos."""
    clock = pygame.time.Clock()
    
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        title = TITLE_FONT.render("Créditos / Comandos", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.08)))

        linhas = [
            "Projeto criado por: Gonçalo Marques",
            "Nº de aluno: 30012478",
            "",
            "=== Comandos ===",
            "W, A, D: Mover",
            "W ou Espaço: Pular",
            "X: Atirar (com Power-up)",
            "P: Pausa",
            "=======================",
            "Obrigado por jogar!"
        ]

        y = int(HEIGHT * 0.22)
        for linha in linhas:
            txt = HUD_FONT.render(linha, True, BLACK)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y))
            y += 40

        btn_w, btn_h = 220, 60
        btn_x = WIDTH // 2 - btn_w // 2
        btn_y = HEIGHT - 100
        back_rect = (btn_x, btn_y, btn_w, btn_h)
        draw_button(screen, back_rect, "Voltar", GRAY, (170, 170, 170), mouse)

        # Clique do mouse no botão 'Voltar'
        if pygame.mouse.get_pressed()[0]:
            if pygame.Rect(back_rect).collidepoint(pygame.mouse.get_pos()):
                pygame.time.delay(120)
                return

        pygame.display.update()
        clock.tick(FPS)

def draw_menu_background(surface):
    """Desenha um gradiente simples como fundo do menu."""
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = int(255 * (1 - t) + 80 * t)
        g = int(120 * (1 - t) + 0 * t)
        b = int(200 * (1 - t) + 120 * t)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))

def level_select_menu(screen):
    """Tela para selecionar nível."""
    from configuracoes import unlocked_levels
    
    clock = pygame.time.Clock()
    selected_idx = 0
    levels = [1, 2, 3, 4, 5]
    buttons = []
    btn_w, btn_h = int(WIDTH * 0.24), 60
    start_y = int(HEIGHT * 0.25)
    spacing = 15

    # Cria retângulos para botões de cada nível
    for i, lvl in enumerate(levels):
        x = WIDTH // 2 - btn_w // 2
        y = start_y + i * (btn_h + spacing)
        buttons.append({
            "label": f"Level {lvl}",
            "rect": (x, y, btn_w, btn_h),
            "level": lvl
        })

    # Botão voltar
    back_btn_w, back_btn_h = 220, 60
    back_btn_x = WIDTH // 2 - back_btn_w // 2
    back_btn_y = HEIGHT - 100
    back_rect = (back_btn_x, back_btn_y, back_btn_w, back_btn_h)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Navegação por teclado
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chosen = buttons[selected_idx]
                    lvl = chosen["level"]
                    if lvl <= unlocked_levels:
                        # Importa aqui para evitar importação circular
                        from project_2 import main_game
                        main_game(screen, start_level=lvl)
                        return
                elif event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clique com rato
                for i, b in enumerate(buttons):
                    if pygame.Rect(b["rect"]).collidepoint(event.pos):
                        lvl = b["level"]
                        if lvl <= unlocked_levels:
                            from project_2 import main_game
                            main_game(screen, start_level=lvl)
                            return
                if pygame.Rect(back_rect).collidepoint(event.pos):
                    pygame.time.delay(120)
                    return

        # Desenha interface
        screen.fill(WHITE)
        title = TITLE_FONT.render("Selecionar Nível", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.12)))

        for i, b in enumerate(buttons):
            lvl = b["level"]
            disabled = lvl > unlocked_levels
            label = b["label"] + (" (bloqueado)" if disabled else "")
            is_selected = (i == selected_idx)
            draw_button(screen, b["rect"], label, PRIMARY, PRIMARY_HOVER, mouse, selected=is_selected, disabled=disabled)

        draw_button(screen, back_rect, "Voltar", GRAY, (170, 170, 170), mouse)

        pygame.display.update()
        clock.tick(FPS)

def menu(screen):
    """Menu principal do jogo."""
    clock = pygame.time.Clock()
    selected_idx = 0

    buttons = [
        {"label": "Jogar", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3), 320, 64), 
         "base": PRIMARY, "hover": PRIMARY_HOVER, "action": "play"},
        {"label": "Selecionar Nível", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3) + 80, 320, 64), 
         "base": PRIMARY, "hover": PRIMARY_HOVER, "action": "level_select"},
        {"label": "Créditos/Comandos", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3) + 160, 320, 64), 
         "base": GRAY, "hover": (170, 170, 200), "action": "credits"},
        {"label": "Sair", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3) + 240, 320, 64), 
         "base": RED, "hover": RED_HOVER, "action": "quit"},
    ]

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Teclado: navegar e confirmar
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = buttons[selected_idx]["action"]
                    if action == "play":
                        from project_2 import main_game
                        main_game(screen, start_level=1)
                    elif action == "level_select":
                        level_select_menu(screen)
                    elif action == "credits":
                        creditos(screen)
                    elif action == "quit":
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clique do mouse nos botões
                for i, b in enumerate(buttons):
                    if pygame.Rect(b["rect"]).collidepoint(event.pos):
                        if b["action"] == "play":
                            from project_2 import main_game
                            main_game(screen, start_level=1)
                        elif b["action"] == "level_select":
                            level_select_menu(screen)
                        elif b["action"] == "credits":
                            creditos(screen)
                        elif b["action"] == "quit":
                            pygame.quit()
                            sys.exit()

        # Desenha fundo e títulos
        draw_menu_background(screen)

        title = TITLE_FONT_MENU.render("Super Cat Runner", True, (255, 240, 0))
        outline_color = (0, 0, 0)

        # Desenha um pequeno contorno deslocado para criar efeito de outline
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            shadow = TITLE_FONT_MENU.render("Super Cat Runner", True, outline_color)
            screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + dx,
                                 int(HEIGHT * 0.12) + dy))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.12)))

        # Desenha botões e destaques
        for i, b in enumerate(buttons):
            is_selected = (i == selected_idx)
            draw_button(screen, b["rect"], b["label"], b["base"], b["hover"], mouse, selected=is_selected)

        pygame.display.update()
        clock.tick(FPS)

