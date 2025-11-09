from dataclasses import dataclass
from uuid import UUID
from ....domain.entities.value_objects.entity_id import EntityId

@dataclass
class GetEntityInfoQuery:
    """Query para obtener información de una entidad específica"""
    battle_id: UUID
    entity_id: EntityId