from dataclasses import dataclass
from uuid import UUID
from ....domain.entities.value_objects.entity_id import EntityId
from ....domain.entities.value_objects.position import Position

@dataclass
class MoveEntityCommand:
    """Comando para mover una entidad con posible embestida"""
    battle_id: UUID
    entity_id: EntityId
    target_position: Position
    dash_targets: list = None  # Lista de enemigos a embestir

    def __post_init__(self):
        if self.dash_targets is None:
            self.dash_targets = []