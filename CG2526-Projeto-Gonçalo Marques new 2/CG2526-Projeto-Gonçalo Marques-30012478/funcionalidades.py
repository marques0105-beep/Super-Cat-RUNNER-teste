import pygame
import json
import os
import math
from configuracoes import *

def load_image(path, size=None, dirs=(ASSET_DIR, IMAGES_DIR), flip_x=False, flip_y=False, fallback_color=(150,150,150)):
    """Carrega uma imagem procurando nas pastas especificadas."""
    for d in dirs:
        try:
            full = os.path.join(d, path)
            img = pygame.image.load(full).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            if flip_x or flip_y:
                img = pygame.transform.flip(img, flip_x, flip_y)
            return img
        except Exception:
            continue

    # Fallback: retorna uma superfície colorida
    w, h = size if size else (50, 50)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(fallback_color)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    return surf

def detect_ground_y_from_bg(surface):
    """Tenta detectar automaticamente a linha do chão no background."""
    try:
        w, h = surface.get_size()
        sample_y = max(2, min(20, h // 20))
        sky_sample = surface.get_at((w // 2, sample_y))[:3]

        def is_greenish(col):
            r, g, b = col[:3]
            return (g > r + 10) and (g > b + 8) and (g > 40)

        start_y = int(h * 0.35)
        end_y = int(h * 0.85)
        step_x = max(1, w // 120)
        for y in range(start_y, end_y):
            samples = 0
            green_count = 0
            diff_from_sky = 0
            for x in range(0, w, step_x):
                samples += 1
                col = surface.get_at((x, y))[:3]
                if is_greenish(col):
                    green_count += 1
                dist = abs(col[0] - sky_sample[0]) + abs(col[1] - sky_sample[1]) + abs(col[2] - sky_sample[2])
                if dist > 40:
                    diff_from_sky += 1
            if samples > 0:
                green_frac = green_count / samples
                diff_frac = diff_from_sky / samples
                if green_frac > 0.18 and diff_frac > 0.25:
                    return max(0, y - 2)
                if diff_frac > 0.35:
                    return max(0, y - 4)
    except Exception:
        pass
    return int(HEIGHT * 0.8)

def create_ground_surface(bg_surface, ground_y, height=56):
    """Cria uma superfície que será usada como faixa de chão."""
    try:
        w, h = bg_surface.get_size()
        sample_w = max(10, w // 40)
        sample_h = 8
        sx = max(0, (w // 2) - sample_w // 2)
        sy = max(0, min(h - sample_h, ground_y - sample_h // 2))

        r = g = b = cnt = 0
        for xx in range(sx, min(sx + sample_w, w)):
            for yy in range(sy, min(sy + sample_h, h)):
                cr, cg, cb, *_ = bg_surface.get_at((xx, yy))
                r += cr; g += cg; b += cb; cnt += 1
        if cnt == 0:
            color = (80, 170, 70)
        else:
            r //= cnt; g //= cnt; b //= cnt
            g = min(255, int(g * 1.4))
            r = int(r * 0.7)
            b = int(b * 0.7)
            color = (r, g, b)

        surf = pygame.Surface((w, height))
        surf.fill(color)
        return surf
    except Exception:
        surf = pygame.Surface((WIDTH, height))
        surf.fill((80, 170, 70))
        return surf

def load_highscore():
    """Lê o highscore do ficheiro JSON."""
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f).get("highscore", 0)
    except:
        return 0

def save_highscore(value):
    """Persiste o highscore no ficheiro JSON."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({"highscore": value}, f)
    except Exception as e:
        print("Erro ao salvar highscore:", e)

def draw_button(surface, rect, text, base_color, hover_color, mouse_pos, selected=False, disabled=False):
    """Desenha um botão com sombra e efeitos visuais."""
    x, y, w, h = rect
    is_hover = pygame.Rect(rect).collidepoint(mouse_pos) or selected
    color = hover_color if is_hover and not disabled else base_color

    if disabled:
        color = (120, 120, 120)

    # Sombra
    shadow_rect = pygame.Rect(x + 4, y + 4, w, h)
    pygame.draw.rect(surface, (40, 40, 40), shadow_rect)

    # Botão
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=8)
    
    # Destaque se selecionado
    if selected and not disabled:
        pygame.draw.rect(surface, (255, 255, 255), (x - 3, y - 3, w + 6, h + 6), 3, border_radius=10)

    label_color = BLACK if not disabled else (80, 80, 80)
    label = BTN_FONT.render(text, True, label_color)
    surface.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))

def draw_progress_map(surface, score, level):
    """Desenha uma barra de progresso no HUD para o nível atual."""
    from configuracoes import LEVEL_DISTANCES, WIDTH, HEIGHT, HUD_FONT, BLACK
    
    total = LEVEL_DISTANCES.get(level, 1000)
    if math.isinf(total):
        return

    progress = min(1.0, score / total)

    bar_w = int(WIDTH * 0.55)
    bar_h = 6
    bar_x = WIDTH // 2 - bar_w // 2
    bar_y = HEIGHT - 60

    # Linha de fundo
    pygame.draw.line(surface, (200, 200, 200), (bar_x, bar_y), (bar_x + bar_w, bar_y), bar_h)

    # Marcador do gato
    cat_w = 18
    cat_h = 18
    cat_x = bar_x - cat_w - 12
    cat_y = bar_y - cat_h // 2
    pygame.draw.rect(surface, (60, 60, 60), (cat_x, cat_y, cat_w, cat_h))
    pygame.draw.circle(surface, (0, 0, 0), (cat_x + 5, cat_y + 6), 2)
    pygame.draw.circle(surface, (0, 0, 0), (cat_x + 13, cat_y + 6), 2)

    # Bandeira final
    flag_x = bar_x + bar_w + 12
    flag_y = bar_y - 20
    pole_h = 40
    pygame.draw.line(surface, (0, 0, 0), (flag_x, flag_y), (flag_x, flag_y + pole_h), 3)
    pygame.draw.polygon(surface, (0, 0, 0), [(flag_x, flag_y), (flag_x + 30, flag_y + 10), (flag_x, flag_y + 20)])

    # Marcador atual
    marker_x = int(bar_x + progress * bar_w)
    marker_y = bar_y
    pygame.draw.circle(surface, (255, 200, 0), (marker_x, marker_y), 8)
    pygame.draw.polygon(surface, (255, 200, 0), [(marker_x, marker_y + 12), (marker_x - 6, marker_y + 5), (marker_x + 6, marker_y + 5)])

    remaining = max(0, int(total - score))
    meters_txt = f"{remaining}m"
    m_surf = HUD_FONT.render(meters_txt, True, BLACK)
    surface.blit(m_surf, (WIDTH // 2 - m_surf.get_width() // 2, bar_y + 12))

def draw_boss_hp(surface, boss):
    """Desenha a barra de HP do boss no HUD."""
    from configuracoes import WIDTH, HEIGHT, HUD_FONT, BLACK
    
    if not boss:
        return
    bar_w = int(WIDTH * 0.25)
    bar_h = 14
    bar_x = WIDTH - bar_w - 30
    bar_y = HEIGHT - 40
    pygame.draw.rect(surface, (40, 40, 40), (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), border_radius=4)
    pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    pct = max(0.0, boss.hp / boss.max_hp)
    pygame.draw.rect(surface, (200, 30, 30), (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=4)
    txt = HUD_FONT.render(f"Boss HP: {boss.hp}/{boss.max_hp}", True, BLACK)
    surface.blit(txt, (bar_x, bar_y - 26))
