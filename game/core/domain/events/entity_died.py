from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId

@dataclass(frozen=True)
class EntityDied:
    entity_id: EntityId