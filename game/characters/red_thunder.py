# game/characters/red_thunder.py (VERSIÓN CORREGIDA)
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
        """Listeners específicos para Red Thunder"""
        super().setup_energy_listeners()
        
        def on_storm_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'storm' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_storm_ability']['base']
                self.gain_energy(energy_gain, "storm_ability")
        
        from game.core.event_system import event_system, EventTypes
        event_system.register(EventTypes.ABILITY_USED, on_storm_ability)