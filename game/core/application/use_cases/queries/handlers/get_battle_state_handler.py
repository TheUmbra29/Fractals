from .....domain.repositories.battle_repository import BattleRepository
from ..get_battle_state_query import GetBattleStateQuery

class GetBattleStateHandler:
    """Manejador para obtener el estado de la batalla"""
    
    def __init__(self, battle_repository: BattleRepository):
        self.battle_repository = battle_repository
    
    def handle(self, query: GetBattleStateQuery):
        battle = self.battle_repository.get_by_id(query.battle_id)
        
        # Convertir el agregado Battle a un DTO simple para la UI
        return {
            "battle_id": str(battle.id),
            "mode": battle.mode,
            "turn": battle.turn_count,
            "current_turn": battle.current_turn,
            "actions_remaining": battle.actions_remaining,
            "wave_number": battle.wave_number,
            "is_completed": battle.is_completed,
            "entities": [
                {
                    "id": str(entity.id),
                    "name": entity.name,
                    "position": {"x": entity.position.x, "y": entity.position.y},
                    "stats": {
                        "current_hp": entity.stats.current_hp,
                        "max_hp": entity.stats.max_hp,
                        "current_ph": entity.stats.current_ph,
                        "max_ph": entity.stats.max_ph,
                        "attack": entity.stats.attack,
                        "defense": entity.stats.defense,
                        "speed": entity.stats.speed
                    },
                    "team": entity.team,
                    "class": entity.character_class,
                    "has_acted": entity.has_acted,
                    "has_moved": entity.has_moved
                }
                for entity in battle._entities.values()
            ]
        }