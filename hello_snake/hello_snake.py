import pygame
import time
import random
import math

# 初始化pygame
pygame.init()

# 定义颜色
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# 定义屏幕大小
dis_width = 800
dis_height = 600

# 创建游戏窗口
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('贪吃蛇游戏')

# 定义时钟
clock = pygame.time.Clock()

# 定义蛇的大小和速度
snake_block = 20  # 增加大小
snake_speed = 10  # 初始速度
max_speed = 25    # 最大速度限制
speed_increase = 0.5  # 每吃一个食物增加的速度

# 定义网格大小（用于像素效果）
grid_size = snake_block

# 定义食物动画参数
food_surface = pygame.Surface((snake_block, snake_block), pygame.SRCALPHA)

# 创建像素风格的方块
def create_pixel_block(size, color, alpha=255):
    surface = pygame.Surface((size, size))
    surface.fill(color)
    
    # 添加像素风格的边框
    pygame.draw.line(surface, (255, 255, 255, alpha), (0, 0), (size-1, 0), 2)  # 顶部
    pygame.draw.line(surface, (255, 255, 255, alpha), (0, 0), (0, size-1), 2)  # 左侧
    pygame.draw.line(surface, (0, 0, 0, alpha), (size-1, 1), (size-1, size-1), 2)  # 右侧
    pygame.draw.line(surface, (0, 0, 0, alpha), (1, size-1), (size-1, size-1), 2)  # 底部
    
    return surface

# 定义颜色渐变
def get_gradient_color(index, length):
    start_color = pygame.Color('darkgreen')
    end_color = pygame.Color('lightgreen')
    factor = index / length if length > 0 else 0
    return start_color.lerp(end_color, factor)

# 修改字体设置
try:
    font_style = pygame.font.Font(r"C:\Windows\Fonts\simhei.ttf", 35)  # 增大字体
    score_font = pygame.font.Font(r"C:\Windows\Fonts\simhei.ttf", 45)  # 增大字体
except:
    font_style = pygame.font.SysFont(None, 35)
    score_font = pygame.font.SysFont(None, 45)

# 显示得分
def Your_score(score):
    value = score_font.render("你的得分: " + str(score), True, yellow)
    dis.blit(value, [10, 10])  # 稍微调整位置

# 绘制蛇
def our_snake(snake_block, snake_list):
    for i, x in enumerate(snake_list):
        color = get_gradient_color(i, len(snake_list))
        block = create_pixel_block(snake_block, color)
        dis.blit(block, [x[0], x[1]])

# 显示消息
def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width/2 - mesg.get_width()/2, dis_height/3])

# 绘制背景网格
def draw_grid():
    for x in range(0, dis_width, grid_size):
        pygame.draw.line(dis, (70, 70, 70), (x, 0), (x, dis_height), 1)
    for y in range(0, dis_height, grid_size):
        pygame.draw.line(dis, (70, 70, 70), (0, y), (dis_width, y), 1)

# 游戏结束画面
def game_over_screen(score):
    dis.fill(blue)
    draw_grid()  # 添加网格背景
    game_over_text = font_style.render("游戏结束!", True, red)
    score_text = font_style.render(f"最终得分: {score}", True, yellow)
    restart_text = font_style.render("按C重新开始 或 按Q退出", True, white)
    
    dis.blit(game_over_text, [dis_width/2 - game_over_text.get_width()/2, dis_height/3])
    dis.blit(score_text, [dis_width/2 - score_text.get_width()/2, dis_height/2])
    dis.blit(restart_text, [dis_width/2 - restart_text.get_width()/2, dis_height/1.5])
    pygame.display.update()

# 开始界面
def draw_start_screen():
    dis.fill(blue)
    draw_grid()  # 添加网格背景
    title = font_style.render("贪吃蛇游戏", True, yellow)
    start_text = font_style.render("按空格键开始游戏", True, white)
    help_text = font_style.render("使用方向键控制蛇的移动", True, white)
    speed_text = font_style.render("吃到食物会增加速度", True, white)
    
    dis.blit(title, [dis_width/2 - title.get_width()/2, dis_height/4])
    dis.blit(start_text, [dis_width/2 - start_text.get_width()/2, dis_height/2])
    dis.blit(help_text, [dis_width/2 - help_text.get_width()/2, dis_height/1.6])
    dis.blit(speed_text, [dis_width/2 - speed_text.get_width()/2, dis_height/1.4])
    pygame.display.update()

def gameLoop():
    game_over = False
    game_close = False
    game_started = False
    
    # 显示开始界面
    draw_start_screen()
    while not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_started = True
                elif event.key == pygame.K_q:
                    return

    x1 = dis_width / 2
    y1 = dis_height / 2
    current_speed = snake_speed  # 当前速度

    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1

    # 确保食物位置对齐网格
    foodx = round(random.randrange(0, dis_width - snake_block) / grid_size) * grid_size
    foody = round(random.randrange(0, dis_height - snake_block) / grid_size) * grid_size

    while not game_over:
        while game_close == True:
            game_over_screen(Length_of_snake - 1)
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change <= 0:
                    x1_change = -grid_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change >= 0:
                    x1_change = grid_size
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change <= 0:
                    y1_change = -grid_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change >= 0:
                    y1_change = grid_size
                    x1_change = 0

        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True
            
        # 更新蛇的位置
        x1 += x1_change
        y1 += y1_change
        
        dis.fill(blue)
        draw_grid()  # 添加网格背景
        
        # 绘制食物（带像素风格效果）
        food_alpha = abs(math.sin(time.time() * 3)) * 155 + 100
        food_block = create_pixel_block(snake_block, green, int(food_alpha))
        dis.blit(food_block, (foodx, foody))

        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        Your_score(Length_of_snake - 1)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / grid_size) * grid_size
            foody = round(random.randrange(0, dis_height - snake_block) / grid_size) * grid_size
            Length_of_snake += 1
            # 增加速度，但不超过最大速度
            current_speed = min(current_speed + speed_increase, max_speed)

        clock.tick(current_speed)

    pygame.quit()
    quit()

# 启动游戏
if __name__ == '__main__':
    gameLoop()
