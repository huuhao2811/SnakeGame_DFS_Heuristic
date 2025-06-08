import pygame
import random
import sys
pygame.init()

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

head_img = pygame.image.load('snake.png')
body_img = pygame.image.load('rectangle.png')
apple_img = pygame.image.load('apple.png')
head_img = pygame.transform.scale(head_img, (25, 25))
food_img = pygame.transform.scale(apple_img, (22, 22))

WHITE = (255, 255, 255)
GREEN = (154, 205, 50)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
head_size = 25
offset = (20 - head_size) // 2

def draw_snake(snake_body, direction):
    for i, block in enumerate(snake_body):
        x, y = block
        if i == 0:
            if direction == 'UP':
                rotated_head = pygame.transform.rotate(head_img, 180)
            elif direction == 'DOWN':
                rotated_head = pygame.transform.rotate(head_img, 0)
            elif direction == 'LEFT':
                rotated_head = pygame.transform.rotate(head_img, 270)
            elif direction == 'RIGHT':
                rotated_head = pygame.transform.rotate(head_img, 90)
            screen.blit(rotated_head, (x + offset, y + offset))
        else:
            pygame.draw.rect(screen, GREEN, pygame.Rect(x, y, 17, 17))

def random_food():
    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)

        y = random.randrange(0, HEIGHT, CELL_SIZE)
        if [x, y] not in snake_body:
            return [x, y]

snake_pos = [100, 60]
snake_body = [[100, 60], [80, 60], [60, 60]]
food_pos = random_food()
food_spawned = True

direction = 'RIGHT'
change_to = direction

clock = pygame.time.Clock()
speed = 10

score = 0  # Điểm số trò chơi
font = pygame.font.SysFont('Arial', 24)

moves = [('UP', (0, -CELL_SIZE)), ('DOWN', (0, CELL_SIZE)),
         ('LEFT', (-CELL_SIZE, 0)), ('RIGHT', (CELL_SIZE, 0))]

opposite_directions = {
    'UP': 'DOWN',
    'DOWN': 'UP',
    'LEFT': 'RIGHT',
    'RIGHT': 'LEFT'
}

def is_safe(pos, snake_body):
    return (0 <= pos[0] < WIDTH and 0 <= pos[1] < HEIGHT and pos not in snake_body)

def get_sorted_moves(current, goal, last_move):
    dx = goal[0] - current[0]
    dy = goal[1] - current[1]
    move_priority = []
    if abs(dx) > abs(dy):
        if dx > 0:
            move_priority.append(('RIGHT', (CELL_SIZE, 0)))
        else:
            move_priority.append(('LEFT', (-CELL_SIZE, 0)))
        if dy > 0:
            move_priority.append(('DOWN', (0, CELL_SIZE)))
        else:
            move_priority.append(('UP', (0, -CELL_SIZE)))
    else:
        if dy > 0:
            move_priority.append(('DOWN', (0, CELL_SIZE)))
        else:
            move_priority.append(('UP', (0, -CELL_SIZE)))
        if dx > 0:
            move_priority.append(('RIGHT', (CELL_SIZE, 0)))
        else:
            move_priority.append(('LEFT', (-CELL_SIZE, 0)))
    for m in moves:
        if m not in move_priority:
            move_priority.append(m)
    move_priority = [m for m in move_priority if m[0] != opposite_directions.get(last_move)]
    return move_priority

def flood_fill_count(pos, snake_body, max_rows, max_cols):
    visited = set()
    stack = [tuple(pos)]
    count = 0
    min_x, max_x = pos[0], pos[0]
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        count += 1
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx * CELL_SIZE, y + dy * CELL_SIZE
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and [nx, ny] not in snake_body:
                if (nx, ny) not in visited:
                    stack.append((nx, ny))
    width = (max_x - min_x) // CELL_SIZE + 1
    return count, width

def simulate_path(snake_body, path, food_pos):
    simulated_body = snake_body.copy()
    pos = simulated_body[0][:]
    ate_food = False
    for move in path:
        if move == 'UP':
            pos[1] -= CELL_SIZE
        elif move == 'DOWN':
            pos[1] += CELL_SIZE
        elif move == 'LEFT':
            pos[0] -= CELL_SIZE
        elif move == 'RIGHT':
            pos[0] += CELL_SIZE
        if pos in simulated_body:
            return False, 0
        simulated_body.insert(0, pos[:])
        if pos == food_pos:
            ate_food = True
        else:
            simulated_body.pop()
    free_cells, width = flood_fill_count(pos, simulated_body, HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE)
    return ate_food and free_cells >= len(simulated_body) and width > 2, free_cells

