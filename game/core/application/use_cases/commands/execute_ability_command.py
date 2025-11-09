from dataclasses import dataclass
from uuid import UUID
from ....domain.entities.value_objects.entity_id import EntityId
from ....domain.entities.value_objects.ability_id import AbilityId
from ....domain.entities.value_objects.position import Position

@dataclass
class ExecuteAbilityCommand:
    """Comando para ejecutar una habilidad"""
    battle_id: UUID
    caster_id: EntityId
    ability_id: AbilityId
    target_id: EntityId = None
    target_position: Position = None