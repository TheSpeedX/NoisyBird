import time

import pygame
import random
import sounddevice as sd
import numpy as np
import os

black = (0, 0, 0)
white = (255, 255, 255)
green = (34, 139, 34)
blue = (64, 224, 208)
pygame.init()

surfaceWidth = 800
surfaceHeight = 500
surface = pygame.display.set_mode((surfaceWidth, surfaceHeight))
pygame.display.set_caption('Noisy Bird')
clock = pygame.time.Clock()

img = pygame.image.load(os.path.join('images', 'bird.png'))
img_width = img.get_size()[0]
img_height = img.get_size()[1]

die_sound = pygame.mixer.Sound(os.path.join('sounds', 'die.mp3'))


def show_score(current_score):
    font = pygame.font.Font('freesansbold.ttf', 20)
    text = font.render(f'Score:{current_score}', True, white)
    surface.blit(text, [3, 3])


def blocks(x_block, y_block, block_width, block_height, gap):
    pygame.draw.rect(surface, green, [
                     x_block, y_block, block_width, block_height])
    pygame.draw.rect(surface, green, [
                     x_block, y_block + block_height + gap,
                     block_width, surfaceHeight])


def makeTextObjs(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()


def replay_or_quit():
    for event in pygame.event.get([pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT]):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            continue

        return event.key
    return None


def msg_surface(text):
    smallText = pygame.font.Font('freesansbold.ttf', 20)
    largeText = pygame.font.Font('freesansbold.ttf', 130)

    titletextSurf, titleTextRect = makeTextObjs(text, largeText)
    titleTextRect.center = surfaceWidth / 2, surfaceHeight / 2
    surface.blit(titletextSurf, titleTextRect)

    typtextSurf, typTextRect = makeTextObjs(
        'Press any key to continue', smallText)
    typTextRect.center = surfaceWidth / 2, ((surfaceHeight / 2) + 100)
    surface.blit(typtextSurf, typTextRect)

    pygame.display.update()
    time.sleep(1)

    while replay_or_quit() is None:
        clock.tick()

    main()


def gameOver():
    die_sound.play()
    msg_surface('Game over')


def bird(x, y, image):
    surface.blit(image, (x, y))


y = 200
max_volume = 0


def process_sound(indata, outdata, frames, time, status):
    global y, max_volume
    volume_norm = np.linalg.norm(indata)
    max_volume = max(max_volume, volume_norm)
    if volume_norm > 1:
        y -= 5
    else:
        y += 5
    print(max_volume)


def main():
    global y
    x = 150
    y = 200

    x_block = surfaceWidth
    y_block = 0

    block_width = 50
    block_height = random.randint(0, surfaceHeight / 2)
    gap = img_height * 5

    # speed of blocks
    block_move = 3

    score = 0
    game_over = False

    # Game Loop
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        surface.fill(blue)
        bird(x, y, img)
        show_score(score)

        blocks(x_block, y_block, block_width, block_height, gap)
        x_block -= block_move

        # boundaries
        if y > surfaceHeight - img_height or y < 0:
            gameOver()

        # blocks on screen or not
        if x_block < (-1 * block_width):
            x_block = surfaceWidth
            block_height = random.randint(0, surfaceHeight / 2)

        # Collision Detection

        if (
            x + img_width > x_block
            and x < x_block + block_width
            and (y < block_height or y + img_height > block_height + gap)
        ):
            gameOver()

        # detecting whether we are past the block or not in X
        if (
            x > x_block + block_width and
            x < x_block + block_width + img_width / 5
        ):
            score += 1

        pygame.display.update()
        clock.tick(80)


sd.Stream(callback=process_sound).start()
main()
pygame.quit()
exit()
