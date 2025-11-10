from abc import ABC, abstractmethod
from typing import List
from ...domain.events.domain_event import DomainEvent

class EventPublisherPort(ABC):
    """Puerto para publicar eventos de dominio"""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publica un evento de dominio"""
        pass
    
    @abstractmethod
    def publish_all(self, events: List[DomainEvent]) -> None:
        """Publica múltiples eventos de dominio"""
        pass