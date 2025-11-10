from typing import Dict, List, Optional
from uuid import UUID
from core.domain.repositories.battle_repository import BattleRepository
from core.domain.entities.aggregates.battle import Battle

class InMemoryBattleRepository(BattleRepository):
    """Repositorio en memoria para battles - CON IMPORTS CORREGIDOS"""
    
    def __init__(self):
        self._battles: Dict[UUID, Battle] = {}
    
    def get_by_id(self, battle_id: UUID) -> Battle:
        battle = self._battles.get(battle_id)
        if not battle:
            raise ValueError(f"Battle {battle_id} no encontrada")
        return battle
    
    def save(self, battle: Battle) -> None:
        self._battles[battle.id] = battle
    
    def delete(self, battle_id: UUID) -> None:
        if battle_id in self._battles:
            del self._battles[battle_id]
    
    def get_all(self) -> List[Battle]:
        return list(self._battles.values())