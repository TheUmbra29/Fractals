from typing import List
from ...core.application.ports.event_publisher_port import EventPublisherPort
from ...core.domain.events.domain_event import DomainEvent

class DomainEventPublisher(EventPublisherPort):
    """Implementación simple de publicador de eventos"""
    
    def __init__(self):
        self._subscribers = []
    
    def publish(self, event: DomainEvent) -> None:
        """Publica un evento a todos los suscriptores"""
        for subscriber in self._subscribers:
            subscriber(event)
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """Publica múltiples eventos"""
        for event in events:
            self.publish(event)
    
    def subscribe(self, subscriber) -> None:
        """Suscribe un callback para recibir eventos"""
        self._subscribers.append(subscriber)