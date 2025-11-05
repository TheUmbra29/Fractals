# game/characters/red_thunder.py - VERSIÓN MIGRADA
from game.entities.battle_entity import BattleEntity
from game.characters.character_registry import CharacterRegistry
from .red_thunder_config import RED_THUNDER_ABILITIES, RED_THUNDER_STATS, RED_THUNDER_ENERGY_SOURCES, RED_THUNDER_ENERGY_MULTIPLIERS

class RedThunder(BattleEntity):
    def __init__(self, position, team="player"):
        super().__init__(
            name="Red Thunder",
            position=position,
            team=team,
            stats=RED_THUNDER_STATS.copy(),
            character_class="tank",
            abilities_config=RED_THUNDER_ABILITIES
        )
    
    def setup_energy_sources(self):
        return RED_THUNDER_ENERGY_SOURCES.copy()
    
    def setup_energy_multipliers(self):
        return RED_THUNDER_ENERGY_MULTIPLIERS.copy()
    
    def setup_energy_listeners(self):
        super().setup_energy_listeners()
        
        # Listener específico para habilidades de Tormenta
        def on_storm_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'storm' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_storm_ability']['base']
                self.gain_energy(energy_gain, "storm_ability")
        
        from game.core.event_system import event_system, EventTypes
        event_system.register(EventTypes.ABILITY_USED, on_storm_ability)

CharacterRegistry.register("red_thunder", RedThunder)