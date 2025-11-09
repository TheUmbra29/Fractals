from game.entities.battle_entity import BattleEntity
from game.characters.character_registry import CharacterRegistry

class Zoe(BattleEntity):
    def __init__(self, position, team="player"):
        super().__init__(
            character_id="zoe",
            position=position,
            team=team
        )
        self.character_id = "zoe"
    
    def setup_energy_listeners(self):
        """Listeners SIMPLIFICADOS - sin tipos de daño"""
        super().setup_energy_listeners()