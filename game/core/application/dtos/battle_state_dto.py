"""
DTO para estado de batalla
"""
from dataclasses import dataclass
from typing import Dict, List, Any
from uuid import UUID

@dataclass
class BattleStateDTO:
    """DTO para transferir estado de batalla a la UI"""
    battle_id: UUID
    mode: str
    turn_count: int
    current_turn: str
    actions_remaining: int
    wave_number: int
    is_completed: bool
    entities: List[Dict[str, Any]]