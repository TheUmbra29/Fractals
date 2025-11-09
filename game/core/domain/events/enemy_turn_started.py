from dataclasses import dataclass
from uuid import UUID
from .domain_event import DomainEvent

@dataclass(frozen=True)
class EnemyTurnStarted(DomainEvent):
    """Evento de dominio cuando comienza el turno del enemigo"""
    battle_id: UUID
    turn_count: int