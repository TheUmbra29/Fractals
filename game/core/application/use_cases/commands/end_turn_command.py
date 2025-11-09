from dataclasses import dataclass
from uuid import UUID

@dataclass
class EndTurnCommand:
    """Comando para terminar el turno actual"""
    battle_id: UUID