from enum import Enum, auto

class Team(Enum):
    """Equipos del juego"""
    PLAYER = "player"
    ENEMY = "enemy"
    
    def __str__(self):
        return self.value

class GameState(Enum):
    """Estados del juego"""
    IDLE = auto()
    ENTITY_SELECTED = auto() 
    TRACING_ROUTE = auto()
    TARGETING_ABILITY = auto()
    AWAITING_CONFIRMATION = auto()

class CharacterClass(Enum):
    """Clases de personajes"""
    DAMAGE = "Daño"
    TACTICAL = "Táctico" 
    SUPPORT = "Apoyo"
    
    def __str__(self):
        return self.value

class ActionType(Enum):
    """Tipos de acciones"""
    MOVE = "move"
    BASIC_ATTACK = "basic_attack"
    ABILITY_ALPHA = "ability_alpha"
    ABILITY_BETA = "ability_beta" 
    ABILITY_ULTIMATE = "ability_ultimate"
    
    def __str__(self):
        return self.value