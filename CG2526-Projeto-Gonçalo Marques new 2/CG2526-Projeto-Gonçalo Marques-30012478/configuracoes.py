# config.py
import pygame
import os

# Inicializa o pygame
pygame.init()

# Obtém as dimensões do monitor atual para inicializar fullscreen
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Cores usadas no jogo (tuplas RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (220, 50, 50)
RED_HOVER = (200, 30, 30)
PRIMARY = (40, 120, 220)
PRIMARY_HOVER = (30, 100, 200)

# Frames por segundo alvo
FPS = 60

# Diretórios de assets
ASSET_DIR = "."
IMAGES_DIR = os.path.join(ASSET_DIR, "Imagens_usadas")

# Ficheiro onde o highscore será guardado
HIGHSCORE_FILE = "highscore.json"

# Permite forçar uma posição do chão manualmente (None = detecção automática)
MANUAL_GROUND_Y = 780

# Tamanhos (pixels) usados para sprites principais
PLAYER_SIZE_NORMAL = (140, 140)
PLAYER_SIZE_SHOOT = (150, 150)
FIREBALL_SIZE = (64, 64)
BOSS_BULLET_SIZE = (98, 98)
POWERUP_SIZE = (110, 110)

# Ajustes da hitbox do Boss
BOSS_HITBOX_INSET = (140, 120)
BOSS_HITBOX_OFFSET = (-28, 0)

# Parâmetros para troncos (obstáculos)
CACTUS_SCALE_MIN = 0.75
CACTUS_SCALE_MAX = 1.25
CACTUS_MIN_WIDTH = 60
CACTUS_MAX_WIDTH = 160
CACTUS_MIN_HEIGHT = 60

# Distâncias necessárias para completar cada nível (5 = boss level = infinito)
LEVEL_DISTANCES = {
    1: 1000,
    2: 2000,
    3: 3000,
    4: 4200,
    5: float('inf'),
}

# Fontes usadas para interface e HUD
TITLE_FONT = pygame.font.SysFont("Arial", 60, bold=True)
TITLE_FONT_MENU = pygame.font.SysFont("Comic Sans MS", 70, bold=True)
BTN_FONT = pygame.font.SysFont("Arial", 32)
HUD_FONT = pygame.font.SysFont("Arial", 30)

# Variáveis globais que serão atualizadas
unlocked_levels = 1
GROUND_Y = int(HEIGHT * 0.8)