import pygame
import sounddevice as sd
import numpy as np

import time
import random
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


class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.image.load(os.path.join('images', 'bird.png'))
        self.img_width = self.img.get_size()[0]
        self.img_height = self.img.get_size()[1]
        self.jump = 5
        self.gravity = 5
        self.die_sound = pygame.mixer.Sound(os.path.join('sounds', 'die.mp3'))

    def draw(self):
        surface.blit(self.img, (self.x, self.y))

    def move_up(self):
        self.y -= self.jump

    def move_down(self):
        self.y += self.gravity

    def is_out_of_bounds(self):
        return (self.y > surfaceHeight - self.img_height or self.y < 0)


class ScoreCard:
    def __init__(self):
        self.position = [3, 3]
        self.highscorepos = [3, 20]
        self.score = 0
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.highscore = 0
        self.highscore_path = os.path.join('score', 'highscore.save')
        self.load_highscore()

    def load_highscore(self):
        # load high score upon initializing game
        try:
            with open(self.highscore_path, 'r+') as f:
                self.highscore = int(f.read())
        except Exception:
            self.highscore = 0

    def save_highscore(self):
        # saves highscore to path file
        with open(self.highscore_path, 'w') as f:
            f.write(str(self.highscore))

    def add_score(self, value):
        self.score += value

    def reset(self):
        self.score = 0

    def draw(self):
        # Shows Current and High scores
        text = self.font.render(f'Current Score: {self.score}', True, white)
        hstext = self.font.render(f'High Score: {self.highscore}', True, white)
        surface.blit(text, self.position)
        surface.blit(hstext, self.highscorepos)

    def update(self):
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()


class Block:
    def __init__(self, block_width, block_height, gap):
        self.x_block = surfaceWidth
        self.y_block = 0
        self.block_width = block_width
        self.block_height = block_height
        self.gap = gap
        self.passed = False

    def draw(self):
        pygame.draw.rect(
            surface, green,
            [
                self.x_block, self.y_block,
                self.block_width, self.block_height
            ]
        )
        pygame.draw.rect(
            surface, green,
            [
                self.x_block, self.y_block + self.block_height + self.gap,
                self.block_width, surfaceHeight
            ]
        )

    def move(self, x, y):
        self.passed = False
        self.x_block = x
        self.y_block = y

    def update(self, gap):
        self.gap = gap

    def check_passed(self, bird: Bird):
        self.passed = (
            bird.x > self.x_block + self.block_width and
            bird.x < self.x_block + self.block_width + bird.img_width / 5
        )
        return self.passed

    def check_collision(self, bird: Bird):
        return (
            (
                bird.y < self.block_height
                or bird.y + bird.img_height > self.block_height + self.gap
            )
            and bird.x + bird.img_width > self.x_block
            and bird.x < self.x_block + self.block_width
        )


class TextBlock:
    def __init__(self, text, size=20):
        self.font = pygame.font.Font('freesansbold.ttf', size)
        self.text = self.font.render(text, True, white)

    def center_text(self, x, y):
        self.text.get_rect().center = (x, y)

    def draw(self, position):
        surface.blit(self.text, position)


class NoisyBird:

    bird = Bird(150, 200)
    score_card = ScoreCard()
    block = Block(50, random.randint(0, surfaceHeight / 2), bird.img_height*5)

    def __init__(self):
        self.game_over = False

    @staticmethod
    def process_sound(indata, outdata, frames, time, status):
        volume_norm = np.linalg.norm(indata)
        if volume_norm > 1:
            NoisyBird.bird.move_up()
        else:
            NoisyBird.bird.move_down()

    @staticmethod
    def reset_game():
        NoisyBird.bird = Bird(150, 200)
        NoisyBird.score_card.reset()
        NoisyBird.block = Block(
            50,
            random.randint(0, surfaceHeight / 2),
            NoisyBird.bird.img_height*5
        )

    def replay_or_quit(self):
        for event in pygame.event.get(
            [pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT]
        ):
            if event.type == pygame.QUIT:
                exit()

            elif event.type == pygame.KEYDOWN:
                continue

            return event.key
        return None

    def game_show_screen(self, title, body):
        game_over_text = TextBlock(title, 70)
        game_over_rect = game_over_text.text.get_rect()
        game_over_rect.center = surfaceWidth / 2, surfaceHeight / 2 - 50
        continue_text = TextBlock(body, 20)
        continue_rect = continue_text.text.get_rect()
        continue_rect.center = surfaceWidth / 2, surfaceHeight / 2 + 50
        game_over_text.draw(game_over_rect)
        continue_text.draw(continue_rect)
        pygame.display.update()
        time.sleep(1)
        while self.replay_or_quit() is None:
            clock.tick()
        self.game_over = False
        self.play()

    def game_over_screen(self):
        self.game_show_screen('GAME OVER', 'Press any key to continue')

    def game_start_screen(self):
        surface.fill(blue)
        NoisyBird.bird = Bird(280, 100)
        NoisyBird.bird.draw()

        pygame.draw.rect(
            surface, green,
            [
                150, 320,
                50, 500
            ]
        )
        pygame.draw.rect(
            surface, green,
            [
                600, 0,
                50, 150
            ]
        )
        self.game_show_screen('NOISYBIRD', 'Press any key to start game')

    def gameOver(self):
        NoisyBird.bird.die_sound.play()
        self.game_over_screen()

    def play(self):
        NoisyBird.reset_game()
        print('Game Started')
        x_block = surfaceWidth
        y_block = 0

        block_width = 50

        # speed of blocks
        block_move = 3

        # Game Loop
        while not self.game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            surface.fill(blue)
            NoisyBird.bird.draw()
            NoisyBird.score_card.draw()

            NoisyBird.block.move(x_block, y_block)
            NoisyBird.block.draw()
            x_block -= block_move

            # boundaries
            if NoisyBird.bird.is_out_of_bounds():
                self.gameOver()

            # blocks on screen or not
            if x_block < (-1 * block_width):
                x_block = surfaceWidth
                NoisyBird.block.block_height = random.randint(
                    0, surfaceHeight / 2)

            # Collision Detection
            if NoisyBird.block.check_collision(NoisyBird.bird):
                self.gameOver()

            # detecting whether we are past the block or not in X
            if NoisyBird.block.check_passed(NoisyBird.bird):
                NoisyBird.score_card.add_score(1)

            pygame.display.update()
            NoisyBird.score_card.update()
            # NOTE: Higher the Tick, Faster the Game
            clock.tick(80)


def main():
    sd.Stream(callback=NoisyBird.process_sound).start()
    game = NoisyBird()
    game.game_start_screen()
    game.play()


if __name__ == '__main__':
    main()
