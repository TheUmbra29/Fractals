import pygame
from game.scenes.battle_scene import BattleScene

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Fractals - Estrategia por Turnos")
        self.clock = pygame.time.Clock()
        self.scene = BattleScene(self.screen)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.scene.handle_event(event)
            
            self.scene.update()
            self.scene.draw()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()