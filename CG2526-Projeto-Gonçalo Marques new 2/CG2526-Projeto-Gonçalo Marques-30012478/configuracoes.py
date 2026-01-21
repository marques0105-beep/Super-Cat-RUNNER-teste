import pygame
import os
import json

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
PROGRESS_FILE = "progress.json"  # NOVO: ficheiro de progresso

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

def load_unlocked_levels():
    """Carrega os níveis desbloqueados do ficheiro."""
    global unlocked_levels
    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            unlocked_levels = data.get("unlocked_levels", 1)
            print(f"Níveis desbloqueados carregados: {unlocked_levels}")
    except:
        unlocked_levels = 1
        save_unlocked_levels()

def save_unlocked_levels():
    """Salva os níveis desbloqueados no ficheiro."""
    global unlocked_levels
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"unlocked_levels": unlocked_levels}, f)
        print(f"Níveis desbloqueados salvos: {unlocked_levels}")
    except Exception as e:
        print("Erro ao salvar progresso:", e)

# Carrega os níveis desbloqueados ao iniciar
load_unlocked_levels()

