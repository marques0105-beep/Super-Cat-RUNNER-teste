import pygame
import random
import math
from configuracoes import *
from funcionalidades import load_image

class Gato:
    def __init__(self):
        self.image_normal = load_image("gato.png", PLAYER_SIZE_NORMAL)
        self.image_shoot = load_image("gato_atirador.png", PLAYER_SIZE_SHOOT)
        self.image = self.image_normal
        self.shoot_timer = 0
        self.JUMP_VEL = 10
        
        self.rect = self.image.get_rect()
        self.X_POS = int(WIDTH * 0.08)
        self.Y_POS = GROUND_Y - self.rect.height
        self.rect.topleft = (self.X_POS, self.Y_POS)
        
        self.is_jumping = False
        self.jump_vel = self.JUMP_VEL
        self.y = float(self.Y_POS)
        
        self.can_shoot = False
        self.shoot_timer_powerup = 0

    def activate_powerup(self, duration_seconds):
        self.can_shoot = True
        self.shoot_timer_powerup = int(duration_seconds * FPS)

    def update(self, user_input):
        if self.can_shoot:
            self.shoot_timer_powerup -= 1
            if self.shoot_timer_powerup <= 0:
                self.can_shoot = False

        if self.shoot_timer > 0:
            self.shoot_timer -= 1
            if self.shoot_timer == 0:
                self.image = self.image_normal

        if not self.is_jumping and (user_input[pygame.K_w] or user_input[pygame.K_SPACE]):
            self.is_jumping = True

        if self.is_jumping:
            self.y -= self.jump_vel * 2.5
            self.jump_vel -= 0.5

            if self.jump_vel < -self.JUMP_VEL:
                self.is_jumping = False
                self.jump_vel = self.JUMP_VEL
                self.y = float(self.Y_POS)

        self.rect.y = int(self.y)

        if user_input[pygame.K_d]:
            self.rect.x += 6
        if user_input[pygame.K_a]:
            self.rect.x -= 6

        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width

    def shoot(self):
        self.image = self.image_shoot
        self.shoot_timer = 8

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Projetil:
    SPEED = 28

    def __init__(self, x, y):
        self.image = load_image("fireball.png", FIREBALL_SIZE)
        self.rect = self.image.get_rect()
        self.rect.midleft = (x, y)

    def update(self):
        self.rect.x += self.SPEED

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class BossProjetil:
    def __init__(self, x, y, vx=-13, vy=0):
        self.image = load_image("egg.png", BOSS_BULLET_SIZE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = vx
        self.vy = vy

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# CORREÇÃO NO entidades.py

class Tronco:
    def __init__(self):
        width = random.randint(CACTUS_MIN_WIDTH, CACTUS_MAX_WIDTH)
        height = random.randint(CACTUS_MIN_HEIGHT, min(int(PLAYER_SIZE_NORMAL[1] * 1.05), int(HEIGHT * 0.33)))
        
        base_img = load_image("tronco_textura.png")
        base_w, base_h = base_img.get_size()
        
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if base_h > 0:
            scale = height / base_h
        else:
            scale = 1.0
        tile_w = max(1, int(base_w * scale))
        tile_h = max(1, int(base_h * scale))
        tile_img = pygame.transform.scale(base_img, (tile_w, tile_h))
        
        x = 0
        while x < width:
            surf.blit(tile_img, (x, 0))
            x += tile_w
        
        pygame.draw.rect(surf, (80, 50, 25), surf.get_rect(), 3)
        pygame.draw.rect(surf, (0, 0, 0, 40), (0, height - 6, width, 6))
        
        self.surf = surf
        self.rect = self.surf.get_rect()
        # CORREÇÃO: Alinha corretamente com o chão
        self.rect.bottom = GROUND_Y  # Mudei de topleft para bottom
        self.rect.left = WIDTH + 50

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        screen.blit(self.surf, (self.rect.x, self.rect.y))

class Bird:
    def __init__(self):
        self.image = load_image("passaro.png", (150, 100), flip_x=True)
        self.rect = self.image.get_rect()
        
        # CORREÇÃO: Pássaros mais altos
        base_height = GROUND_Y - 200  # Aumentei de 140 para 200
        alt1 = base_height
        alt2 = base_height - 80  # Aumentei de 60 para 80
        alt3 = base_height - 160  # Nova altura mais alta
        height = random.choice([alt1, alt2, alt3])
        
        self.rect.topleft = (WIDTH + 50, height)
        self.wave_offset = random.uniform(0, math.pi * 2)

    def update(self, speed):
        self.rect.x -= speed
        self.rect.y += int(math.sin(pygame.time.get_ticks() * 0.005 + self.wave_offset) * 2.0)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class PowerUp:
    def __init__(self):
        self.image = load_image("power.png", POWERUP_SIZE)
        self.rect = self.image.get_rect()
        self.base_x = WIDTH + 80
        self.base_y = GROUND_Y - 140
        self.rect.center = (self.base_x, self.base_y)

    def update(self, speed):
        self.base_x -= speed
        t = pygame.time.get_ticks() / 400.0
        float_offset = math.sin(t) * 12
        self.rect.centerx = int(self.base_x)
        self.rect.centery = int(self.base_y + float_offset)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Boss:
    def __init__(self):
        self.image_base = load_image("Boss.png", (320, 240), flip_x=True)
        self.rect = self.image_base.get_rect()
        
        self.start_x = WIDTH - 360
        self.start_y = int(HEIGHT * 0.28)
        self.rect.topleft = (self.start_x, self.start_y)
        
        self.hp = 170
        self.max_hp = 170
        self.base_speed_x = 4
        self.speed_x = self.base_speed_x
        
        self.state = "normal"
        self.state_timer = 180
        
        self.smash_phase = "up"
        self.smash_speed_down = 12
        self.dash_direction = -1
        self.dash_speed = 26
        self.shoot_cooldown = 120
        self.shoot_burst = 0
        
        self.hit_timer = 0

    def get_collision_rect(self):
        cr = self.rect.inflate(-BOSS_HITBOX_INSET[0], -BOSS_HITBOX_INSET[1])
        return cr.move(BOSS_HITBOX_OFFSET)

    def update(self, player_rect):
        self.state_timer -= 1
        
        if self.hit_timer > 0:
            self.hit_timer -= 1
            
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
            
        top_limit = int(HEIGHT * 0.12)
        bottom_limit = GROUND_Y + 40
        if self.rect.y < top_limit:
            self.rect.y = top_limit
        if self.rect.y > bottom_limit:
            self.rect.y = bottom_limit

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
        self.rect.x += self.speed_x
        if self.rect.right >= WIDTH - 20 or self.rect.left <= 20:
            self.speed_x *= -1
            
        if self.rect.centery < player_rect.centery - 20:
            self.rect.y += 2
        elif self.rect.centery > player_rect.centery + 20:
            self.rect.y -= 2

    def update_smash(self, player_rect):
        if self.smash_phase == "up":
            self.rect.y -= 6
            if self.rect.y <= int(HEIGHT * 0.12):
                self.smash_phase = "align"
                
        elif self.smash_phase == "align":
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
        if self.dash_direction == 0:
            self.dash_direction = -1 if self.rect.centerx > player_rect.centerx else 1
            
        self.rect.x += self.dash_speed * self.dash_direction
        
        if self.rect.right >= WIDTH - 10 or self.rect.left <= 10:
            self.state = "returning"

    def update_shoot_pause(self):
        self.shoot_cooldown -= 1
        if self.shoot_burst <= 0:
            self.state = "returning"

    def update_returning(self):
        dx = self.start_x - self.rect.x
        dy = self.start_y - self.rect.y
        dist = math.hypot(dx, dy)
        if dist < 8:
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
        self.hp -= 1
        self.hit_timer = 10
        if from_state in ("smash", "dash"):
            self.state = "recoil"

    def draw(self, screen):
        if self.hit_timer > 0:
            flash = self.image_base.copy()
            flash.fill((255, 255, 255, 120), None, pygame.BLEND_RGBA_ADD)
            screen.blit(flash, self.rect)
        else:
            screen.blit(self.image_base, self.rect)
