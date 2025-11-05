from game.characters.base_character import BaseCharacter
from game.characters.character_registry import CharacterRegistry
from .zoe_config import ZOE_ABILITIES, ZOE_STATS, ZOE_ENERGY_SOURCES, ZOE_ENERGY_MULTIPLIERS

class Zoe(BaseCharacter):
    def __init__(self, position, team="player"):
        super().__init__(
            name="Zoe",
            position=position,
            team=team,
            stats=ZOE_STATS.copy(),
            role="support",
            abilities_config=ZOE_ABILITIES
        )
    
    def setup_energy_sources(self):
        """Zoe genera más energía por habilidades de soporte"""
        return ZOE_ENERGY_SOURCES.copy()
    
    def setup_energy_multipliers(self):
        """Zoe bonus por habilidades de luz"""
        return ZOE_ENERGY_MULTIPLIERS.copy()
    
    def setup_energy_listeners(self):
        """Listeners de energía específicos para Zoe"""
        super().setup_energy_listeners()
        
        # Listener especial para habilidades de luz
        from game.core.event_system import event_system, EventTypes
        
        def on_light_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'light' and
                not data.get('is_ultimate', False)):
                print(f"✨ {self.name} usa habilidad de luz!")
        
        event_system.register(EventTypes.ABILITY_USED, on_light_ability)

CharacterRegistry.register("zoe", Zoe)