from enum import Enum, auto

class CombatActionType(Enum):
    MOVE = auto()
    ATTACK = auto()
    ABILITY = auto()
    DASH = auto()
    COVER = auto()
    INTERACT = auto()
