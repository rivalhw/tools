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
player_image = pygame.image.load("./images/player_fighter.png")
player_image = pygame.transform.scale(player_image, (60, 60))

enemy_image = pygame.image.load("./images/enemy_fighter.png")
enemy_image = pygame.transform.scale(enemy_image, (60, 60))

# 加载音效
shoot_sound = pygame.mixer.Sound("./sounds/shoot.wav")
explosion_sound = pygame.mixer.Sound("./sounds/explosion.wav")
collision_sound = pygame.mixer.Sound("./sounds/collision.wav")
missile_sound = pygame.mixer.Sound("./sounds/missile.mp3")

# 加载背景音乐
pygame.mixer.music.load("./sounds/background_music.mp3")
pygame.mixer.music.play(-1)  # 循环播放背景音乐

# 加载爆炸图像
explosion_image = pygame.image.load("./images/explosion.gif")
explosion_image = pygame.transform.scale(explosion_image, (60, 60))

# 玩家飞机
player = pygame.Rect(370, 500, 60, 60)
player_speed = 5

# 导弹数量
missile_count = 10
missiles = []

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

# 生命次数
lives = 3

# 星星
stars = [pygame.Rect(random.randint(0, width-2), random.randint(0, height-2), 2, 2) for _ in range(100)]

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

def reset_game():
    global player, missiles, enemies, enemy_bullets, bullets, missile_count, start_ticks
    player = pygame.Rect(370, 500, 60, 60)
    missiles = []
    enemies = []
    enemy_bullets = []
    bullets = []
    missile_count = 10
    start_ticks = pygame.time.get_ticks()

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
                # 玩家子弹发射两列
                bullets.append(pygame.Rect(player.left + 10, player.top, 6, 15))
                bullets.append(pygame.Rect(player.right - 16, player.top, 6, 15))
                shoot_sound.play()
            if event.key == pygame.K_m and missile_count > 0:
                missiles.append(pygame.Rect(player.centerx - 5, player.top, 10, 20))  # 玩家导弹
                missile_count -= 1
                missile_sound.play()

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

    # 移动玩家导弹
    for missile in missiles[:]:
        missile.y -= 10
        if missile.bottom < 0:
            missiles.remove(missile)

    # 检测碰撞
    collision_occurred = False
    for enemy in enemies[:]:
        if player.colliderect(enemy):
            collision_sound.play()
            enemies.remove(enemy)
            lives -= 1
            collision_occurred = True
            break
        for bullet in bullets[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 10
                explosion_sound.play()
                screen.blit(explosion_image, enemy.topleft)  # 在敌机位置显示爆炸图片
                pygame.display.update()
                break
        for missile in missiles[:]:
            if missile.colliderect(enemy):
                enemies.remove(enemy)
                missiles.remove(missile)
                score += 20
                explosion_sound.play()
                screen.blit(explosion_image, enemy.topleft)  # 在敌机位置显示爆炸图片
                pygame.display.update()
                break

    # 检测玩家是否被敌机子弹击中
    for bullet in enemy_bullets[:]:
        if player.colliderect(bullet):
            collision_sound.play()
            enemy_bullets.remove(bullet)
            lives -= 1
            collision_occurred = True

    # 如果发生碰撞，暂停3秒并倒计时
    if collision_occurred:
        for i in range(3, 0, -1):
            screen.fill(BLACK)
            countdown_text = font.render(f"Resuming in {i}", True, WHITE)
            screen.blit(countdown_text, (width // 2 - 60, height // 2))
            pygame.display.flip()
            time.sleep(1)
        reset_game()
        if lives <= 0:
            running = False

    # 绘制游戏画面
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.rect(screen, WHITE, star)
    screen.blit(player_image, player.topleft)
    for enemy in enemies:
        screen.blit(enemy_image, enemy.topleft)
    for bullet in bullets:
        pygame.draw.rect(screen, RED, bullet)
    for missile in missiles:
        pygame.draw.rect(screen, GREEN, missile)
    for bullet in enemy_bullets:
        pygame.draw.rect(screen, GREEN, bullet)  # 敌机子弹为绿色

    # 显示积分
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # 显示倒计时
    timer_text = font.render(f"Time Left: {time_left}", True, WHITE)
    screen.blit(timer_text, (width - 180, 10))

    # 显示导弹数量
    missile_text = font.render(f"Missiles: {missile_count}", True, WHITE)
    screen.blit(missile_text, (10, 40))

    # 显示剩余生命次数
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (width - 180, 40))

    pygame.display.flip()
    clock.tick(60)

    # 如果时间到或玩家生命用尽，结束游戏
    if time_left == 0 or lives <= 0:
        running = False

# 游戏结束，更新和显示历史最高分记录
high_scores = update_high_scores(score)

while True:
    screen.fill(BLACK)
    game_over_text = font.render("Game Over: You were hit!", True, RED)
    final_score_text = font.render(f"Final Score: {score}", True, WHITE)
    high_scores_text = font.render("Top 5 Scores:", True, WHITE)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)

    screen.blit(game_over_text, (width // 2 - 100, height // 2 - 100))
    screen.blit(final_score_text, (width // 2 - 120, height // 2 - 50))
    screen.blit(high_scores_text, (width // 2 - 120, height // 2))
    screen.blit(restart_text, (width // 2 - 200, height // 2 + 100))

    for i, high_score in enumerate(high_scores):
        score_text = font.render(f"{i + 1}. {high_score}", True, WHITE)
        screen.blit(score_text, (width // 2 - 120, height // 2 + 30 + i * 30))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                lives = 3
                score = 0
                reset_game()
            if event.key == pygame.K_q:
                pygame.quit()
                exit()
