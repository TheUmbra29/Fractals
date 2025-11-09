from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId
from ..entities.value_objects.ability_id import AbilityId

@dataclass(frozen=True)
class AbilityUsed:
    caster_id: EntityId
    ability_id: AbilityId
    target_id: EntityId = None