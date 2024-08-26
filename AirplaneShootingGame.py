import pygame
import random

# 初始化 Pygame
pygame.init()

# 设置游戏窗口
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("打飞机游戏")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 玩家飞机
player = pygame.Rect(400, 500, 50, 50)
player_speed = 5

# 敌机列表
enemies = []

# 子弹列表
bullets = []

# 游戏主循环
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.centerx - 2, player.top, 4, 10))

    # 移动玩家飞机
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < width:
        player.x += player_speed

    # 生成敌机
    if random.randint(1, 60) == 1:
        enemies.append(pygame.Rect(random.randint(0, width-50), 0, 50, 50))

    # 移动敌机
    for enemy in enemies[:]:
        enemy.y += 2
        if enemy.top > height:
            enemies.remove(enemy)

    # 移动子弹
    for bullet in bullets[:]:
        bullet.y -= 5
        if bullet.bottom < 0:
            bullets.remove(bullet)

    # 检测碰撞
    for enemy in enemies[:]:
        if player.colliderect(enemy):
            running = False
        for bullet in bullets[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                break

    # 绘制游戏画面
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, BLUE, player)
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, bullet)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
