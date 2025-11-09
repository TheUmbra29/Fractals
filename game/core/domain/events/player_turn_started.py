from dataclasses import dataclass
from uuid import UUID
from .domain_event import DomainEvent

@dataclass(frozen=True)
class PlayerTurnStarted(DomainEvent):
    """Evento de dominio cuando comienza el turno del jugador"""
    battle_id: UUID
    turn_count: int