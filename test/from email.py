from pygame import *
import random
import sys

# Ініціалізація pygame
init()

# Константи
WIN_WIDTH = 1280
WIN_HEIGHT = 700
FPS = 60

# Кольори
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Game(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
    
class Player(Game):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_x_speed, player_y_speed):
        Game.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.x_speed = player_x_speed
        self.y_speed = player_y_speed
        self.on_ground = False
        self.gravity = 0.5
        self.jump_power = -12
        self.is_attacking = False
        self.attack_image = transform.scale(image.load("attack3.png"), (250, 160))
        self.original_image = self.image
        self.attack_cooldown = 0
        self.attack_range = 150
        self.facing_right = True
        self.score = 0

    def update(self):
        # Гравітація і рух
        self.y_speed += self.gravity
        self.rect.y += self.y_speed
        
        # Перевірка на землю
        if self.rect.y >= WIN_HEIGHT - self.rect.height:
            self.rect.y = WIN_HEIGHT - self.rect.height
            self.y_speed = 0
            self.on_ground = True
        
        # Рух по X
        self.rect.x += self.x_speed
        
        # Межі екрану
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > WIN_WIDTH - self.rect.width:
            self.rect.x = WIN_WIDTH - self.rect.width
        
        # Атака
        if self.is_attacking:
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                self.is_attacking = False
                self.image = self.original_image

    def jump(self):
        if self.on_ground:
            self.y_speed = self.jump_power
            self.on_ground = False
    
    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_cooldown = 15
            self.image = self.attack_image
            
            # Перевірка зіткнення з монстрами
            for monster in monsters:
                if self.check_attack_collision(monster):
                    monster.kill()
                    self.score += 1
    
    def check_attack_collision(self, monster):
        if self.facing_right:
            attack_rect = Rect(self.rect.right, self.rect.y, self.attack_range, self.rect.height)
        else:
            attack_rect = Rect(self.rect.left - self.attack_range, self.rect.y, self.attack_range, self.rect.height)
        
        return attack_rect.colliderect(monster.rect)

class Monster(Game):
    def __init__(self, image_path, x, y, width, height, speed):
        Game.__init__(self, image_path, x, y, width, height)
        self.speed = speed
    
    def update(self):
        self.rect.x -= self.speed
        
        # Якщо монстр дійшов до лівого краю
        if self.rect.right < 0:
            global game_over
            game_over = True
            self.kill()

# Створення вікна
window = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Dark Fantasy")

# Завантаження фону
try:
    back = transform.scale(image.load("dard.png"), (WIN_WIDTH, WIN_HEIGHT))
except:
    back = Surface((WIN_WIDTH, WIN_HEIGHT))
    back.fill(BLACK)

# Шрифт
font.init()
main_font = font.SysFont(None, 50)

# Групи спрайтів
monsters = sprite.Group()

# Головний герой
hero = Player("idle1.png", 50, WIN_HEIGHT - 160, 80, 160, 0, 0)

# Змінні гри
clock = time.Clock()
running = True
game_over = False
spawn_timer = 0

# Головний цикл гри
while running:
    # Обробка подій
    for e in event.get():
        if e.type == QUIT:
            running = False
        elif e.type == KEYDOWN:
            if e.key == K_LEFT:
                hero.x_speed = -8
                hero.facing_right = False
            elif e.key == K_RIGHT:
                hero.x_speed = 8
                hero.facing_right = True
            elif e.key == K_UP:
                hero.jump()
            elif e.key == K_SPACE:
                hero.attack()
        elif e.type == KEYUP:
            if e.key == K_LEFT and hero.x_speed < 0:
                hero.x_speed = 0
            elif e.key == K_RIGHT and hero.x_speed > 0:
                hero.x_speed = 0
    
    if not game_over:
        # Оновлення
        hero.update()
        monsters.update()
        
        # Спораун монстрів
        spawn_timer += 1
        if spawn_timer >= 120: # Кожні 2 секунди
            spawn_timer = 0
            new_monster = Monster(
                "monster.png", 
                WIN_WIDTH, 
                WIN_HEIGHT - 160, 
                80, 
                160, 
                random.randint(2, 5)
            )
            monsters.add(new_monster)
        
        # Відображення
        window.blit(back, (0, 0))
        hero.reset()
        monsters.draw(window)
        
        # Відображення рахунку
        score_text = main_font.render(f"Score: {hero.score}", True, WHITE)
        window.blit(score_text, (20, 20))
    else:
        # Екран завершення гри
        game_over_text = main_font.render("GAME OVER - Монстр дістався до людей!", True, RED)
        restart_text = main_font.render("Натисніть R для перезапуску", True, WHITE)
        window.blit(back, (0, 0))
        window.blit(game_over_text, (WIN_WIDTH//2 - game_over_text.get_width()//2, WIN_HEIGHT//2 - 50))
        window.blit(restart_text, (WIN_WIDTH//2 - restart_text.get_width()//2, WIN_HEIGHT//2 + 50))
        
        # Перезапуск гри
        keys = key.get_pressed()
        if keys[K_r]:
            game_over = False
            hero.score = 0
            monsters.empty()
            hero.rect.x = 50
            hero.rect.y = WIN_HEIGHT - 160
    
    display.update()
    clock.tick(FPS)

quit()