# Battle Repository Interface
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.aggregates.battle import Battle

class BattleRepository(ABC):
    """Interface para el repositorio de battles - AGREGADO RAIZ"""
    
    @abstractmethod
    def get_by_id(self, battle_id: UUID) -> Battle:
        pass
    
    @abstractmethod
    def save(self, battle: Battle) -> None:
        pass
    
    @abstractmethod
    def delete(self, battle_id: UUID) -> None:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Battle]:
        pass