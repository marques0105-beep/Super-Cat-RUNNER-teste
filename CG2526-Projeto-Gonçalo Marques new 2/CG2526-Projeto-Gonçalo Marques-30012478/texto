import pygame
import random
import sys
import json
import os
import math

# Inicializa o pygame (cria módulos internos necessários)
pygame.init()

# ========================= CONFIGURAÇÕES INICIAIS =========================

# Obtém as dimensões do monitor atual para inicializar fullscreen
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Cria a janela em fullscreen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Título da janela
pygame.display.set_caption("Super Cat Runner")

# Cores usadas no jogo (tuplas RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Frames por segundo alvo e relógio do pygame
FPS = 60
clock = pygame.time.Clock()

# Diretórios de assets: pasta base e pasta alternativa "Imagens_usadas"
ASSET_DIR = "."
IMAGES_DIR = os.path.join(ASSET_DIR, "Imagens_usadas")

# Ficheiro onde o highscore será guardado
HIGHSCORE_FILE = "highscore.json"

# Permite forçar uma posição do chão manualmente (se quiseres)
# Se quiseres que a detecção automática seja sempre usada, define para None
MANUAL_GROUND_Y = 780

# Valor padrão (caso não se use MANUAL_GROUND_Y)
GROUND_Y = int(HEIGHT * 0.8)

# Quantidade de níveis desbloqueados no arranque
unlocked_levels = 1

# ========================= CONSTANTES DE JOGO =========================

# Tamanhos (pixels) usados para sprites principais
PLAYER_SIZE_NORMAL = (140, 140)
PLAYER_SIZE_SHOOT = (150, 150)
FIREBALL_SIZE = (64, 64)
BOSS_BULLET_SIZE = (98, 98)
POWERUP_SIZE = (110, 110)

# Ajustes da hitbox do Boss para colisões mais precisas
BOSS_HITBOX_INSET = (140, 120)
BOSS_HITBOX_OFFSET = (-28, 0)

# Parâmetros para troncos (obstáculos)
CACTUS_SCALE_MIN = 0.75
CACTUS_SCALE_MAX = 1.25

# Limites absolutos para as dimensões dos troncos
CACTUS_MIN_WIDTH = 60
CACTUS_MAX_WIDTH = 160
CACTUS_MIN_HEIGHT = 60
CACTUS_MAX_HEIGHT = min(int(PLAYER_SIZE_NORMAL[1] * 1.05), int(HEIGHT * 0.33))

# ========================= FUNÇÕES DE UTILIDADE E ASSETS =========================

def load_image(path, size=None, dirs=(ASSET_DIR, IMAGES_DIR), flip_x=False, flip_y=False, fallback_color=(150,150,150)):
    
    #Carrega uma imagem procurando nas pastas especificadas.
    for d in dirs:
        try:
            full = os.path.join(d, path)  # caminho completo ao ficheiro candidato
            img = pygame.image.load(full).convert_alpha()  # carrega imagem com alpha
            if size:
                img = pygame.transform.scale(img, size)  # redimensiona se pedido
            if flip_x or flip_y:
                img = pygame.transform.flip(img, flip_x, flip_y)
            return img
        except Exception:
            # ignora erro e tenta o próximo diretório
            continue

    # Se nenhuma imagem foi encontrada, retorna uma superfície de fallback visível
    w, h = size if size else (50, 50)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(fallback_color)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    return surf

