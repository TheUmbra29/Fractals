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
        """Listeners específicos para Zoe"""
        super().setup_energy_listeners()
        
        def on_light_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'light' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_light_ability']['base']
                self.gain_energy(energy_gain, "light_ability")
        
        from game.core.event_system import event_system, EventTypes
        event_system.register(EventTypes.ABILITY_USED, on_light_ability)