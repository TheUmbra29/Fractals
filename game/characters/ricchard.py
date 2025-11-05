# game/characters/ricchard.py - VERSIÓN MIGRADA
from game.entities.battle_entity import BattleEntity  # 🆕 NUEVA BASE
from game.characters.character_registry import CharacterRegistry
from .ricchard_config import RICCHARD_ABILITIES, RICCHARD_STATS, RICCHARD_ENERGY_SOURCES, RICCHARD_ENERGY_MULTIPLIERS

class Ricchard(BattleEntity):  # 🆕 HEREDA DE BATTLEENTITY
    def __init__(self, position, team="player"):
        # 🎯 CONSTRUCTOR SIMPLIFICADO - BattleEntity maneja todo
        super().__init__(
            name="Ricchard",
            position=position,
            team=team,
            stats=RICCHARD_STATS.copy(),
            character_class="damage",
            abilities_config=RICCHARD_ABILITIES
        )
    
    def setup_energy_sources(self):
        """Override para Ricchard - más energía por habilidades del Vacío"""
        return RICCHARD_ENERGY_SOURCES.copy()
    
    def setup_energy_multipliers(self):
        """Override para Ricchard - bonus por daño del Vacío"""
        return RICCHARD_ENERGY_MULTIPLIERS.copy()
    
    def setup_energy_listeners(self):
        """Listeners específicos para Ricchard"""
        super().setup_energy_listeners()
        
        # Listener especial para habilidades del Vacío
        def on_void_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'void' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_void_ability']['base']
                self.gain_energy(energy_gain, "void_ability")
        
        from game.core.event_system import event_system, EventTypes
        event_system.register(EventTypes.ABILITY_USED, on_void_ability)

CharacterRegistry.register("ricchard", Ricchard)