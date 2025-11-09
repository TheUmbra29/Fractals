from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass(frozen=True)
class AbilityId:
    """Value Object para identificadores de habilidades"""
    value: UUID
    
    @classmethod
    def generate(cls) -> 'AbilityId':
        return AbilityId(uuid4())
    
    def __str__(self) -> str:
        return str(self.value)