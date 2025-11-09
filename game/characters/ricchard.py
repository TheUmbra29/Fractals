# game/characters/ricchard.py (VERSIÓN SIMPLIFICADA)
from game.entities.battle_entity import BattleEntity
from game.characters.character_registry import CharacterRegistry

class Ricchard(BattleEntity):
    def __init__(self, position, team="player"):
        super().__init__(
            character_id="ricchard",  
            position=position,
            team=team
        )
    
    def setup_energy_listeners(self):
        """Listeners SIMPLIFICADOS - sin tipos de daño"""
        super().setup_energy_listeners()