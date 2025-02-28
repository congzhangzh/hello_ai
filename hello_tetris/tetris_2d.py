import pygame
import random
import numpy
import math

# 游戏常量
SCREEN_WIDTH = 400  # 增加宽度以容纳预览区域
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
FPS = 30
INITIAL_DROP_INTERVAL = 0.5  # 初始下落间隔时间（秒）
COLORS = {
    'background': (15, 56, 15),
    'grid': (48, 98, 48),
    'I': (15, 155, 215),
    'O': (227, 159, 2),
    'T': (175, 41, 138),
    'S': (89, 177, 1),
    'Z': (215, 15, 55),
    'J': (33, 65, 198),
    'L': (227, 91, 2)
}

# 方块形状
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]]
}

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Retro Tetris')
        self.clock = pygame.time.Clock()
        self.grid = [[0] * (SCREEN_WIDTH // BLOCK_SIZE) 
                    for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False
        self.last_drop_time = pygame.time.get_ticks()
        self.drop_interval = INITIAL_DROP_INTERVAL * 1000  # 转换为毫秒

    def new_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        return {
            'shape': shape,
            'rotation': 0,
            'x': SCREEN_WIDTH // BLOCK_SIZE // 2 - 1,
            'y': 0,
            'color': COLORS[shape]
        }

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, val,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE, BLOCK_SIZE))

    def draw_piece(self, piece):
        shape = SHAPES[piece['shape']]
        for y, row in enumerate(shape):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, piece['color'],
                                   ((piece['x'] + x) * BLOCK_SIZE,
                                    (piece['y'] + y) * BLOCK_SIZE,
                                    BLOCK_SIZE, BLOCK_SIZE))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if self.move_piece(-1):
                        self.play_sound('move')
                elif event.key == pygame.K_RIGHT:
                    if self.move_piece(1):
                        self.play_sound('move')
                elif event.key == pygame.K_DOWN:
                    if self.move_piece(0, 1):
                        self.play_sound('move')
                elif event.key == pygame.K_UP:
                    if self.rotate_piece():
                        self.play_sound('rotate')
                elif event.key == pygame.K_SPACE:
                    self.hard_drop()
                    self.play_sound('drop')

    def move_piece(self, dx=0, dy=0):
        new_x = self.current_piece['x'] + dx
        new_y = self.current_piece['y'] + dy
        if not self.check_collision(new_x, new_y):
            self.current_piece['x'] = new_x
            self.current_piece['y'] = new_y
            return True
        return False

    def rotate_piece(self):
        shape = SHAPES[self.current_piece['shape']]
        rotated = list(zip(*shape[::-1]))
        if not self.check_collision(self.current_piece['x'], 
                                  self.current_piece['y'], rotated):
            SHAPES[self.current_piece['shape']] = rotated

    def hard_drop(self):
        while self.move_piece(0, 1):
            pass

    def check_collision(self, x, y, shape=None):
        shape = shape or SHAPES[self.current_piece['shape']]
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    grid_x = x + col_idx
                    grid_y = y + row_idx
                    if (grid_x < 0 or grid_x >= len(self.grid[0]) or
                        grid_y >= len(self.grid) or
                        (grid_y >= 0 and self.grid[grid_y][grid_x])):
                        return True
        return False

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time > self.drop_interval:
            if not self.move_piece(0, 1):
                self.lock_piece()
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
                if self.check_collision(self.current_piece['x'],
                                      self.current_piece['y']):
                    self.game_over = True
            self.last_drop_time = current_time

    def lock_piece(self):
        shape = SHAPES[self.current_piece['shape']]
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = self.current_piece['x'] + x
                    grid_y = self.current_piece['y'] + y
                    self.grid[grid_y][grid_x] = self.current_piece['color']

    def clear_lines(self):
        lines_cleared = 0
        for y in range(len(self.grid)):
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0] * (SCREEN_WIDTH // BLOCK_SIZE))
                lines_cleared += 1
        self.score += lines_cleared * 100

    def render(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid_lines()
        self.draw_grid()
        self.draw_piece(self.current_piece)
        self.draw_next_piece()
        self.draw_score()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def draw_grid_lines(self):
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(self.screen, COLORS['grid'],
                            (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(self.screen, COLORS['grid'],
                            (0, y), (SCREEN_WIDTH, y), 1)

    def draw_next_piece(self):
        # 游戏区域和预览区域布局
        game_width = 300
        preview_x = game_width + 20
        preview_width = 100
        
        # 绘制"Next"标签
        font = pygame.font.SysFont('8bitoperator', 18)
        label = font.render('Next:', True, (255, 255, 255))
        self.screen.blit(label, (preview_x, 10))
        
        # 绘制预览方块
        shape = SHAPES[self.next_piece['shape']]
        preview_block_size = BLOCK_SIZE // 2
        start_x = preview_x + (preview_width - len(shape[0]) * preview_block_size) // 2
        start_y = 40
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece['color'],
                                   (start_x + x * preview_block_size,
                                    start_y + y * preview_block_size,
                                    preview_block_size, preview_block_size))
        
        # 绘制当前方块
        current_label = font.render('Current:', True, (255, 255, 255))
        self.screen.blit(current_label, (preview_x, 150))
        
        current_shape = SHAPES[self.current_piece['shape']]
        current_start_x = preview_x + (preview_width - len(current_shape[0]) * preview_block_size) // 2
        current_start_y = 180
        
        for y, row in enumerate(current_shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_piece['color'],
                                   (current_start_x + x * preview_block_size,
                                    current_start_y + y * preview_block_size,
                                    preview_block_size, preview_block_size))

    def draw_game_over(self):
        font = pygame.font.SysFont('8bitoperator', 36)
        text = font.render('GAME OVER', True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        self.screen.blit(text, text_rect)

    def play_sound(self, sound):
        if hasattr(self, 'sounds'):
            self.sounds[sound].play()

    def generate_sound(self, frequency, duration):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        # 创建二维数组，支持立体声
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        max_sample = 2**(16 - 1) - 1
        
        for s in range(n_samples):
            t = float(s) / sample_rate
            sample = int(max_sample * math.sin(2 * math.pi * frequency * t))
            # 将相同的样本写入左右声道
            buf[s][0] = sample
            buf[s][1] = sample
        
        sound = pygame.sndarray.make_sound(buf)
        sound.set_volume(0.1)
        return sound

    def load_sounds(self):
        self.sounds = {
            'move': self.generate_sound(440, 0.1),
            'rotate': self.generate_sound(523.25, 0.1),
            'drop': self.generate_sound(659.25, 0.2),
            'clear': self.generate_sound(784, 0.3),
            'gameover': self.generate_sound(220, 1.0)
        }

    def draw_score(self):
        font = pygame.font.SysFont('8bitoperator', 24)
        text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def run(self):
        pygame.mixer.init()
        self.load_sounds()
        while True:
            while not self.game_over:
                self.clock.tick(FPS)
                self.handle_events()
                self.update()
                self.render()
            
            # 显示游戏结束画面
            self.draw_game_over()
            pygame.display.flip()
            
            # 等待用户按键
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    # 按任意键重新开始
                    self.__init__()
                    break

if __name__ == '__main__':
    game = Tetris()
    game.run()