def evaluate_move(new_pos, snake_body, current_pos, tail_pos):
    count, width = flood_fill_count(new_pos, snake_body, HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE)
    escape_score = 0
    if current_pos[0] == 0:  # Sát tường trái
        if new_pos[0] > current_pos[0]:  # Di chuyển sang phải
            escape_score += 100
        elif new_pos[1] > current_pos[1]:  # Di chuyển xuống dưới
            escape_score += 50
    tail_distance = abs(new_pos[0] - tail_pos[0]) + abs(new_pos[1] - tail_pos[1])
    tail_score = 1000 / (tail_distance + 1)
    width_score = width * 10
    return count + escape_score + tail_score + width_score

def dfs_recursive(current, goal, snake_body, visited, last_move):
    if current == goal:
        return []
    visited.add(tuple(current))
    for move, (dx, dy) in get_sorted_moves(current, goal, last_move):
        neighbor = [current[0] + dx, current[1] + dy]
        if tuple(neighbor) in visited or not is_safe(neighbor, snake_body):
            continue
        path = dfs_recursive(neighbor, goal, snake_body, visited, move)
        if path is not None:
            return [move] + path
    return None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    visited = set()
    path = dfs_recursive(snake_pos, food_pos, snake_body[1:], set(), direction)

    if path:
        is_safe_path, free_cells = simulate_path(snake_body, path, food_pos)
        if is_safe_path:
            change_to = path[0]
            direction = change_to
        else:
            print(f"Path leads to trap (free cells: {free_cells}), finding alternative")
            tail = snake_body[-1] if snake_body else snake_pos
            path_to_tail = dfs_recursive(snake_pos, tail, snake_body[1:], set(), direction)
            if path_to_tail and simulate_path(snake_body, path_to_tail, food_pos)[0]:
                change_to = path_to_tail[0]
                direction = change_to
            else:
                best_move = None
                best_move_score = -1  
                for move, (dx, dy) in moves:
                    new_pos = [snake_pos[0] + dx, snake_pos[1] + dy]
                    if is_safe(new_pos, snake_body):
                        move_score = evaluate_move(new_pos, snake_body, snake_pos, tail)  
                        if move_score > best_move_score:
                            best_move_score = move_score
                            best_move = move
                if best_move:
                    change_to = best_move
                    direction = change_to
                else:
                    print("No safe move found, game over")
                    pygame.quit()
                    sys.exit()
    else:
        print("No valid path found, using heuristic approach")
        tail = snake_body[-1] if snake_body else snake_pos
        path_to_tail = dfs_recursive(snake_pos, tail, snake_body[1:], set(), direction)
        if path_to_tail and simulate_path(snake_body, path_to_tail, food_pos)[0]:
            change_to = path_to_tail[0]
            direction = change_to
        else:
            best_move = None
            best_move_score = -1
            for move, (dx, dy) in moves:
                new_pos = [snake_pos[0] + dx, snake_pos[1] + dy]
                if is_safe(new_pos, snake_body):
                    move_score = evaluate_move(new_pos, snake_body, snake_pos, tail)
                    if move_score > best_move_score:
                        best_move_score = move_score
                        best_move = move
            if best_move:
                change_to = best_move
                direction = change_to
            else:
                print("No safe move found, game over")
                pygame.quit()
                sys.exit()

    if direction == 'UP':
        snake_pos[1] -= CELL_SIZE
    elif direction == 'DOWN':
        snake_pos[1] += CELL_SIZE
    elif direction == 'LEFT':
        snake_pos[0] -= CELL_SIZE
    elif direction == 'RIGHT':
        snake_pos[0] += CELL_SIZE

    snake_body.insert(0, list(snake_pos))

    if snake_pos == food_pos:
        score += 1  # Điểm số trò chơi chỉ tăng 1 khi ăn thức ăn
        food_spawned = False
    else:
        snake_body.pop()

    if not food_spawned:
        food_pos = random_food()
        food_spawned = True

    if (snake_pos[0] < 0 or snake_pos[0] >= WIDTH or
        snake_pos[1] < 0 or snake_pos[1] >= HEIGHT or
        snake_pos in snake_body[1:]):
        pygame.quit()
        sys.exit()

    screen.fill(BLACK)
    draw_snake(snake_body, direction)
    screen.blit(food_img, (food_pos[0], food_pos[1]))
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, [10, 10])
    pygame.display.update()
    clock.tick(speed)


