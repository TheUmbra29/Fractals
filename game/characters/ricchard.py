# game/characters/ricchard.py (VERSIÓN CORREGIDA)
from game.entities.battle_entity import BattleEntity
from game.characters.character_registry import CharacterRegistry

class Ricchard(BattleEntity):
    def __init__(self, position, team="player"):
        # ✅ CONSTRUCTOR SIMPLIFICADO - solo posición y equipo
        super().__init__(
            character_id="ricchard",  # Esto activa la carga automática
            position=position,
            team=team
        )
    
    def setup_energy_listeners(self):
        """Listeners específicos para Ricchard"""
        super().setup_energy_listeners()
        
        def on_void_ability(data):
            if (data.get('caster') == self and 
                data.get('damage_type') == 'void' and
                not data.get('is_ultimate', False)):
                energy_gain = self.energy_stats['energy_sources']['on_void_ability']['base']
                self.gain_energy(energy_gain, "void_ability")
        
        from game.core.event_system import event_system, EventTypes
        event_system.register(EventTypes.ABILITY_USED, on_void_ability)