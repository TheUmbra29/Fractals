"""
COMPOSITION ROOT - Con la ruta CORRECTA
"""
import sys
import os

# Configurar path para imports absolutos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# IMPORTS CORRECTOS segÃºn tu estructura REAL
from infrastructure.ui.game_loop import GameLoop
from infrastructure.persistence.repositories.in_memory_battle_repository import InMemoryBattleRepository
from core.domain.services.turn_service import TurnService

def main():
    """Solo ensambla y inicia"""
    print("ðŸŽ® FRACTALS - Composition Root")
    print("ðŸ—ï¸  Rutas Corregidas")
    
    # Ensamblar dependencias
    battle_repo = InMemoryBattleRepository()
    turn_service = TurnService(battle_repo)
    game_loop = GameLoop(battle_repo, turn_service)
    
    # Iniciar
    game_loop.run()

if __name__ == "__main__":
    main()