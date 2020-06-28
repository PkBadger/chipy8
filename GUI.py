import pygame
from chip8 import Chip8
import os

pygame.display.set_caption('Chip8')

WHITE = (255,255,255)
BLACK = (0,0,0)

class GUI:
    def __init__(self, file):
        self.height = 500
        self.width = 1000
        self.blockSize = self.height / 32 #15
        self.window = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.chip8 = Chip8()
        self.file = file

    def drawGraphics(self):
        for index, pixel in enumerate(self.chip8.gfx):
            if pixel == 1:
                x = ((index) % 64) * self.blockSize
                y = (index // 64) * self.blockSize
                square = pygame.draw.rect(self.window, WHITE, (x, y, self.blockSize, self.blockSize))
                #pygame.display.update(square)
        pygame.display.flip()

    def run(self):
        self.chip8.loadGame(self.file)
        run = True
        pause = False
        pygame.mixer.init()
        
        #self.window.fill(BLACK)
        # Remove later
        while run:
            keyIndex = {
                pygame.K_1: 0,
                pygame.K_2: 1,
                pygame.K_3: 2,
                pygame.K_4: 3,
                pygame.K_q: 4,
                pygame.K_w: 5,
                pygame.K_e: 6,
                pygame.K_r: 7,
                pygame.K_a: 8,
                pygame.K_s: 9,
                pygame.K_d: 10,
                pygame.K_f: 11,
                pygame.K_z: 12,
                pygame.K_x: 13,
                pygame.K_c: 14,
                pygame.K_v: 15,
            }

            self.clock.tick(500)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.KEYDOWN:
                    index = keyIndex.get(event.key, None)
                    if(self.chip8.paused): self.chip8.callback(index)
                    if(index): self.chip8.key[index] = 1
                if event.type == pygame.KEYUP:
                    index = keyIndex.get(event.key, None)
                    if(index): self.chip8.key[index] = 0                 
            #print(self.clock.get_fps())
            self.chip8.emulateCycle()
            if (self.chip8.drawFlag):
                self.window.fill(BLACK)
                self.drawGraphics()
                self.chip8.drawFlag = False

            if(self.chip8.soundFlag):
                pygame.mixer.music.load('buzzer.wav')
                pygame.mixer.music.play(0)
                self.chip8.soundFlag = False

            # Remove later

        pygame.quit()

#if __name__ == '__main__':
absolute_path = os.path.dirname(os.path.abspath(__file__))
game = GUI('c8games/TANK')

game.run()
