import pygame
import random

# Initialize Pygame
pygame.init()

# Set window dimensions
width, height = 300, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Game board
grid_rows = 20
grid_cols = 10
grid = [[0] * grid_cols for _ in range(grid_rows)]
block_size = 30
score = 0
score_increment = 100

# Tetromino shapes
tetromino_shapes = [
    [[1, 1, 1, 1]],  # I-shape

    [[1, 0, 0],
     [1, 1, 1]],  # J-shape

    [[0, 0, 1],
     [1, 1, 1]],  # L-shape

    [[1, 1],
     [1, 1]],  # O-shape

    [[0, 1, 1],
     [1, 1, 0]],  # S-shape

    [[0, 1, 0],
     [1, 1, 1]],  # T-shape

    [[1, 1, 0],
     [0, 1, 1]]  # Z-shape
]

tetromino_colors = [CYAN, BLUE, ORANGE, YELLOW, GREEN, MAGENTA, RED]

def new_tetromino():
    shape = random.choice(tetromino_shapes)
    color = tetromino_colors[tetromino_shapes.index(shape)]
    return {"shape": shape, "color": color, "row": 0, "col": grid_cols // 2 - len(shape[0]) // 2}

def draw_grid(surface, grid, block_size):
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col]:
                pygame.draw.rect(surface, tetromino_colors[grid[row][col]-1], (col * block_size, row * block_size, block_size, block_size))
            pygame.draw.rect(surface, GRAY, (col * block_size, row * block_size, block_size, block_size), 1)

def draw_tetromino(surface, tetromino, block_size):
    shape = tetromino["shape"]
    color = tetromino["color"]
    row = tetromino["row"]
    col = tetromino["col"]

    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c]:
                pygame.draw.rect(surface, color, ((col + c) * block_size, (row + r) * block_size, block_size, block_size))

# Initialize current tetromino
current_tetromino = new_tetromino()

def valid_move(grid, tetromino):
    shape = tetromino["shape"]
    row = tetromino["row"]
    col = tetromino["col"]

    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c]:
                new_row = row + r
                new_col = col + c
                if new_row >= grid_rows or new_col < 0 or new_col >= grid_cols or (new_row >= 0 and grid[new_row][new_col] != 0):
                    return False
    return True

def rotate_tetromino(tetromino):
    shape = tetromino["shape"]
    rotated_shape = [list(reversed(col)) for col in zip(*shape)]
    rotated_tetromino = {"shape": rotated_shape, "color": tetromino["color"], "row": tetromino["row"], "col": tetromino["col"]}
    return rotated_tetromino

def lock_tetromino(grid, tetromino):
    shape = tetromino["shape"]
    row = tetromino["row"]
    col = tetromino["col"]
    color_index = tetromino_colors.index(tetromino["color"]) + 1  # Get color index for grid

    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c]:
                grid[row + r][col + c] = color_index
    clear_rows(grid)

def clear_rows(grid):
    rows_to_clear = []
    for r in range(len(grid)):
        if all(grid[r]):
            rows_to_clear.append(r)

    for r in rows_to_clear:
        del grid[r]
        grid.insert(0, [0] * grid_cols)
        global score
        score += score_increment

# Game loop (placeholder for now)
running = True
while running:
    pygame.time.Clock().tick(30)  # Limit frames per second

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_tetromino["col"] -= 1
                if not valid_move(grid, current_tetromino):
                    current_tetromino["col"] += 1
            elif event.key == pygame.K_RIGHT:
                current_tetromino["col"] += 1
                if not valid_move(grid, current_tetromino):
                    current_tetromino["col"] -= 1
            elif event.key == pygame.K_DOWN:
                current_tetromino["row"] += 1
                if not valid_move(grid, current_tetromino):
                    current_tetromino["row"] -= 1
                    lock_tetromino(grid, current_tetromino)
                    current_tetromino = new_tetromino()
            elif event.key == pygame.K_UP:
                rotated_tetromino = rotate_tetromino(current_tetromino)
                if valid_move(grid, rotated_tetromino):
                    current_tetromino = rotated_tetromino

    # Fill the screen with black (for now)
    screen.fill(BLACK)

    # Draw the grid
    draw_grid(screen, grid, block_size)

    # Draw the current tetromino
    draw_tetromino(screen, current_tetromino, block_size)

    # Move tetromino down
    current_tetromino["row"] += 1
    if not valid_move(grid, current_tetromino):
        current_tetromino["row"] -= 1
        lock_tetromino(grid, current_tetromino)
        current_tetromino = new_tetromino()
        if not valid_move(grid, current_tetromino):  # Game Over check
            running = False

    # Display score
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

    # Update the display
    pygame.display.flip()

def valid_move(grid, tetromino):
    shape = tetromino["shape"]
    row = tetromino["row"]
    col = tetromino["col"]

    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c]:
                new_row = row + r
                new_col = col + c
                if new_row >= grid_rows or new_col < 0 or new_col >= grid_cols or (new_row >= 0 and grid[new_row][new_col] != 0):
                    return False
    return True

def rotate_tetromino(tetromino):
    shape = tetromino["shape"]
    rotated_shape = [list(reversed(col)) for col in zip(*shape)]
    rotated_tetromino = {"shape": rotated_shape, "color": tetromino["color"], "row": tetromino["row"], "col": tetromino["col"]}
    return rotated_tetromino

def lock_tetromino(grid, tetromino):
    shape = tetromino["shape"]
    row = tetromino["row"]
    col = tetromino["col"]
    color_index = tetromino_colors.index(tetromino["color"]) + 1  # Get color index for grid

    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c]:
                grid[row + r][col + c] = color_index
    clear_rows(grid)

def clear_rows(grid):
    rows_to_clear = []
    for r in range(len(grid)):
        if all(grid[r]):
            rows_to_clear.append(r)

    for r in rows_to_clear:
        del grid[r]
        grid.insert(0, [0] * grid_cols)
        global score
        score += score_increment


pygame.quit()
