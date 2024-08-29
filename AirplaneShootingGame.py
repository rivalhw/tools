import pygame
import random
import time
import os

# 初始化 Pygame
pygame.init()

# 设置游戏窗口
width = 800
height = 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("太空大战")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 加载飞机图标，并将大小调整为60x60
player_image = pygame.image.load("player_fighter.png")
player_image = pygame.transform.scale(player_image, (60, 60))

enemy_image = pygame.image.load("enemy_fighter.png")
enemy_image = pygame.transform.scale(enemy_image, (60, 60))

# 玩家飞机
player = pygame.Rect(370, 500, 60, 60)
player_speed = 5

# 敌机列表和敌机子弹列表
enemies = []
enemy_bullets = []

# 子弹列表
bullets = []

# 积分
score = 0
font = pygame.font.SysFont(None, 36)  # 设置字体

# 游戏时间
game_time = 30  # 游戏时间为30秒
start_ticks = pygame.time.get_ticks()  # 游戏开始时间

# 历史最高分文件路径
high_scores_file = "high_scores.txt"

# 读取历史最高分记录
def load_high_scores():
    if os.path.exists(high_scores_file):
        with open(high_scores_file, "r") as file:
            scores = [int(line.strip()) for line in file.readlines()]
            return scores
    return []

# 保存历史最高分记录
def save_high_scores(scores):
    with open(high_scores_file, "w") as file:
        for score in scores:
            file.write(f"{score}\n")

# 更新历史最高分记录
def update_high_scores(new_score):
    scores = load_high_scores()
    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]  # 只保留前5名
    save_high_scores(scores)
    return scores

# 游戏主循环
running = True
clock = pygame.time.Clock()

while running:
    seconds = (pygame.time.get_ticks() - start_ticks) / 1000  # 计算已过去的时间
    time_left = max(0, game_time - int(seconds))  # 剩余时间

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.centerx - 3, player.top, 6, 15))  # 玩家子弹

    # 移动玩家飞机
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < width:
        player.x += player_speed

    # 生成敌机
    if random.randint(1, 60) == 1:
        enemies.append(pygame.Rect(random.randint(0, width-60), 0, 60, 60))

    # 敌机随机发射子弹
    for enemy in enemies:
        if random.randint(1, 100) == 1:
            enemy_bullets.append(pygame.Rect(enemy.centerx - 3, enemy.bottom, 6, 15))

    # 移动敌机
    for enemy in enemies[:]:
        enemy.y += 2
        if enemy.top > height:
            enemies.remove(enemy)

    # 移动敌机子弹
    for bullet in enemy_bullets[:]:
        bullet.y += 5
        if bullet.top > height:
            enemy_bullets.remove(bullet)

    # 移动玩家子弹
    for bullet in bullets[:]:
        bullet.y -= 7
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
                score += 10
                break

    # 检测玩家是否被敌机子弹击中
    for bullet in enemy_bullets[:]:
        if player.colliderect(bullet):
            running = False

    # 绘制游戏画面
    screen.fill(WHITE)
    screen.blit(player_image, player.topleft)
    for enemy in enemies:
        screen.blit(enemy_image, enemy.topleft)
    for bullet in bullets:
        pygame.draw.rect(screen, RED, bullet)
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, GREEN, bullet)  # 敌机子弹为绿色

    # 显示积分
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # 显示倒计时
    timer_text = font.render(f"Time Left: {time_left}", True, BLACK)
    screen.blit(timer_text, (width - 180, 10))

    pygame.display.flip()
    clock.tick(60)

    # 如果时间到或玩家被敌机碰到或被子弹击中，结束游戏
    if time_left == 0:
        running = False

# 游戏结束，更新和显示历史最高分记录
high_scores = update_high_scores(score)

screen.fill(WHITE)
game_over_text = font.render("Game Over: You were hit!", True, RED)
final_score_text = font.render(f"Final Score: {score}", True, BLACK)
high_scores_text = font.render("Top 5 Scores:", True, BLACK)

screen.blit(game_over_text, (width // 2 - 100, height // 2 - 100))
screen.blit(final_score_text, (width // 2 - 120, height // 2 - 50))
screen.blit(high_scores_text, (width // 2 - 120, height // 2))

for i, high_score in enumerate(high_scores):
    score_text = font.render(f"{i + 1}. {high_score}", True, BLACK)
    screen.blit(score_text, (width // 2 - 120, height // 2 + 30 + i * 30))

pygame.display.flip()
pygame.time.wait(10000)  # 显示5秒

pygame.quit()
