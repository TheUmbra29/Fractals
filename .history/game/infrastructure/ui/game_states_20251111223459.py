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
    ABILITY_MENU = auto()            # Menú de habilidades activo

@dataclass
class GameContext:
    """Contexto actual del juego - estado compartido"""
    current_state: GameState = GameState.IDLE
    selected_entity_id: Optional[EntityId] = None
    current_route: Optional[List[Position]] = None
    dash_anchors: List[Position] = None  # ✅ NUEVO: Puntos de anclaje para embestidas
    current_destination: Optional[Position] = None  # ✅ NUEVO: Destino actual del cursor
    pending_action: Optional[str] = None  # "move", "attack", "ability_alpha", etc.

    def __post_init__(self):
        if self.dash_anchors is None:
            self.dash_anchors = []

    def reset(self):
        """Resetea el contexto al estado inicial"""
        self.current_state = GameState.IDLE
        self.selected_entity_id = None
        self.current_route = None
        self.dash_anchors.clear()
        self.current_destination = None
        self.pending_action = None

    def get_full_route_points(self) -> List[Position]:
        """Obtiene todos los puntos de la ruta completa: inicio + anclajes + destino"""
        points = []
        if self.selected_entity_id and self.dash_anchors:
            # Esto se calculará dinámicamente en el GameLoop
            pass
        return points

    def can_perform_action(self, action_type: str, entity) -> bool:
        """Verifica si una acción puede realizarse según tu GDD"""
        return action_type not in entity.actions_used_this_turn