from game.entities.battle_entity import BattleEntity
from game.characters.character_registry import CharacterRegistry

class RedThunder(BattleEntity):
    def __init__(self, position, team="player"):
        super().__init__(
            character_id="red_thunder",
            position=position, 
            team=team
        )
    
    def setup_energy_listeners(self):
        """Listeners SIMPLIFICADOS - sin tipos de daño"""
        super().setup_energy_listeners()