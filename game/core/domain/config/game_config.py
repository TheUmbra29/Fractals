from dataclasses import dataclass, field
from typing import Tuple, Dict, Any

@dataclass(frozen=True)
class GameConfig:
    """Configuración centralizada del juego - INMUTABLE"""
    
    # Grid y movimiento
    GRID_SIZE: Tuple[int, int] = (8, 8)
    MAX_MOVEMENT_RANGE: int = 999
    ACTIONS_PER_TURN: int = 3
    
    # Equipos
    PLAYER_TEAM: str = "player"
    ENEMY_TEAM: str = "enemy"
    
    # Daños y balance
    BASE_DASH_DAMAGE: int = 15
    BASE_ATTACK_DAMAGE: int = 25
    PH_RECOVERY_RATE: float = 0.2
    
    # Posiciones iniciales
    INITIAL_OBSTACLES: Tuple[Tuple[int, int], ...] = (
        (3, 3), (4, 4), (2, 5)
    )
    
    # Stats base por clase - ✅ CORREGIDO: usar default_factory
    CLASS_STATS: Dict[str, Dict[str, int]] = field(
        default_factory=lambda: {
            "Daño": {
                "max_hp": 100, "max_ph": 50, "attack": 25, "defense": 15, "speed": 10
            },
            "Táctico": {
                "max_hp": 80, "max_ph": 60, "attack": 20, "defense": 12, "speed": 12
            },
            "Apoyo": {
                "max_hp": 90, "max_ph": 70, "attack": 15, "defense": 18, "speed": 8
            }
        }
    )

# Instancia global única
GAME_CONFIG = GameConfig()