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
background_img = pygame.image.load('soil.jpg')
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
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
    x = random.randrange(0, WIDTH-10, CELL_SIZE)
    y = random.randrange(0, HEIGHT-10, CELL_SIZE)
    if [x, y] in snake_body:
        return random_food()
    return [x, y]


snake_pos = [100, 60]  # Initial position of the snake
snake_body = [[100, 60], [90, 60], [80, 60]]  # Initial body of the snake

food_pos = random_food()
food_spawned = True

direction = 'RIGHT'
change_to = direction

clock = pygame.time.Clock()
speed = 15

score = 0

font = pygame.font.SysFont('Arial', 24)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                change_to = 'UP'
            elif event.key == pygame.K_DOWN and direction != 'UP':
                change_to = 'DOWN'
            elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                change_to = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                change_to = 'RIGHT'
    direction = change_to

    if direction == 'UP':
        snake_pos[1] -= CELL_SIZE
    elif direction == 'DOWN':
        snake_pos[1] += CELL_SIZE
    elif direction == 'LEFT':
        snake_pos[0] -= CELL_SIZE
    elif direction == 'RIGHT':
        snake_pos[0] += CELL_SIZE
    
    snake_body.insert(0, list(snake_pos))

    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
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

    screen.blit(background_img, (0, 0))
    draw_snake(snake_body, direction)
    screen.blit(food_img, (food_pos[0], food_pos[1]))

    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, [10, 10])

    pygame.display.update()

    clock.tick(speed)