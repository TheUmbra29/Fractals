from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId
from ..entities.value_objects.ability_id import AbilityId

@dataclass(frozen=True)
class AbilityUsed:
    """Evento cuando se usa una habilidad"""
    caster_id: EntityId
    ability_id: AbilityId
    target_id: EntityId = None
    damage_dealt: int = 0
    healing_done: int = 0