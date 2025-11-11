from dataclasses import dataclass
from ..entities.value_objects.entity_id import EntityId

@dataclass(frozen=True)
class EntityHealed:
    """Evento cuando una entidad es curada"""
    entity_id: EntityId
    heal_amount: int
    healer_id: EntityId = None