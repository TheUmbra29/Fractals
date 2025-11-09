from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId

@dataclass(frozen=True)
class EntityLeveledUp:
    entity_id: EntityId
    old_level: int
    new_level: int