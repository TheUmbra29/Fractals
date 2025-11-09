from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId

@dataclass(frozen=True)
class EntityDamaged:
    entity_id: EntityId
    old_hp: int
    new_hp: int
    damage_amount: int