from game.characters.base_character import BaseCharacter
from game.characters.character_registry import CharacterRegistry
from game.systems.passive_system import PassiveFactory
from .ricchard_config import RICCHARD_ABILITIES, RICCHARD_STATS, RICCHARD_ENERGY_SOURCES, RICCHARD_ENERGY_MULTIPLIERS

class Ricchard(BaseCharacter):
    def __init__(self, position, team="player"):
        super().__init__(
            name="Ricchard",
            position=position,
            team=team,
            stats=RICCHARD_STATS.copy(),
            role="damage",
            abilities_config=RICCHARD_ABILITIES
        )
    
    def setup_energy_sources(self):
        """Ricchard genera más energía por habilidades del Vacío"""
        return RICCHARD_ENERGY_SOURCES.copy()
    
    def setup_energy_multipliers(self):
        """Ricchard bonus por daño del Vacío"""
        return RICCHARD_ENERGY_MULTIPLIERS.copy()
    
    def setup_energy_listeners(self):
        """Listeners de energía específicos para Ricchard"""
        super().setup_energy_listeners()
        
        # Listener especial para habilidades del Vacío
        from game.core.event_system import event_system, EventTypes
        
        def on_void_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'void' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_void_ability']['base']
                self.gain_energy(energy_gain, "void_ability")
        
        event_system.register(EventTypes.ABILITY_USED, on_void_ability)
    
    def setup_passives(self):
        """Solo configurar pasivas"""
        passive_name, event_type, callback = PassiveFactory.create_ph_regen_on_kill(
            self, 
            ph_amount=50, 
            passive_name="Instinto del Vacío"
        )
        self.add_passive(passive_name, event_type, callback)

CharacterRegistry.register("ricchard", Ricchard)