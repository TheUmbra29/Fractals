from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass(frozen=True)
class EntityId:
    """Value Object simple para IDs"""
    value: UUID
    
    @classmethod
    def generate(cls) -> 'EntityId':
        return EntityId(uuid4())
    
    def __str__(self) -> str:
        return str(self.value)