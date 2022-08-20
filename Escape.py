#Space Invaders

import pygame
import os
import random
import time
from pygame import mixer
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape from Calypsan")

#Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#Player Ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 15

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter >0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 20))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (1 - ((self.max_health - self.health)/self.max_health)), 20))

class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    music_list = ["Song1.wav", "Song2.wav", "Song3.wav", "Song4.wav", "Song5.wav", "Song6.wav", "Exit Calpysan.mp3"]
    music_main = random.choice(music_list)
    mixer.music.load(music_main)
    mixer.music.play(-1)
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("lucidasans", 50)
    main_font.set_underline(True)

    player_vel = 7
    laser_vel = 7
    player = Player(475, 850)

    lost = False
    lost_font = pygame.font.SysFont("lucidasans", 80)
    lost_count = 0
    win = False
    win_font = pygame.font.SysFont("lucidasans", 80)
    win_count = 0

    enemies = []
    wave_length = 5
    enemy_vel = 1.25

    clock = pygame.time.Clock()


    def redraw_window():
        WIN.blit(BG, (0,0))
        #Draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (168, 143, 143))
        level_label = main_font.render(f"Level: {level}", 1, (168, 143, 143))

        WIN.blit(lives_label, (20, 20))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 20, 20))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if win:
            win_label = win_font.render("You've see a ship ", 1, (114, 40, 127))
            WIN.blit(win_label, (WIDTH/2 - win_label.get_width()/2, 300))
            win_label1 = win_font.render("in the distance...", 1, (114, 40, 127))
            WIN.blit(win_label1, (WIDTH/2 - win_label1.get_width()/2, 400))
            win_label2 = win_font.render("An ally! You've done it!", 1, (114, 40, 127))
            WIN.blit(win_label2, (WIDTH / 2 - win_label2.get_width() / 2, 500))
            win_label3 = win_font.render("Calypsan is saved!", 1, (114, 40, 127))
            WIN.blit(win_label3, (WIDTH / 2 - win_label3.get_width() / 2, 600))

        if lost:
            lost_label = lost_font.render("You've lost...", 1, (102, 0, 0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))
            lost_label1 = lost_font.render("Calpysan will", 1, (102, 0, 0))
            WIN.blit(lost_label1, (WIDTH / 2 - lost_label1.get_width() / 2, 350))
            lost_label2 = lost_font.render("be destroyed", 1, (102, 0, 0))
            WIN.blit(lost_label2, (WIDTH / 2 - lost_label2.get_width() / 2, 450))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if level >= 10:
            win = True
            win_count += 1

        if win:
            if win_count > FPS * 6:
                run = False
            else:
                continue

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-2000, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # Left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() - 15 < WIDTH: # Right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # Up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 30 < HEIGHT: # Down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 15
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)



        player.move_lasers(-laser_vel, enemies)

def main_menu():
    mixer.music.load("Exit Calpysan.mp3")
    mixer.music.play(-1)
    title_font = pygame.font.SysFont("lucidasans", 60)
    instructions_font = pygame.font.SysFont("lucidasans", 35)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Your home planet, Calpysan, has", 1, (114, 40, 127))
        title_label1 = title_font.render("been taken over by a rebellion.", 1, (114, 40, 127))
        title_label2 = title_font.render("The king is dead. With most of", 1, (114, 40, 127))
        title_label3 = title_font.render("Calypsan's space vessels", 1, (114, 40, 127))
        title_label4 = title_font.render("destroyed, your fighter has", 1, (114, 40, 127))
        title_label5 = title_font.render("become the planet's only hope", 1, (114, 40, 127))
        title_label6 = title_font.render("of getting word of the attack", 1, (114, 40, 127))
        title_label7 = title_font.render("to Calypsan's allies...", 1, (114, 40, 127))
        title_label8 = title_font.render("Good luck, young star fighter", 1, (114, 40, 127))
        instructions = instructions_font.render("Click to begin. Use W A S D to move. Space to shoot.", 1, (114, 40, 127))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 0))
        WIN.blit(title_label1, (WIDTH / 2 - title_label1.get_width() / 2, 100))
        WIN.blit(title_label2, (WIDTH / 2 - title_label2.get_width() / 2, 200))
        WIN.blit(title_label3, (WIDTH / 2 - title_label3.get_width() / 2, 300))
        WIN.blit(title_label4, (WIDTH / 2 - title_label4.get_width() / 2, 400))
        WIN.blit(title_label5, (WIDTH / 2 - title_label5.get_width() / 2, 500))
        WIN.blit(title_label6, (WIDTH / 2 - title_label6.get_width() / 2, 600))
        WIN.blit(title_label7, (WIDTH / 2 - title_label7.get_width() / 2, 700))
        WIN.blit(title_label8, (WIDTH / 2 - title_label8.get_width() / 2, 800))
        WIN.blit(instructions, (WIDTH / 2 - instructions.get_width() / 2, 900))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = false
            if event.type == pygame.MOUSEBUTTONUP:
                main()
    pygame.quit()

main_menu()