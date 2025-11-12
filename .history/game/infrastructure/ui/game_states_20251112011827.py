from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List
from core.domain.entities.value_objects.entity_id import EntityId
from core.domain.entities.value_objects.position import Position

class GameState(Enum):
    IDLE = auto()
    ENTITY_SELECTED = auto()
    TRACING_ROUTE = auto()
    TARGETING_ABILITY = auto()
    AWAITING_CONFIRMATION = auto()
    ABILITY_MENU = auto()

@dataclass
class GameContext:
    current_state: GameState = GameState.IDLE
    selected_entity_id: Optional[EntityId] = None
    current_route: Optional[List[Position]] = None
    dash_anchors: List[Position] = None
    current_destination: Optional[Position] = None
    pending_action: Optional[str] = None

    def __post_init__(self):
        if self.dash_anchors is None:
            self.dash_anchors = []

    def reset(self):
        self.current_state = GameState.IDLE
        self.selected_entity_id = None
        self.current_route = None
        self.dash_anchors.clear()
        self.current_destination = None
        self.pending_action = None

    def get_full_route_points(self) -> List[Position]:
        points = []
        if self.selected_entity_id and self.dash_anchors:
            pass
        return points

    def can_perform_action(self, action_type: str, entity) -> bool:
        return action_type not in entity.actions_used_this_turn