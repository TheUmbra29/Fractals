from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetBattleStateQuery:
    """Query para obtener el estado completo de la batalla"""
    battle_id: UUID