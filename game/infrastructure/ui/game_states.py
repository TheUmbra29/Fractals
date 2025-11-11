from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.value_objects.position import Position

class GameState(Enum):
    """Estados del juego según tu GDD"""
    IDLE = auto()                    # Nada seleccionado - esperando input
    ENTITY_SELECTED = auto()         # Entidad seleccionada, mostrando menú de acciones
    TRACING_ROUTE = auto()           # Modo trazado de ruta activo
    TARGETING_ABILITY = auto()       # Seleccionando objetivo para habilidad
    AWAITING_CONFIRMATION = auto()   # Esperando confirmación de acción

@dataclass
class GameContext:
    """Contexto actual del juego - estado compartido"""
    current_state: GameState = GameState.IDLE
    selected_entity_id: Optional[EntityId] = None
    current_route: Optional[List[Position]] = None
    marked_dash_targets: List[EntityId] = None
    pending_action: Optional[str] = None  # "move", "attack", "ability_alpha", etc.
    
    def __post_init__(self):
        if self.marked_dash_targets is None:
            self.marked_dash_targets = []
    
    def reset(self):
        """Resetea el contexto al estado inicial"""
        self.current_state = GameState.IDLE
        self.selected_entity_id = None
        self.current_route = None
        self.marked_dash_targets.clear()
        self.pending_action = None
    
    def can_perform_action(self, action_type: str, entity) -> bool:
        """Verifica si una acción puede realizarse según tu GDD"""
        return action_type not in entity.actions_used_this_turn