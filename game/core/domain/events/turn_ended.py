from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class TurnEnded:
    battle_id: UUID
    turn_count: int