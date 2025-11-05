from game.characters.base_character import BaseCharacter
from game.characters.character_registry import CharacterRegistry
from .red_thunder_config import RED_THUNDER_ABILITIES, RED_THUNDER_STATS, RED_THUNDER_ENERGY_SOURCES, RED_THUNDER_ENERGY_MULTIPLIERS

class RedThunder(BaseCharacter):
    def __init__(self, position, team="player"):
        super().__init__(
            name="Red Thunder",
            position=position,
            team=team,
            stats=RED_THUNDER_STATS.copy(),
            role="speed",
            abilities_config=RED_THUNDER_ABILITIES
        )
    
    def setup_energy_sources(self):
        """Red Thunder genera más energía por golpear y por turno"""
        return RED_THUNDER_ENERGY_SOURCES.copy()
    
    def setup_energy_multipliers(self):
        """Red Thunder bonus por daño físico y de tormenta"""
        return RED_THUNDER_ENERGY_MULTIPLIERS.copy()
    
    def setup_energy_listeners(self):
        """Listeners de energía específicos para Red Thunder"""
        super().setup_energy_listeners()
        
        # Listener especial para habilidades de tormenta
        from game.core.event_system import event_system, EventTypes
        
        def on_storm_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'storm' and
                not data.get('is_ultimate', False)):
                # Ya está cubierto por el multiplicador, pero podemos añadir bonus extra
                print(f"🌪️ {self.name} usa habilidad de tormenta!")
        
        event_system.register(EventTypes.ABILITY_USED, on_storm_ability)

CharacterRegistry.register("red_thunder", RedThunder)