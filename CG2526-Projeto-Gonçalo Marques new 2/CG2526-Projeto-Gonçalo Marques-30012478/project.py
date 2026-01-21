# project.py - Ponto de entrada principal
from project_2 import *

# Este ficheiro mantém compatibilidade com a estrutura original
# Apenas importa e executa o jogo a partir do módulo reorganizado
if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Super Cat Runner")
    menu(screen)