def detect_ground_y_from_bg(surface):
    
    #Tenta detectar automaticamente a linha do chão no background.
    try:
        w, h = surface.get_size()
        sample_y = max(2, min(20, h // 20))
        sky_sample = surface.get_at((w // 2, sample_y))[:3]  # cor aproximada do céu

        def is_greenish(col):
            r, g, b = col[:3]
            # heurística simples: componente verde bem mais alta que r/b
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
                # diferença L1 da cor em relação ao céu
                dist = abs(col[0] - sky_sample[0]) + abs(col[1] - sky_sample[1]) + abs(col[2] - sky_sample[2])
                if dist > 40:
                    diff_from_sky += 1
            if samples > 0:
                green_frac = green_count / samples
                diff_frac = diff_from_sky / samples
                # regras heurísticas para reconhecer uma faixa de chão
                if green_frac > 0.18 and diff_frac > 0.25:
                    return max(0, y - 2)
                if diff_frac > 0.35:
                    return max(0, y - 4)
    except Exception:
        # se houver qualquer erro na análise de pixels, devolve fallback
        pass
    return int(HEIGHT * 0.8)

def create_ground_surface(bg_surface, ground_y, height=56):
    
    #Cria uma superfície que será usada como faixa de chão (verde),
    try:
        w, h = bg_surface.get_size()
        sample_w = max(10, w // 40)
        sample_h = 8
        sx = max(0, (w // 2) - sample_w // 2)
        sy = max(0, min(h - sample_h, ground_y - sample_h // 2))

        # soma de componentes RGB das amostras
        r = g = b = cnt = 0
        for xx in range(sx, min(sx + sample_w, w)):
            for yy in range(sy, min(sy + sample_h, h)):
                cr, cg, cb, *_ = bg_surface.get_at((xx, yy))
                r += cr; g += cg; b += cb; cnt += 1
        if cnt == 0:
            color = (80, 170, 70)  # fallback verde
        else:
            # média simples e intensificar componente verde
            r //= cnt; g //= cnt; b //= cnt
            g = min(255, int(g * 1.4))
            r = int(r * 0.7)
            b = int(b * 0.7)
            color = (r, g, b)

        surf = pygame.Surface((w, height))
        surf.fill(color)
        return surf
    except Exception:
        # fallback simples caso algo falhe
        surf = pygame.Surface((WIDTH, height))
        surf.fill((80, 170, 70))
        return surf

def load_highscore():
    
    #Lê o highscore do ficheiro JSON. Se não existir, devolve 0.
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f).get("highscore", 0)
    except:
        return 0

def save_highscore(value):

    #Persiste o highscore no ficheiro JSON.
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({"highscore": value}, f)
    except Exception as e:
        print("Erro ao salvar highscore:", e)

# Fontes usadas para interface e HUD
TITLE_FONT = pygame.font.SysFont("Arial", 60, bold=True)
TITLE_FONT_MENU = pygame.font.SysFont("Comic Sans MS", 70, bold=True)
BTN_FONT = pygame.font.SysFont("Arial", 32)
HUD_FONT = pygame.font.SysFont("Arial", 30)

# Paleta para botões e destaque
PRIMARY = (40, 120, 220)
PRIMARY_HOVER = (30, 100, 200)
RED = (220, 50, 50)
RED_HOVER = (200, 30, 30)

# ========================= CLASSE DO JOGADOR =========================

class Gato:
    def __init__(self):
        # carrega os sprites (com fallback se não existirem)
        self.image_normal = load_image("gato.png", PLAYER_SIZE_NORMAL)
        self.image_shoot = load_image("gato_atirador.png", PLAYER_SIZE_SHOOT)

        # inicia com sprite normal
        self.image = self.image_normal
        # contador de frames para exibir sprite de disparo brevemente
        self.shoot_timer = 0

        # velocidade inicial do salto (ajustável)
        self.JUMP_VEL = 10

        # retângulo de colisão e posição inicial no ecrã
        self.rect = self.image.get_rect()
        self.X_POS = int(WIDTH * 0.08)
        self.Y_POS = GROUND_Y - self.rect.height
        self.rect.topleft = (self.X_POS, self.Y_POS)

        # variáveis de movimento vertical (suavidade com float)
        self.is_jumping = False
        self.jump_vel = self.JUMP_VEL
        self.y = float(self.Y_POS)

        # estado do power-up de disparo
        self.can_shoot = False
        self.shoot_timer_powerup = 0

    def activate_powerup(self, duration_seconds):
        #Ativa o power-up por duration_seconds segundos.
        self.can_shoot = True
        self.shoot_timer_powerup = int(duration_seconds * FPS)

#Atualiza o estado do jogador:
    def update(self, user_input):

        # decrementa tempo do power-up
        if self.can_shoot:
            self.shoot_timer_powerup -= 1
            if self.shoot_timer_powerup <= 0:
                self.can_shoot = False

        # decrementa animação de disparo (volta ao normal quando chegar a 0)
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
            if self.shoot_timer == 0:
                self.image = self.image_normal

        # iniciar salto se não estiver já a saltar
        if not self.is_jumping and (user_input[pygame.K_w] or user_input[pygame.K_SPACE]):
            self.is_jumping = True

        # física do salto: sobe enquanto jump_vel > 0, depois desce
        if self.is_jumping:
            self.y -= self.jump_vel * 2.5
            self.jump_vel -= 0.5

            # quando o salto termina, reseta valores para próxima vez
            if self.jump_vel < -self.JUMP_VEL:
                self.is_jumping = False
                self.jump_vel = self.JUMP_VEL
                self.y = float(self.Y_POS)

        # aplica posição vertical (convertendo para int para rect)
        self.rect.y = int(self.y)

        # movimento horizontal simples com A/D
        if user_input[pygame.K_d]:
            self.rect.x += 6
        if user_input[pygame.K_a]:
            self.rect.x -= 6

        # limites da janela
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width

#Troca o sprite para animação de disparo
    def shoot(self):
        self.image = self.image_shoot
        self.shoot_timer = 8

#Desenha o gato na tela
    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

# ========================= CLASSES DE PROJÉTEIS =========================

# Projétil do jogador (fireball).
class Projetil:
    
    SPEED = 28

    def __init__(self, x, y):
        self.image = load_image("fireball.png", FIREBALL_SIZE)
        self.rect = self.image.get_rect()
        # definir o ponto de nascimento a partir do lado direito do gato
        self.rect.midleft = (x, y)

    def update(self):
        #Move o projétil para a direita
        self.rect.x += self.SPEED

    def draw(self, screen):
        #Desenha o projétil
        screen.blit(self.image, self.rect)

# Projéteis disparados pelo Boss
class BossProjetil:

    def __init__(self, x, y, vx=-13, vy=0):
        self.image = load_image("egg.png", BOSS_BULLET_SIZE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # nasce no centro do boss (ou proximo)
        self.vx = vx
        self.vy = vy

    def update(self):
        #Aplica a velocidade ao rect para mover o projétil.
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, screen):
        #Desenha o projétil do boss.
        screen.blit(self.image, self.rect)

# ========================= OBSTÁCULOS (Tronco e Bird) =========================

# Tronco (obstáculo)
class Tronco:
    def __init__(self):
        # escolhe dimensão do tronco dentro dos limites
        width = random.randint(CACTUS_MIN_WIDTH, CACTUS_MAX_WIDTH)
        height = random.randint(CACTUS_MIN_HEIGHT, CACTUS_MAX_HEIGHT)

        # carrega textura base (pode ser fallback)
        base_img = load_image("tronco_textura.png")
        base_w, base_h = base_img.get_size()

        # cria superfície transparente para o tronco
        surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # escala a textura para a altura do tronco mantendo proporção
        if base_h > 0:
            scale = height / base_h
        else:
            scale = 1.0
        tile_w = max(1, int(base_w * scale))
        tile_h = max(1, int(base_h * scale))
        tile_img = pygame.transform.scale(base_img, (tile_w, tile_h))

        # tiling horizontal para preencher a largura
        x = 0
        while x < width:
            surf.blit(tile_img, (x, 0))
            x += tile_w

        # desenha borda e sombra para dar profundidade
        pygame.draw.rect(surf, (80, 50, 25), surf.get_rect(), 3)
        pygame.draw.rect(surf, (0, 0, 0, 40), (0, height - 6, width, 6))

        self.surf = surf
        self.rect = self.surf.get_rect()
        # posiciona o tronco à direita do ecrã, alinhado ao chão
        self.rect.topleft = (WIDTH + 50, GROUND_Y - height)

    def update(self, speed):
        #Move o tronco para a esquerda de acordo com a velocidade do jogo
        self.rect.x -= speed

    def draw(self, screen):
        #Desenha o tronco
        screen.blit(self.surf, (self.rect.x, self.rect.y))

# Passaro (obstáculo) 
class Bird:
    def __init__(self):
        self.image = load_image("passaro.png", (150, 100), flip_x=True)
        base_height = GROUND_Y - 140
        alt1 = base_height
        alt2 = base_height - 60
        height = random.choice([alt1, alt2])
        self.rect = self.image.get_rect()
        # nasce à direita e a uma altura variável
        self.rect.topleft = (WIDTH + 50, height)
        self.wave_offset = random.uniform(0, math.pi * 2)  # offset para a onda vertical

    def update(self, speed):
        #Move-se para a esquerda e faz um up/down suave."""
        self.rect.x -= speed
        self.rect.y += int(math.sin(pygame.time.get_ticks() * 0.005 + self.wave_offset) * 2.0)

    def draw(self, screen):
        #Desenha o pássaro
        screen.blit(self.image, self.rect)

# ========================= POWER-UP =========================

class PowerUp:
    def __init__(self):
        self.image = load_image("power.png", POWERUP_SIZE)
        self.rect = self.image.get_rect()
        # posição base de nascimento do powerup 
        self.base_x = WIDTH + 80
        self.base_y = GROUND_Y - 140
        self.rect.center = (self.base_x, self.base_y)

    def update(self, speed):
       
        #Move o powerup para a esquerda e aplica um efeito de flutuação vertical.
        self.base_x -= speed
        t = pygame.time.get_ticks() / 400.0
        float_offset = math.sin(t) * 12
        self.rect.centerx = int(self.base_x)
        self.rect.centery = int(self.base_y + float_offset)

    def draw(self, screen):
        """Desenha o powerup."""
        screen.blit(self.image, self.rect)

# ========================= BOSS (Inimigo especial) =========================

class Boss:
    
    def __init__(self):
        # carrega sprite principal (com flip horizontal para olhar para a esquerda)
        self.image_base = load_image("Boss.png", (320, 240), flip_x=True)
        self.rect = self.image_base.get_rect()

        # posição inicial 'permanente' do boss (onde regressa)
        self.start_x = WIDTH - 360
        self.start_y = int(HEIGHT * 0.28)
        self.rect.topleft = (self.start_x, self.start_y)

        # vida do boss e velocidade base
        self.hp = 170
        self.max_hp = 170
        self.base_speed_x = 4
        self.speed_x = self.base_speed_x

        # estado e temporizadores
        self.state = "normal"
        self.state_timer = 180

        # parâmetros para smash/dash/shoot
        self.smash_phase = "up"
        self.smash_speed_down = 12
        self.dash_direction = -1
        self.dash_speed = 26
        self.shoot_cooldown = 120
        self.shoot_burst = 0

        # hit timer para flash visual quando o boss é atingido
        self.hit_timer = 0

#  Calcula uma hitbox reduzida para colisões mais justas.
    def get_collision_rect(self):
        cr = self.rect.inflate(-BOSS_HITBOX_INSET[0], -BOSS_HITBOX_INSET[1])
        return cr.move(BOSS_HITBOX_OFFSET)

# Atualiza a lógica do boss consoante o estado atual.
    def update(self, player_rect):
        self.state_timer -= 1

        if self.hit_timer > 0:
            self.hit_timer -= 1

        # dispatch para métodos específicos do estado
        if self.state == "normal":
            if self.state_timer <= 0:
                self.choose_next_state()
            self.update_normal(player_rect)
        elif self.state == "smash":
            if self.state_timer <= 0:
                self.state = "returning"
            else:
                self.update_smash(player_rect)
        elif self.state == "dash":
            self.update_dash(player_rect)
        elif self.state == "shoot_pause":
            self.update_shoot_pause()
        elif self.state == "returning":
            self.update_returning()
        elif self.state == "recoil":
            self.update_recoil()

        # limites verticais para o boss (para não sair muito do ecrã)
        top_limit = int(HEIGHT * 0.12)
        bottom_limit = GROUND_Y + 40
        if self.rect.y < top_limit:
            self.rect.y = top_limit
        if self.rect.y > bottom_limit:
            self.rect.y = bottom_limit

# Decide o próximo estado do boss com base em probabilidades
    def choose_next_state(self):
       
        self.state_timer = random.randint(160, 240)
        choice = random.random()
        if choice < 0.35:
            self.state = "smash"
            self.smash_phase = "up"
            self.state_timer = max(self.state_timer, 140)
        elif choice < 0.7:
            self.state = "dash"
            self.dash_direction = -1 if self.rect.centerx > WIDTH // 2 else 1
            self.state_timer = max(self.state_timer, 80)
        else:
            self.state = "shoot_pause"
            self.shoot_cooldown = 40
            self.shoot_burst = 3

    def update_normal(self, player_rect):
        #Comportamento em estado normal: deslocação horizontal e ligeiro follow vertical
        self.rect.x += self.speed_x
        if self.rect.right >= WIDTH - 20 or self.rect.left <= 20:
            self.speed_x *= -1

        if self.rect.centery < player_rect.centery - 20:
            self.rect.y += 2
        elif self.rect.centery > player_rect.centery + 20:
            self.rect.y -= 2

    def update_smash(self, player_rect):
        #Sequência 'smash' (subir, alinhar, esperar, descer)
        if self.smash_phase == "up":
            self.rect.y -= 6
            if self.rect.y <= int(HEIGHT * 0.12):
                self.smash_phase = "align"

        elif self.smash_phase == "align":
            # aproxima-se do x do jogador
            if self.rect.centerx > player_rect.centerx + 80:
                self.rect.x -= 8
            elif self.rect.centerx < player_rect.centerx - 80:
                self.rect.x += 8
            else:
                self.smash_phase = "wait"
                self.smash_wait_timer = 20

        elif self.smash_phase == "wait":
            self.smash_wait_timer -= 1
            if self.smash_wait_timer <= 0:
                self.smash_phase = "down"

        elif self.smash_phase == "down":
            self.rect.y += self.smash_speed_down
            if self.rect.bottom >= GROUND_Y + 8:
                self.rect.bottom = GROUND_Y + 8
                self.state = "returning"
                self.smash_phase = None

    def update_dash(self, player_rect):
        #Movimento rápido (dash) horizontal do boss
        if self.dash_direction == 0:
            self.dash_direction = -1 if self.rect.centerx > player_rect.centerx else 1

        self.rect.x += self.dash_speed * self.dash_direction

        # se colidir com bordas, volta ao estado 'returning'
        if self.rect.right >= WIDTH - 10 or self.rect.left <= 10:
            self.state = "returning"

    def update_shoot_pause(self):
        #Estado onde o boss se prepara para atirar em rajadas
        self.shoot_cooldown -= 1
        if self.shoot_burst <= 0:
            self.state = "returning"

    def update_returning(self):
        #Move o boss de volta à posição inicial 
        dx = self.start_x - self.rect.x
        dy = self.start_y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist < 8:
            # perto o suficiente: reajusta e volta ao estado normal
            self.rect.topleft = (self.start_x, self.start_y)
            self.state = "normal"
            self.state_timer = random.randint(160, 240)
            self.speed_x = self.base_speed_x
            return
        step = 12
        if dist != 0:
            self.rect.x += int(step * dx / dist)
            self.rect.y += int(step * dy / dist)

    def update_recoil(self):
        #Quando é atingido durante smash/dash, recua e depois regressa
        dx = self.start_x - self.rect.x
        dy = self.start_y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist < 60:
            self.state = "returning"
            return
        step = 16
        if dist != 0:
            self.rect.x += int(step * dx / dist)
            self.rect.y += int(step * dy / dist)

    def should_shoot_now(self):
        #Decide se o boss deve disparar agora.
        if self.state == "shoot_pause":
            if self.shoot_cooldown <= 0 and self.shoot_burst > 0:
                self.shoot_cooldown = 40
                self.shoot_burst -= 1
                return True
        elif self.state == "normal":
            if random.randint(0, 420) == 0:
                return True
        elif self.state == "dash":
            if random.randint(0, 600) == 0:
                return True
        return False

    def take_hit(self, from_state=None):
        #Aplica dano ao boss e define efeito visual e possivel recoil."""
        self.hp -= 1
        self.hit_timer = 10
        if from_state in ("smash", "dash"):
            self.state = "recoil"

    def draw(self, screen):
       #Desenha o boss; se estiver no hit_timer, desenha um flash."""
        if self.hit_timer > 0:
            flash = self.image_base.copy()
            flash.fill((255, 255, 255, 120), None, pygame.BLEND_RGBA_ADD)
            screen.blit(flash, self.rect)
        else:
            screen.blit(self.image_base, self.rect)

# ========================= FUNÇÕES DE UI (BOTÕES, MENUS) =========================

# Desenha um botão com sombra, cor base e cor de hover.
def draw_button(surface, rect, text, base_color, hover_color, mouse_pos, selected=False, disabled=False):
    x, y, w, h = rect
    is_hover = pygame.Rect(rect).collidepoint(mouse_pos) or selected
    color = hover_color if is_hover and not disabled else base_color

    if disabled:
        color = (120, 120, 120)

    # sombra
    shadow_rect = pygame.Rect(x + 4, y + 4, w, h)
    pygame.draw.rect(surface, (40, 40, 40), shadow_rect)

    # botão
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=8)
    # destaque se selecionado
    if selected and not disabled:
        pygame.draw.rect(surface, (255, 255, 255), (x - 3, y - 3, w + 6, h + 6), 3, border_radius=10)

    label_color = BLACK if not disabled else (80, 80, 80)
    label = BTN_FONT.render(text, True, label_color)
    surface.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))

# ========================= TELAS: MORTE / NÍVEL CONCLUÍDO / VITÓRIA =========================

def death_screen(score, highscore):
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

# Distâncias necessárias para completar cada nível (5 = boss level = infinito)
LEVEL_DISTANCES = {
    1: 1000,
    2: 2000,
    3: 3000,
    4: 4200,
    5: float('inf'),
}

# Desenha uma barra de progresso no HUD para o nível atual.
def draw_progress_map(surface, score, level):
    total = LEVEL_DISTANCES.get(level, 1000)
    if math.isinf(total):
        # não desenhar se for boss level
        return

    progress = min(1.0, score / total)

    bar_w = int(WIDTH * 0.55)
    bar_h = 6
    bar_x = WIDTH // 2 - bar_w // 2
    bar_y = HEIGHT - 60

    # linha de fundo
    pygame.draw.line(surface, (200, 200, 200), (bar_x, bar_y), (bar_x + bar_w, bar_y), bar_h)

    # 'gato' marcador e pequenos indicadores visuais
    cat_w = 18
    cat_h = 18
    cat_x = bar_x - cat_w - 12
    cat_y = bar_y - cat_h // 2
    pygame.draw.rect(surface, (60, 60, 60), (cat_x, cat_y, cat_w, cat_h))
    pygame.draw.circle(surface, (0, 0, 0), (cat_x + 5, cat_y + 6), 2)
    pygame.draw.circle(surface, (0, 0, 0), (cat_x + 13, cat_y + 6), 2)

    # bandeira final
    flag_x = bar_x + bar_w + 12
    flag_y = bar_y - 20
    pole_h = 40
    pygame.draw.line(surface, (0, 0, 0), (flag_x, flag_y), (flag_x, flag_y + pole_h), 3)
    pygame.draw.polygon(surface, (0, 0, 0), [(flag_x, flag_y), (flag_x + 30, flag_y + 10), (flag_x, flag_y + 20)])

    # marcador atual (círculo e seta)
    marker_x = int(bar_x + progress * bar_w)
    marker_y = bar_y
    pygame.draw.circle(surface, (255, 200, 0), (marker_x, marker_y), 8)
    pygame.draw.polygon(surface, (255, 200, 0), [(marker_x, marker_y + 12), (marker_x - 6, marker_y + 5), (marker_x + 6, marker_y + 5)])

    remaining = max(0, int(total - score))
    meters_txt = f"{remaining}m"
    m_surf = HUD_FONT.render(meters_txt, True, BLACK)
    surface.blit(m_surf, (WIDTH // 2 - m_surf.get_width() // 2, bar_y + 12))

# Desenha a barra de HP do boss 
def draw_boss_hp(surface, boss):
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

# Tela mostrada quando um nível é concluído.
def level_complete_screen(level, score, highscore, has_next_level):
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

# Tela mostrada quando o jogador derrota o boss final (vitória).
def victory_screen(score, highscore):
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

# ========================= LOOP PRINCIPAL DO JOGO (main_game) =========================º

#Função principal que executa a lógica do jogo para um nível.
def main_game(start_level=1):

    global unlocked_levels
    global GROUND_Y

    run = True

    # carrega background (procura nas pastas)
    bg = load_image("game_bg.png", (WIDTH, HEIGHT))

    # detecta posição do chão: se MANUAL_GROUND_Y definido usa-o, caso contrário detecta a partir do bg
    if MANUAL_GROUND_Y is not None:
        detected_ground = int(MANUAL_GROUND_Y)
    else:
        detected_ground = detect_ground_y_from_bg(bg)
    GROUND_Y = max(0, detected_ground)

    # cria superfície verde do chão baseada na cor do background
    ground_height = 56
    ground_surface = create_ground_surface(bg, GROUND_Y, height=ground_height)

    # instancia o jogador e ajusta a sua posição base
    gato = Gato()
    gato.Y_POS = GROUND_Y - gato.rect.height
    gato.y = float(gato.Y_POS)
    gato.rect.topleft = (gato.X_POS, gato.Y_POS)

    # listas para entidades dinâmicas
    obstacles = []
    bullets = []
    powerups = []
    boss_bullets = []

    # variáveis de jogo
    score = 0
    speed = 12 + 2 * (start_level - 1)  # velocidade aumenta com o nível
    level = start_level

    boss = None
    boss_active = False
    paused = False

    highscore = load_highscore()
    font = HUD_FONT

    bg_x = 0
    bg_speed = 4

    # temporizadores de spawn/intervalos
    obstacle_spawn_interval = max(26, 64 - (level - 1) * 6)
    obstacle_spawn_timer = obstacle_spawn_interval
    max_obstacles_base = 5

    if level == 5:
        powerup_spawn_interval = 220
    else:
        powerup_spawn_interval = 480
    powerup_spawn_timer = 0

    level_distance = LEVEL_DISTANCES.get(level, 1000)

    # se é boss level (distância infinita), inicializa o boss no começo do nível
    if math.isinf(level_distance):
        boss = Boss()
        boss_active = True

    # LOOP PRINCIPAL DO NÍVEL
    while run:
        # dt em segundos 
        dt = clock.tick(FPS) / 1000.0
        mouse = pygame.mouse.get_pos()
        user_input = pygame.key.get_pressed()

        # ========== EVENTOS ==========
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # salva highscore antes de sair
                save_highscore(max(score, highscore))
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # tecla X: atirar (se tiver power-up) e não estiver em pausa
                if event.key == pygame.K_x and gato.can_shoot and not paused:
                    gato.shoot()
                    bullets.append(Projetil(gato.rect.right, gato.rect.centery))
                # tecla P: pausa
                if event.key == pygame.K_p:
                    paused = not paused

            # clique no botão "Voltar ao Menu" quando em pausa
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
            # desenha e espera nas rotinas de desenho de pausa
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
            continue  # pula o resto do loop enquanto pausado

        # ========== ATUALIZAÇÕES DO JOGADOR ==========
        gato.update(user_input)

        # verifica se completou o nível 
        if not math.isinf(level_distance) and score >= level_distance:
            # desbloqueia próximo nível se aplicável
            if level + 1 > unlocked_levels:
                unlocked_levels = level + 1
            save_highscore(max(score, highscore))

            has_next_level = (level < 5)
            escolha = level_complete_screen(level, score, max(score, highscore), has_next_level)

            if escolha == "next" and has_next_level:
                main_game(start_level=level + 1)
                return
            else:
                return

        # ========== LÓGICA DO BOSS (SE ATIVO) ==========
        if boss_active and boss:
            boss.update(gato.rect)

            # decide se o boss deve disparar agora
            if boss.should_shoot_now():
                on_ground = (boss.rect.bottom >= GROUND_Y - 2)
                offset_y = random.randint(-34, 34)
                bullet_y = boss.rect.centery + offset_y

                if on_ground:
                    vx = -13
                    vy = 0
                else:
                    # mira aproximada em direção ao gato com velocidade vertical limit
                    dy = (gato.rect.centery - boss.rect.centery)
                    vy = max(min(dy * 0.06, 8), -2)
                    vx = -10
                spawn_x = boss.rect.left - 20
                boss_bullets.append(BossProjetil(spawn_x, bullet_y, vx=vx, vy=vy))

            # se o boss ficou sem HP: vitória
            if boss.hp <= 0:
                unlocked_levels = max(unlocked_levels, 5)
                pygame.time.delay(400)  # pequena pausa para efeito
                save_highscore(max(score, highscore))
                victory_screen(score, max(score, highscore))
                return

            # colisão direta do jogador com a hitbox reduzida do boss = morte
            if gato.rect.colliderect(boss.get_collision_rect()):
                pygame.time.delay(300)
                save_highscore(max(score, highscore))
                death_screen(score, max(score, highscore))
                return

        # ========== ATUALIZAÇÃO E COLISÕES DE PROJÉTEIS DO JOGADOR ==========
        for bullet in bullets[:]:
            bullet.update()

            # verifica colisão entre projecto do jogador e projéteis do boss 
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

            # colisão com boss 
            if boss_active and boss and bullet.rect.colliderect(boss.get_collision_rect()):
                boss.take_hit(from_state=boss.state)
                if bullet in bullets:
                    bullets.remove(bullet)
                continue

            # colisão com obstáculos convencionais
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

            # remove projéteis que saíram muito para a direita
            if bullet.rect.x > WIDTH + 200 and bullet in bullets:
                bullets.remove(bullet)

        # ========== ATUALIZAÇÃO E COLISÕES DE PROJÉTEIS DO BOSS ==========
        for b_bullet in boss_bullets[:]:
            b_bullet.update()
            # colisão com jogador = morte imediata
            if b_bullet.rect.colliderect(gato.rect):
                pygame.time.delay(200)
                save_highscore(max(score, highscore))
                death_screen(score, max(score, highscore))
                return
            # remoção se sair do ecrã
            if b_bullet.rect.right < -50 or b_bullet.rect.top > HEIGHT + 200 or b_bullet.rect.bottom < -200:
                if b_bullet in boss_bullets:
                    boss_bullets.remove(b_bullet)

        # ========== SPAWN E MOVIMENTO DE OBSTÁCULOS (se não for boss active) ==========
        if not boss_active:
            obstacle_spawn_timer -= 1
            if obstacle_spawn_timer <= 0:
                max_obstacles = max_obstacles_base + level
                min_spacing = int(WIDTH * max(0.18, 0.35 - 0.03 * (level - 1)))
                rightmost = max((obs.rect.right for obs in obstacles), default=-9999)
                if len(obstacles) < max_obstacles and rightmost <= WIDTH - min_spacing:
                    # probabilidade de gerar bird em vez de tronco aumenta com nível
                    bird_prob = min(0.5, 0.12 + 0.06 * (level - 1))
                    if level >= 3:
                        bird_prob = min(0.45, bird_prob + 0.06)
                    if random.random() < bird_prob:
                        obstacles.append(Bird())
                    else:
                        obstacles.append(Tronco())

                # recalcula próximo intervalo de spawn com alguma aleatoriedade
                base_interval = max(22, 70 - level * 8)
                obstacle_spawn_interval = base_interval + random.randint(-8, 12)
                obstacle_spawn_interval = max(18, obstacle_spawn_interval - (score // 2000))
                obstacle_spawn_timer = obstacle_spawn_interval

            # atualiza cada obstáculo e checa colisões com o jogador
            for obstacle in obstacles[:]:
                obstacle.update(speed)

                if gato.rect.colliderect(obstacle.rect):
                    pygame.time.delay(300)
                    save_highscore(max(score, highscore))
                    death_screen(score, max(score, highscore))
                    return
                if obstacle.rect.x < -200 and obstacle in obstacles:
                    obstacles.remove(obstacle)

        # ========== SPAWN E ATUALIZAÇÃO DE POWERUPS ==========
        powerup_spawn_timer -= 1
        # garante apenas um powerup ativo ao mesmo tempo
        if powerup_spawn_timer <= 0 and len(powerups) == 0:
            if math.isinf(level_distance):
                chance = 1
            else:
                chance = 3
            if random.randint(0, chance) == 0:
                powerups.append(PowerUp())
            powerup_spawn_timer = powerup_spawn_interval

        # atualiza powerups e verifica coleta
        for p in powerups[:]:
            p.update(speed)
            if gato.rect.colliderect(p.rect):
                gato.activate_powerup(10)  # powerup dura 10s
                powerups.remove(p)
            elif p.rect.right < -100:
                powerups.remove(p)

        # ========== BACKGROUND E DESENHO ==========
        bg_x -= bg_speed
        if bg_x <= -WIDTH:
            bg_x = 0

        screen.fill(WHITE)
        # desenha background com scroll simples
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + WIDTH, 0))

        # desenha o chão em ambos painéis para parecer contínua
        screen.blit(ground_surface, (bg_x, GROUND_Y))
        screen.blit(ground_surface, (bg_x + WIDTH, GROUND_Y))

        # desenha entidades na ordem correta 
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

        # incrementa score com cada frame 
        score += 1

        # desenha HUD com score, nível, highscore
        score_text = font.render(f"Score: {score}", True, BLACK)
        level_text = font.render(f"Level: {level}", True, BLACK)
        high_text = font.render(f"High: {highscore}", True, BLACK)
        hud_x = WIDTH - 260
        screen.blit(score_text, (hud_x, 20))
        screen.blit(level_text, (hud_x, 55))
        screen.blit(high_text, (hud_x, 90))

        # indica tempo restante do powerup no HUD se ativo
        if gato.can_shoot:
            remaining = max(0, gato.shoot_timer_powerup // FPS)
            p_txt = font.render(f"Power-up: {remaining}s", True, (255, 100, 0))
            screen.blit(p_txt, (20, 20))

        # desenha barra de progresso (se aplicável)
        draw_progress_map(screen, score, level)

        # desenha barra de HP do boss se ativo
        if boss_active and boss:
            draw_boss_hp(screen, boss)

        # atualiza e mostra frame
        pygame.display.update()

# ========================= TELA DE CRÉDITOS =========================

def creditos():
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

        # clique do mouse no botão 'Voltar'
        if pygame.mouse.get_pressed()[0]:
            if pygame.Rect(back_rect).collidepoint(pygame.mouse.get_pos()):
                pygame.time.delay(120)
                return

        pygame.display.update()
        clock.tick(FPS)

# ========================= MENU E SELEÇÃO DE NÍVEL =========================

# Desenha um gradiente simples como fundo do menu.
def draw_menu_background(surface):
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = int(255 * (1 - t) + 80 * t)
        g = int(120 * (1 - t) + 0 * t)
        b = int(200 * (1 - t) + 120 * t)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))

# Tela para selecionar nível.
def level_select_menu():
    global unlocked_levels

    selected_idx = 0
    levels = [1, 2, 3, 4, 5]
    buttons = []
    btn_w, btn_h = int(WIDTH * 0.24), 60
    start_y = int(HEIGHT * 0.25)
    spacing = 15

    # cria retângulos para botões de cada nível
    for i, lvl in enumerate(levels):
        x = WIDTH // 2 - btn_w // 2
        y = start_y + i * (btn_h + spacing)
        buttons.append({
            "label": f"Level {lvl}",
            "rect": (x, y, btn_w, btn_h),
            "level": lvl
        })

    # botão voltar
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

                # navegação por teclado
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chosen = buttons[selected_idx]
                    lvl = chosen["level"]
                    if lvl <= unlocked_levels:
                        main_game(start_level=lvl)
                        return
                elif event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # clique com rato
                for i, b in enumerate(buttons):
                    if pygame.Rect(b["rect"]).collidepoint(event.pos):
                        lvl = b["level"]
                        if lvl <= unlocked_levels:
                            main_game(start_level=lvl)
                            return
                if pygame.Rect(back_rect).collidepoint(event.pos):
                    pygame.time.delay(120)
                    return

        # desenha interface
        screen.fill(WHITE)
        title = TITLE_FONT.render("Selecionar Nível", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.12)))

        for i, b in enumerate(buttons):
            lvl = b["level"]
            disabled = lvl > unlocked_levels  # bloqueado se maior que unlocked_levels
            label = b["label"] + (" (bloqueado)" if disabled else "")
            is_selected = (i == selected_idx)
            draw_button(screen, b["rect"], label, PRIMARY, PRIMARY_HOVER, mouse, selected=is_selected, disabled=disabled)

        draw_button(screen, back_rect, "Voltar", GRAY, (170, 170, 170), mouse)

        pygame.display.update()
        clock.tick(FPS)

# ========================= MENU PRINCIPAL =========================
def menu():
    selected_idx = 0
    mouse = (0, 0)

    buttons = [
        {"label": "Jogar", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3), 320, 64), "base": PRIMARY, "hover": PRIMARY_HOVER, "action": "play"},
        {"label": "Selecionar Nível", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3) + 80, 320, 64), "base": PRIMARY, "hover": PRIMARY_HOVER, "action": "level_select"},
        {"label": "Créditos/Comandos", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3) + 160, 320, 64), "base": GRAY, "hover": (170, 170, 200), "action": "credits"},
        {"label": "Sair", "rect": (WIDTH // 2 - 160, int(HEIGHT * 0.3) + 240, 320, 64), "base": RED, "hover": RED_HOVER, "action": "quit"},
    ]

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:

                # teclado: navegar e confirmar
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_idx = (selected_idx + 1) % len(buttons)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_idx = (selected_idx - 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = buttons[selected_idx]["action"]
                    if action == "play":
                        main_game(start_level=1)
                    elif action == "level_select":
                        level_select_menu()
                    elif action == "credits":
                        creditos()
                    elif action == "quit":
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                # clique do mouse nos botões
                for i, b in enumerate(buttons):
                    if pygame.Rect(b["rect"]).collidepoint(event.pos):
                        if b["action"] == "play":
                            main_game(start_level=1)
                        elif b["action"] == "level_select":
                            level_select_menu()
                        elif b["action"] == "credits":
                            creditos()
                        elif b["action"] == "quit":
                            pygame.quit()
                            sys.exit()

        # desenha fundo e títulos
        draw_menu_background(screen)

        title = TITLE_FONT_MENU.render("Super Cat Runner", True, (255, 240, 0))
        outline_color = (0, 0, 0)

        # desenha um pequeno contorno deslocado para criar efeito de outline
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            shadow = TITLE_FONT_MENU.render("Super Cat Runner", True, outline_color)
            screen.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + dx,
                                 int(HEIGHT * 0.12) + dy))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.12)))

        # desenha botões e destaques
        for i, b in enumerate(buttons):
            is_selected = (i == selected_idx)
            draw_button(screen, b["rect"], b["label"], b["base"], b["hover"], mouse, selected=is_selected)

        pygame.display.update()
        clock.tick(FPS)

# ========================= PONTO DE ENTRADA =========================

if __name__ == "__main__":
    # inicia o menu principal quando o ficheiro é executado diretamente
    menu()