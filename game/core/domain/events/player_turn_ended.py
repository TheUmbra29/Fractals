from dataclasses import dataclass
from uuid import UUID
from .domain_event import DomainEvent

@dataclass(frozen=True)
class PlayerTurnEnded(DomainEvent):
    """Evento de dominio cuando termina el turno del jugador"""
    battle_id: UUID
    turn_count: int