# game/characters/zoe.py - VERSIÓN MIGRADA
from game.entities.battle_entity import BattleEntity
from game.characters.character_registry import CharacterRegistry
from .zoe_config import ZOE_ABILITIES, ZOE_STATS, ZOE_ENERGY_SOURCES, ZOE_ENERGY_MULTIPLIERS

class Zoe(BattleEntity):
    def __init__(self, position, team="player"):
        super().__init__(
            name="Zoe",
            position=position,
            team=team,
            stats=ZOE_STATS.copy(),
            character_class="support",
            abilities_config=ZOE_ABILITIES
        )
    
    def setup_energy_sources(self):
        return ZOE_ENERGY_SOURCES.copy()
    
    def setup_energy_multipliers(self):
        return ZOE_ENERGY_MULTIPLIERS.copy()
    
    def setup_energy_listeners(self):
        super().setup_energy_listeners()
        
        # Listener específico para habilidades de Luz
        def on_light_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'light' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_light_ability']['base']
                self.gain_energy(energy_gain, "light_ability")
        
        from game.core.event_system import event_system, EventTypes
        event_system.register(EventTypes.ABILITY_USED, on_light_ability)

CharacterRegistry.register("zoe", Zoe)