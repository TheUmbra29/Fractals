import pygame
from game.game import Game

def main():
    # ✅ INICIALIZAR CONTEXTO GLOBAL ANTES DE TODO
    from game.core.game_context import game_context
    game_context.initialize()
    
    print("🎮 Iniciando juego con arquitectura mejorada...")
    game = Game()
    game.run()

if __name__ == "__main__":
    main()