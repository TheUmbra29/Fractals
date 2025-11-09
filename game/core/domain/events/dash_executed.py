from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId

@dataclass(frozen=True)
class DashExecuted:
    dasher_id: EntityId
    target_id: EntityId
    damage: int